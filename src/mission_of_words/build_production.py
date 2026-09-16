"""Phase C production builder. Writes a readiness report, never a fake KDP PDF."""

from __future__ import annotations

import json
from pathlib import Path

from mission_of_words.full_book_qa import evaluate_full_book
from mission_of_words.image_client import paid_call_count
from mission_of_words.paths import OUTPUT_DIR
from mission_of_words.production_qa import (
    PRODUCTION_PDF_NAME,
    evaluate_production_readiness,
    write_production_readiness,
)


def build_production() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    technical = evaluate_full_book(paid_image_calls=paid_call_count())
    report = evaluate_production_readiness(
        human_findings=[],
        visual_readiness=str(technical.get("visual_readiness") or "FAIL"),
        technical_pass=bool(technical.get("blueprint_pass")),
        paid_image_calls=paid_call_count(),
        production_pdf=OUTPUT_DIR / PRODUCTION_PDF_NAME,
    )
    write_production_readiness(report)
    fake = OUTPUT_DIR / PRODUCTION_PDF_NAME
    if fake.is_file() and not report["production_pass"]:
        fake.unlink()
        report = evaluate_production_readiness(
            human_findings=[],
            visual_readiness=str(technical.get("visual_readiness") or "FAIL"),
            technical_pass=bool(technical.get("blueprint_pass")),
            paid_image_calls=paid_call_count(),
            production_pdf=fake,
        )
        write_production_readiness(report)
    if report["production_pass"] is True:
        raise RuntimeError("production_pass cannot be true until accepted assets and human review exist")
    return report


if __name__ == "__main__":
    result = build_production()
    print(json.dumps({k: result[k] for k in result if k != "missing_accepted_assets"}, indent=2))
    print(f"missing_accepted_assets: {len(result['missing_accepted_assets'])}")
    if result["production_pass"] is True or result["pass"] is True:
        raise SystemExit(1)
    if result["paid_image_calls"] != 0:
        raise SystemExit(1)
    if not Path(OUTPUT_DIR / "production_readiness.json").is_file():
        raise SystemExit(1)
