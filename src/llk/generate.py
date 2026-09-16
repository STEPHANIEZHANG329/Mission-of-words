"""Paid image generation with immediate disk persist. Never exceeds the call cap."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

from llk.openai_images import CallCapExceeded, generate_png, remaining_calls
from llk.paths import ASSETS_ACCEPTED, ASSETS_GENERATED, ROOT, ensure_dirs
from llk.spec import AssetSpec, load_spec


def persist_jpeg(png_path: Path, asset_id: str) -> Path:
    img = Image.open(png_path)
    if asset_id != "cover_front":
        img = img.convert("L").convert("RGB")
    else:
        img = img.convert("RGB")
    dest = ASSETS_ACCEPTED / f"{asset_id}.jpg"
    img.save(dest, "JPEG", quality=92, optimize=True, dpi=(300, 300))
    return dest


def git_persist(paths: list[Path], message: str) -> None:
    if os.environ.get("PERSIST_TO_GIT") != "1":
        return
    subprocess.run(["git", "add", "--", *[str(p) for p in paths]], cwd=ROOT, check=False)
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if not staged.stdout.strip():
        return
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=False)
    subprocess.run(["git", "pull", "--rebase", "origin", "HEAD"], cwd=ROOT, check=False)
    subprocess.run(["git", "push"], cwd=ROOT, check=False)


def generate_asset(asset: AssetSpec, *, force: bool = False) -> Path | None:
    ensure_dirs()
    png_path = ASSETS_GENERATED / f"{asset.asset_id}.png"
    jpg_path = ASSETS_ACCEPTED / f"{asset.asset_id}.jpg"
    if png_path.exists() and png_path.stat().st_size > 1000 and not force:
        print(f"SKIP {asset.asset_id} (png exists)", flush=True)
        if not jpg_path.exists():
            persist_jpeg(png_path, asset.asset_id)
        return png_path
    if jpg_path.exists() and jpg_path.stat().st_size > 1000 and not force:
        print(f"SKIP {asset.asset_id} (jpg exists)", flush=True)
        return jpg_path
    print(f"GENERATE {asset.asset_id} size={asset.size} remaining={remaining_calls()}", flush=True)
    generate_png(
        asset_id=asset.asset_id,
        prompt=asset.prompt,
        size=asset.size,
        out_path=png_path,
    )
    persist_jpeg(png_path, asset.asset_id)
    git_persist(
        [png_path, jpg_path, ROOT / "ops" / "ledger.jsonl", ROOT / "assets" / "provenance" / f"{asset.asset_id}.json"],
        f"persist generated art {asset.asset_id}",
    )
    print(f"PERSISTED {asset.asset_id}", flush=True)
    return png_path


def assets_for_group(group: str | None) -> list[AssetSpec]:
    spec = load_spec()
    if not group or group == "all":
        return list(spec.assets)
    return [a for a in spec.assets if a.group == group]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", default="all")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    assets = assets_for_group(args.group)
    if args.dry_run:
        print(json.dumps({"group": args.group, "count": len(assets), "ids": [a.asset_id for a in assets]}, indent=2))
        return 0
    for asset in assets:
        try:
            generate_asset(asset, force=args.force)
        except CallCapExceeded as exc:
            print(f"CAP {exc}", flush=True)
            return 2
        time.sleep(0.4)
    return 0


if __name__ == "__main__":
    sys.exit(main())
