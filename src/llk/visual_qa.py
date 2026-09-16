"""Render all 48 interior pages and run deterministic visual checks. No paid calls."""

from __future__ import annotations

import json
from pathlib import Path

from llk.contact_sheet import render_pages
from llk.images import open_lineart
from llk.maze import generate_maze
from llk.maze_render import assert_physical_openings
from llk.paths import OUTPUT
from llk.search_place import place_targets
from llk.spec import load_spec


def export_page_pngs(pdf_path: Path, dest_dir: Path) -> list[Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    pages = render_pages(pdf_path)
    if len(pages) != 48:
        raise AssertionError(f"expected 48 rendered pages, got {len(pages)}")
    paths = []
    for i, img in enumerate(pages, start=1):
        path = dest_dir / f"page_{i:02d}.png"
        img.save(path, "PNG")
        paths.append(path)
    return paths


def run_visual_checks(pdf_path: Path | None = None) -> dict:
    spec = load_spec()
    pdf_path = pdf_path or (OUTPUT / "LittleLampkeepers_48Page_Interior_KDP.pdf")
    dest = OUTPUT / "page_pngs"
    paths = export_page_pngs(pdf_path, dest)
    maze_reports = []
    for mission in spec.missions:
        maze_page = mission.pages[2]
        maze = generate_maze(maze_page.maze_grid[0], maze_page.maze_grid[1], maze_page.maze_seed)
        maze_reports.append({"mission": mission.id, **assert_physical_openings(maze)})
        bg = open_lineart(f"search_bg_{mission.id}")
        placed = place_targets(bg, mission.pages[1].targets)
        if len(placed) != 8:
            raise AssertionError(f"{mission.id} placed {len(placed)} targets")
    report = {
        "pages_rendered": len(paths),
        "maze_openings": maze_reports,
        "paid_calls_this_repair": 0,
        "pass": True,
    }
    (OUTPUT / "visual_qa.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run_visual_checks(), indent=2))
