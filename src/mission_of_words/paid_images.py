"""Owner-gated GPT2 / OpenAI Images client.

The API key is read only from the GPT2 environment variable (GitHub Actions
secret). It is never printed, logged, or written to disk. Ordinary PR CI does
not import a live call: generate() refuses unless the confirm phrase, env
gate, remaining cap, and secret are all present.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mission_of_words.paths import OPS_DIR, ROOT

ENDPOINT = "https://api.openai.com/v1/images/generations"
INTERIOR_MODEL = "gpt-image-2.5-flare"
REPAIR_MODEL = "gpt-image-2.5-sunburst"
QUALITY = "high"
PRIMARY_SIZE = "1664x2160"
FALLBACK_SIZE = "1664x2160"
CONFIRM_PHRASE = "OWNER_PHASE_C_GPT2_REBUILD"
GATE_PATH = OPS_DIR / "phase_c_paid_gate.json"
MAX_PAID_CALLS = 24
ESTIMATED_USD_PER_CALL = 0.20


class PaidImageError(RuntimeError):
    """Raised instead of performing or completing a paid image call."""


def _gate() -> dict[str, Any]:
    if not GATE_PATH.is_file():
        raise PaidImageError("missing ops/phase_c_paid_gate.json")
    return json.loads(GATE_PATH.read_text(encoding="utf-8"))


def max_paid_calls() -> int:
    gate = _gate()
    return int(gate.get("max_paid_calls") or MAX_PAID_CALLS)


def secret_present() -> bool:
    return bool(os.environ.get("GPT2"))


def _secret() -> str:
    value = os.environ.get("GPT2") or ""
    if not value:
        raise PaidImageError("GPT2 secret is not present in the environment")
    return value


def generation_authorized(*, confirm: str | None = None) -> tuple[bool, str]:
    if os.environ.get("ALLOW_PAID_IMAGE_CALLS") != "1":
        return False, "ALLOW_PAID_IMAGE_CALLS is not 1"
    phrase = confirm if confirm is not None else os.environ.get("BRIGHT_HEARTS_CONFIRM_PAID_GENERATION", "")
    if phrase != CONFIRM_PHRASE:
        return False, "confirm phrase is missing or does not match"
    if not secret_present():
        return False, "GPT2 secret is not present"
    gate = _gate()
    if not gate.get("paid_calls_enabled") or not gate.get("allow_paid_image_calls"):
        return False, "phase C paid gate is closed"
    if int(gate.get("max_paid_calls") or 0) > MAX_PAID_CALLS:
        return False, "gate max_paid_calls exceeds Owner cap of 24"
    return True, "authorized"


def _redact(text: str) -> str:
    secret = os.environ.get("GPT2") or ""
    if secret:
        text = text.replace(secret, "[REDACTED]")
    text = text.replace("Bearer ", "Bearer [REDACTED]")
    return text


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def _post(payload: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {_secret()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            parsed = json.loads(raw.decode("utf-8"))
            parsed["_http_status"] = getattr(response, "status", 200)
            return parsed
    except urllib.error.HTTPError as exc:
        detail = _redact(exc.read().decode("utf-8", errors="replace")[:800])
        raise PaidImageError(f"OpenAI HTTP {exc.code}: {detail}") from None
    except urllib.error.URLError as exc:
        raise PaidImageError(f"OpenAI network error: {_redact(str(exc.reason))}") from None


def generate_png(
    *,
    prompt: str,
    dest: Path,
    asset_id: str,
    role: str,
    model: str = INTERIOR_MODEL,
    quality: str = QUALITY,
    size: str | None = None,
    remaining_calls: int,
    estimated_usd: float = ESTIMATED_USD_PER_CALL,
) -> dict[str, Any]:
    """One visible paid call. No hidden retries. Caller records the ledger row."""
    ok, reason = generation_authorized()
    if not ok:
        raise PaidImageError(f"paid generation refused: {reason}")
    if remaining_calls <= 0:
        raise PaidImageError("paid-call cap reached; no network request was sent")
    dest.parent.mkdir(parents=True, exist_ok=True)
    requested_size = size or PRIMARY_SIZE
    payload = {
        "model": model,
        "prompt": prompt,
        "size": requested_size,
        "quality": quality,
    }
    used_size = requested_size
    result = _post(payload)
    data = (result.get("data") or [{}])[0]
    b64 = data.get("b64_json")
    if not b64:
        raise PaidImageError("OpenAI response did not include b64_json")
    import base64

    png = base64.b64decode(b64)
    dest.write_bytes(png)
    try:
        rel = str(dest.relative_to(ROOT))
    except ValueError:
        rel = str(dest)
    return {
        "asset_id": asset_id,
        "role": role,
        "model": model,
        "quality": quality,
        "size": used_size,
        "path": rel,
        "sha256": sha256_bytes(png),
        "prompt_hash": prompt_hash(prompt),
        "request_id": str(result.get("id") or data.get("revised_prompt") or "")[:80],
        "openai_created": result.get("created"),
        "paid_call": True,
        "estimated_usd": estimated_usd,
        "status": "generated",
        "accepted": False,
        "ts": datetime.now(timezone.utc).isoformat(),
        "bytes": len(png),
    }
