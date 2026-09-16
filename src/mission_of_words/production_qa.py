"""Fail-closed production readiness. Never confuses a technical proof with a KDP interior."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mission_of_words.art_bible import REQUIRED_QA_DIMENSIONS, art_bible_errors
from mission_of_words.ingest import ingest_failures, missing_accepted_assets, overlay_manifest_with_store
from mission_of_words.paths import OUTPUT_DIR
from mission_of_words.production_assets import load_production_manifest, production_manifest_errors, role_counts
from mission_of_words.search_difficulty import evaluate_search_difficulty
from mission_of_words.book_manifest import load_mission_records

PRODUCTION_PDF_NAME = "BrightHearts_Fall_Interior.pdf"


def _human_review_pass(human_findings: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    by_page = {int(item["page"]): item for item in human_findings}
    if len(by_page) != 48:
        failures.append(f"human visual review covers {len(by_page)} pages, not 48")
    for page in range(1, 49):
        finding = by_page.get(page)
        if not finding:
            failures.append(f"page {page}: human visual review MISSING")
            continue
        if not finding.get("pass"):
            failures.append(f"page {page}: human visual review FAIL — {finding.get('notes')}")
        for dimension in REQUIRED_QA_DIMENSIONS:
            value = finding.get(dimension)
            if isinstance(value, dict):
                ok = bool(value.get("pass"))
            elif isinstance(value, bool):
                ok = value
            elif isinstance(value, str):
                ok = value.upper() == "PASS"
            else:
                ok = False
            if not ok:
                failures.append(f"page {page}: {dimension} is not PASS")
        if finding.get("anatomy_artifact") or finding.get("artifact"):
            failures.append(f"page {page}: anatomy/artifact flag is set")
        if finding.get("text_in_artwork") is True:
            failures.append(f"page {page}: text-in-artwork flag is set")
    return not failures, failures


def evaluate_production_readiness(
    *,
    human_findings: list[dict[str, Any]] | None = None,
    visual_readiness: str = "FAIL",
    technical_pass: bool = False,
    paid_image_calls: int = 0,
    production_pdf: Path | None = None,
) -> dict[str, Any]:
    failures: list[str] = []
    failures.extend(art_bible_errors())
    failures.extend(production_manifest_errors())
    manifest = overlay_manifest_with_store()
    missing = missing_accepted_assets(manifest=manifest)
    failures.extend(ingest_failures(manifest=manifest))
    for mission in load_mission_records():
        search = mission["pages"][1]
        names = [target["name"] for target in search["targets"]]
        failures.extend(
            evaluate_search_difficulty(
                search["targets"],
                excluded_background_objects=names,
                owner=f"{mission['id']} search_find",
            )
        )
    human_ok, human_failures = _human_review_pass(human_findings or [])
    failures.extend(human_failures)
    if (visual_readiness or "FAIL").upper() != "PASS":
        failures.append(f"visual_readiness is {visual_readiness}, not PASS")
    if not technical_pass:
        failures.append("production interior requires the deterministic technical gates to stay green")
    if paid_image_calls != 0 and not missing:
        # Spend is allowed only after an owner gate exists. This pass still
        # reports any unexpected CI spend as a failure.
        pass
    if paid_image_calls != 0:
        failures.append("ordinary evaluation still expects paid_image_calls == 0 until the owner gate exists")

    accepted = [asset for asset in manifest["assets"] if asset.get("status") == "accepted"]
    required = [asset for asset in manifest["assets"] if asset.get("needs_ai_art")]
    production_pass = (
        not failures
        and not missing
        and human_ok
        and (visual_readiness or "").upper() == "PASS"
        and len(accepted) == len(required)
        and len(required) > 0
    )
    if production_pass and missing:
        production_pass = False
        failures.append("production_pass cannot be true while required assets are missing")

    pdf_path = production_pdf or (OUTPUT_DIR / PRODUCTION_PDF_NAME)
    if pdf_path.is_file() and not production_pass:
        failures.append(
            f"publishable PDF {pdf_path.name} exists while production gates fail; delete it"
        )
        production_pass = False

    blockers = []
    if missing:
        blockers.append(
            f"{len(missing)} required production assets are not accepted "
            f"(first: {missing[0]})"
        )
    if not human_ok:
        blockers.append("human visual review is not PASS on all 48 pages")
    if (visual_readiness or "FAIL").upper() != "PASS":
        blockers.append("expanded visual QA is not PASS")
    blockers.append("Do not merge, publish, or upload to KDP until every production gate passes")
    blockers.append("Cover remains deferred until interior lock")

    return {
        "kind": "production_readiness",
        "book_id": manifest.get("book_id"),
        "phase": "C",
        "required_ai_asset_count": len(required),
        "accepted_ai_asset_count": len(accepted),
        "missing_accepted_assets": missing,
        "role_counts": role_counts(manifest),
        "human_visual_review_pass": human_ok,
        "visual_readiness": visual_readiness,
        "paid_image_calls": paid_image_calls,
        "publishable_pdf_present": bool(pdf_path.is_file()),
        "production_pass": production_pass,
        "pass": production_pass,
        "failures": failures,
        "blockers": blockers,
    }


def write_production_readiness(
    report: dict[str, Any],
    json_path: Path | None = None,
    markdown_path: Path | None = None,
) -> tuple[Path, Path]:
    json_dest = json_path or (OUTPUT_DIR / "production_readiness.json")
    md_dest = markdown_path or (OUTPUT_DIR / "production_readiness.md")
    json_dest.parent.mkdir(parents=True, exist_ok=True)
    json_dest.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Production readiness — Bright Hearts Phase C",
        "",
        "This is **not** a publishable KDP interior. A production PDF is written only when",
        "`production_pass` is true.",
        "",
        f"**production_pass:** {report['production_pass']}",
        f"**Required AI assets:** {report['required_ai_asset_count']}",
        f"**Accepted AI assets:** {report['accepted_ai_asset_count']}",
        f"**Human visual review:** {'PASS' if report['human_visual_review_pass'] else 'FAIL/MISSING'}",
        f"**Visual readiness:** {report['visual_readiness']}",
        f"**Paid image calls:** {report['paid_image_calls']}",
        "",
        "## Role counts",
        "",
    ]
    for role, count in (report.get("role_counts") or {}).items():
        lines.append(f"- `{role}`: {count}")
    lines.extend(["", "## Blockers", ""])
    for item in report.get("blockers") or []:
        lines.append(f"- {item}")
    if report.get("failures"):
        lines.extend(["", "## Failures", ""])
        for item in report["failures"][:80]:
            lines.append(f"- {item}")
        extra = len(report["failures"]) - 80
        if extra > 0:
            lines.append(f"- … {extra} more")
    lines.append("")
    md_dest.write_text("\n".join(lines), encoding="utf-8")
    return json_dest, md_dest
