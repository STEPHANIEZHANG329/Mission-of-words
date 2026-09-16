"""OpenAI image API client using the GPT2 secret. Counts every POST."""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from llk import PAID_CALL_CAP
from llk.paths import BUDGET, LEDGER, PROVENANCE, ensure_dirs

API_URL = "https://api.openai.com/v1/images/generations"


class CallCapExceeded(RuntimeError):
    pass


class ImageAPIError(RuntimeError):
    pass


def secret() -> str:
    key = os.environ.get("GPT2") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ImageAPIError("GPT2 secret is not present in the environment")
    return key


def load_budget() -> dict:
    return json.loads(BUDGET.read_text(encoding="utf-8"))


def calls_used() -> int:
    if not LEDGER.exists():
        return 0
    n = 0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        rec = json.loads(line)
        if rec.get("counted"):
            n += 1
    return n


def remaining_calls(cap: int = PAID_CALL_CAP) -> int:
    return cap - calls_used()


def _append_ledger(record: dict) -> None:
    ensure_dirs()
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def generate_png(
    *,
    asset_id: str,
    prompt: str,
    size: str,
    out_path: Path,
    model: str | None = None,
) -> dict:
    ensure_dirs()
    budget = load_budget()
    cap = int(budget.get("paid_call_cap", PAID_CALL_CAP))
    used = calls_used()
    if used >= cap:
        raise CallCapExceeded(f"paid call cap {cap} already reached ({used} calls)")

    models = [model or budget.get("model") or "gpt-image-2"]
    for fallback in budget.get("fallback_models") or []:
        if fallback not in models:
            models.append(fallback)

    last_error: Exception | None = None
    for candidate in models:
        try:
            payload = _post_image(prompt=prompt, size=size, model=candidate, asset_id=asset_id)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(payload["png_bytes"])
            provenance = {
                "asset_id": asset_id,
                "model": candidate,
                "size": size,
                "bytes": len(payload["png_bytes"]),
                "prompt_chars": len(prompt),
                "created_unix": int(time.time()),
            }
            (PROVENANCE / f"{asset_id}.json").write_text(
                json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
            )
            return provenance
        except ImageAPIError as exc:
            last_error = exc
            # Model not found / unsupported size: try fallback without extra panic.
            if "model" in str(exc).lower() or "size" in str(exc).lower():
                continue
            raise
    raise ImageAPIError(f"{asset_id} failed on all models: {last_error}")


def _post_image(*, prompt: str, size: str, model: str, asset_id: str) -> dict:
    body = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": "high",
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {secret()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    counted = False
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            counted = True
            raw = json.loads(resp.read().decode("utf-8"))
            status = resp.status
    except urllib.error.HTTPError as exc:
        counted = True
        err_body = exc.read().decode("utf-8", errors="replace")
        _append_ledger(
            {
                "asset_id": asset_id,
                "model": model,
                "size": size,
                "ok": False,
                "counted": True,
                "http": exc.code,
                "error": err_body[:2000],
                "unix": int(time.time()),
            }
        )
        raise ImageAPIError(f"HTTP {exc.code} for {asset_id} model={model}: {err_body[:500]}") from exc
    except Exception:
        # Network failure before a billed response: do not count.
        raise

    png = _extract_png(raw)
    _append_ledger(
        {
            "asset_id": asset_id,
            "model": model,
            "size": size,
            "ok": True,
            "counted": True,
            "http": status,
            "bytes": len(png),
            "unix": int(time.time()),
        }
    )
    return {"png_bytes": png, "raw_keys": list(raw.keys())}


def _extract_png(raw: dict) -> bytes:
    data = raw.get("data") or []
    if not data:
        raise ImageAPIError(f"image API returned no data: {str(raw)[:400]}")
    item = data[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    url = item.get("url")
    if not url:
        raise ImageAPIError(f"image API item missing b64 and url: {item.keys()}")
    with urllib.request.urlopen(url, timeout=180) as resp:
        return resp.read()
