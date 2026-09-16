"""Phase C full-book evaluation helper. Zero paid image calls.

Use `python -m mission_of_words.build_book` for the marked 48-page technical proof.
Use `python -m mission_of_words.build_production` for the fail-closed production-readiness report.
This module still writes blueprint evidence without claiming production_pass.
"""

from __future__ import annotations

import json
import shutil

from mission_of_words.book_manifest import BOOK_MANIFEST, write_manifest
from mission_of_words.full_book_qa import evaluate_full_book, export_page_map, write_full_book_report
from mission_of_words.image_client import paid_call_count
from mission_of_words.paths import OUTPUT_DIR


def evaluate() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest()
    report = evaluate_full_book(paid_image_calls=paid_call_count())
    write_full_book_report(report)
    export_page_map()
    shutil.copyfile(BOOK_MANIFEST, OUTPUT_DIR / "book_manifest.json")
    return report


def main() -> int:
    report = evaluate()
    print(json.dumps({k: report[k] for k in report if k != "pages"}, indent=2))
    if report["paid_image_calls"] != 0:
        return 1
    if report["production_pass"] is True or report["pass"] is True:
        return 1
    if report["blueprint_pass"] is not True:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
