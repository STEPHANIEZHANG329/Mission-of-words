"""Technical QA for the finished interior and cover PDFs."""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader

from llk.geometry import TRIM_H, TRIM_W
from llk.maze import generate_maze
from llk.paths import OUTPUT
from llk.search import validate_mission_search
from llk.spec import PAGE_COUNT, load_spec


def assert_pdf(path: Path, *, pages: int, width_in: float, height_in: float, fonts_required: bool = True) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    reader = PdfReader(str(path))
    if len(reader.pages) != pages:
        raise AssertionError(f"{path.name} has {len(reader.pages)} pages, expected {pages}")
    page0 = reader.pages[0]
    w = float(page0.mediabox.width) / 72.0
    h = float(page0.mediabox.height) / 72.0
    if abs(w - width_in) > 0.02 or abs(h - height_in) > 0.02:
        raise AssertionError(f"{path.name} page size {w:.3f}x{h:.3f} in, expected {width_in}x{height_in}")
    fonts = set()
    if fonts_required:
        for page in reader.pages:
            resources = page.get("/Resources") or {}
            font_dict = resources.get("/Font") if resources else None
            if font_dict:
                for name in font_dict.keys():
                    fonts.add(str(name))
        if not fonts:
            raise AssertionError(f"{path.name} has no embedded/resource fonts")
        embedded = False
        # pypdf font objects typically include /FontFile2 for TTF.
        for page in reader.pages:
            resources = page.get("/Resources") or {}
            font_dict = resources.get("/Font") if resources else None
            if not font_dict:
                continue
            for font in font_dict.values():
                font_obj = font.get_object()
                descendant = font_obj.get("/DescendantFonts")
                candidates = [font_obj]
                if descendant:
                    candidates.append(descendant[0].get_object())
                for cand in candidates:
                    descriptor = cand.get("/FontDescriptor")
                    if not descriptor:
                        continue
                    descriptor = descriptor.get_object()
                    if descriptor.get("/FontFile2") or descriptor.get("/FontFile3") or descriptor.get("/FontFile"):
                        embedded = True
        if not embedded:
            raise AssertionError(f"{path.name} fonts are not embedded")
    return {"pages": pages, "width_in": w, "height_in": h, "font_resources": sorted(fonts)}


def run_qa() -> dict:
    spec = load_spec()
    for mission in spec.missions:
        validate_mission_search(mission)
        maze_page = mission.pages[2]
        maze = generate_maze(maze_page.maze_grid[0], maze_page.maze_grid[1], maze_page.maze_seed)
        if maze.path[0] != maze.start or maze.path[-1] != maze.end:
            raise AssertionError(f"{mission.id} maze path does not connect start to end")
    interior = OUTPUT / "LittleLampkeepers_48Page_Interior_KDP.pdf"
    cover = OUTPUT / "LittleLampkeepers_Cover_KDP.pdf"
    sheet = OUTPUT / "contact_sheet_all_pages.jpg"
    interior_info = assert_pdf(interior, pages=PAGE_COUNT, width_in=TRIM_W, height_in=TRIM_H)
    from llk.geometry import cover_size_inches

    cw, ch = cover_size_inches(48)
    cover_info = assert_pdf(cover, pages=1, width_in=cw, height_in=ch)
    if not sheet.exists():
        raise FileNotFoundError(sheet)
    report = {
        "interior": interior_info,
        "cover": cover_info,
        "contact_sheet_bytes": sheet.stat().st_size,
        "page_count": PAGE_COUNT,
        "missions": len(spec.missions),
        "assets_planned": len(spec.assets),
        "pass": True,
    }
    (OUTPUT / "qa_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run_qa(), indent=2))
