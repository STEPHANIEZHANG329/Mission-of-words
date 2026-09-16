"""End-to-end produce step after artwork exists: interior, cover, contact sheet, QA."""

from __future__ import annotations

import json
import sys

from llk.compose import Composer
from llk.contact_sheet import build_contact_sheet
from llk.cover import CoverComposer
from llk.paths import OUTPUT
from llk.qa import run_qa
from llk.spec import load_spec


def missing_assets() -> list[str]:
    from llk.images import find_art

    missing = []
    for asset in load_spec().assets:
        try:
            find_art(asset.asset_id)
        except FileNotFoundError:
            missing.append(asset.asset_id)
    return missing


def main() -> int:
    missing = missing_assets()
    if missing:
        print("MISSING_ART " + ", ".join(missing))
        return 2
    interior = Composer().write_interior()
    cover = CoverComposer().write()
    sheet = build_contact_sheet(interior, OUTPUT / "contact_sheet_all_pages.jpg")
    report = run_qa()
    print(json.dumps({"interior": str(interior), "cover": str(cover), "sheet": str(sheet), "qa": report}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
