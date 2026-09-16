"""Compile/test gates that must pass before the first paid image call."""

from __future__ import annotations

import json
import sys

from llk import PAID_CALL_CAP
from llk.geometry import INNER_SAFETY, MIN_ANSWER_PT, MIN_INSTRUCTION_PT, MIN_PUZZLE_PT, OUTER_SAFETY, margins_for_page
from llk.maze import generate_maze
from llk.openai_images import calls_used
from llk.search import validate_mission_search
from llk.spec import PAGE_COUNT, load_spec
from llk.style import LINE_ART_BIBLE


def run_preflight() -> dict:
    spec = load_spec()
    errors: list[str] = []
    if len(spec.pages) != PAGE_COUNT:
        errors.append(f"page count {len(spec.pages)}")
    if len(spec.missions) != 8:
        errors.append("expected 8 missions")
    if len(spec.canon) != 8:
        errors.append("expected 8 canon records")
    if len(spec.assets) > PAID_CALL_CAP:
        errors.append(f"asset count {len(spec.assets)} exceeds cap {PAID_CALL_CAP}")
    numbers = [p["page"] for p in spec.pages]
    if numbers != list(range(1, PAGE_COUNT + 1)):
        errors.append("pages are not 1..48 in order")
    kinds = [p["type"] for p in spec.pages]
    if kinds.count("coloring") != 8 or kinds.count("search_find") != 8 or kinds.count("maze") != 8:
        errors.append("mission activity mix is incomplete")
    if kinds.count("answer_key") != 8:
        errors.append("expected 8 answer-key pages")
    for mission in spec.missions:
        try:
            validate_mission_search(mission)
        except ValueError as exc:
            errors.append(str(exc))
        maze_page = mission.pages[2]
        maze = generate_maze(maze_page.maze_grid[0], maze_page.maze_grid[1], maze_page.maze_seed)
        if len(maze.path) < 8:
            errors.append(f"{mission.id} maze path too short")
        canon = spec.canon[mission.canon_id]
        if canon.license != "public_domain":
            errors.append(f"{canon.canon_id} is not public_domain")
        if not canon.source_text or not canon.child_paraphrase:
            errors.append(f"{canon.canon_id} missing source/paraphrase")
        if canon.source_text in canon.child_paraphrase:
            errors.append(f"{canon.canon_id} paraphrase copies source")
    odd = margins_for_page(1)
    even = margins_for_page(2)
    if odd.left != INNER_SAFETY or even.right != INNER_SAFETY:
        errors.append("gutter parity is wrong")
    if odd.right != OUTER_SAFETY or even.left != OUTER_SAFETY:
        errors.append("outer margin is wrong")
    if MIN_INSTRUCTION_PT < 12 or MIN_PUZZLE_PT < 12 or MIN_ANSWER_PT < 9:
        errors.append("type floor too small")
    for asset in spec.assets:
        low = asset.prompt.lower()
        if "no text" not in low:
            errors.append(f"{asset.asset_id} prompt missing no-text rule")
        if asset.asset_id != "cover_front" and "coloring-book" not in low and "coloring book" not in low:
            errors.append(f"{asset.asset_id} prompt missing line-art bible")
        if any(word in low for word in ("stick figure", "wireframe", "placeholder", "technical proof")):
            errors.append(f"{asset.asset_id} prompt uses rejected language")
    if LINE_ART_BIBLE not in spec.assets[0].prompt:
        errors.append("title prompt missing line-art bible")
    used = calls_used()
    if used != 0:
        # Preflight may run after generation; only the dedicated before-paid job should assert 0.
        pass
    if errors:
        raise SystemExit("PREFLIGHT_FAIL\n" + "\n".join(errors))
    report = {
        "ok": True,
        "pages": len(spec.pages),
        "missions": len(spec.missions),
        "canon": len(spec.canon),
        "planned_paid_assets": len(spec.assets),
        "paid_call_cap": PAID_CALL_CAP,
        "paid_calls_so_far": used,
        "groups": sorted({a.group for a in spec.assets}),
    }
    return report


if __name__ == "__main__":
    strict = "--before-paid" in sys.argv
    report = run_preflight()
    if strict and report["paid_calls_so_far"] != 0:
        raise SystemExit("PREFLIGHT_FAIL paid calls already used before authorization")
    print(json.dumps(report, indent=2))
