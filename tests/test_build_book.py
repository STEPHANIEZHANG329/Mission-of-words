from pathlib import Path
from tempfile import TemporaryDirectory

from mission_of_words.brand import FORBIDDEN_CONSUMER_MARK, TITLE
from mission_of_words.book_manifest import load_mission_records
from mission_of_words.build_book import ANSWER_PDF, INTERIOR_PDF, build
from mission_of_words.full_book_qa import _pdf_text, evaluate_full_book
from mission_of_words.image_client import paid_call_count
from mission_of_words.maze import generate_maze
from mission_of_words.page_search import build_search_scene_from_page
from mission_of_words.paths import OUTPUT_DIR
from mission_of_words.procedural import TARGET_DRAWERS
from mission_of_words.proof import NON_PRODUCTION_MARK


def test_every_search_target_has_a_unique_procedural_drawer():
    missions = load_mission_records()
    seen = []
    for mission in missions:
        names = [target["name"] for target in mission["pages"][1]["targets"]]
        assert len(names) == 8
        for name in names:
            assert name in TARGET_DRAWERS, name
            seen.append(name)
    assert len(seen) == 64
    assert len(set(seen)) == 64


def test_all_search_find_scenes_compose_without_pixel_overlap(tmp_path: Path):
    for mission in load_mission_records():
        dest = tmp_path / mission["id"]
        composed, manifest, _records = build_search_scene_from_page(
            mission["pages"][1],
            dest,
            page_number=int(mission["global_page_start"]) + 1,
            theme=mission["id"],
            marked_proof=True,
        )
        assert composed.is_file()
        names = [row["name"] for row in manifest]
        expected = [target["name"] for target in mission["pages"][1]["targets"]]
        assert names == expected


def test_all_eight_mazes_are_unique_solvable_and_perfect():
    fingerprints = []
    for mission in load_mission_records():
        page = mission["pages"][2]
        rows, cols = page["grid"]
        maze = generate_maze(rows=rows, cols=cols, seed=int(page["seed"]))
        path = maze.solve()
        assert path[0] == maze.start
        assert path[-1] == maze.finish
        assert maze.is_perfect()
        edges = tuple(sorted({tuple(sorted((cell, nxt))) for cell, nbrs in maze.passages.items() for nxt in nbrs}))
        fingerprints.append(edges)
    assert len(set(fingerprints)) == 8


def test_blueprint_cannot_claim_technical_pass_without_the_48_page_proof():
    report = evaluate_full_book()
    assert report["interior_pdf_present"] is False
    assert report["technical_pass"] is False
    assert report["production_pass"] is False
    assert report["pass"] is False


def test_build_book_phase_b_technical_proof_is_not_publishable():
    report = build()
    assert report["page_count"] == 48
    assert report["rendered_page_count"] == 48
    assert report["paid_image_calls"] == 0
    assert paid_call_count() == 0
    assert report["technical_pass"] is True, report["failures"]
    assert report["production_pass"] is False
    assert report["pass"] is False
    assert report["placeholder_assets_present"] is True
    assert report["visual_readiness"] in {"FAIL", "MISSING"}
    assert report["non_production_mark_present"] is True
    assert report["maze_all_solvable"] is True
    assert report["maze_all_unique"] is True
    assert report["search_answer_keys_from_manifest"] is True
    assert report["raster_dpi_ok"] is True
    assert report["facing_page_parity_ok"] is True
    assert report["font_floors_ok"] is True
    assert INTERIOR_PDF.is_file()
    interior_text = _pdf_text(INTERIOR_PDF)
    assert TITLE in interior_text
    assert FORBIDDEN_CONSUMER_MARK not in interior_text
    assert ANSWER_PDF.is_file()
    assert (OUTPUT_DIR / "qa_report.json").is_file()
    assert (OUTPUT_DIR / "visual_qa.md").is_file()
    visual = (OUTPUT_DIR / "visual_qa.md").read_text(encoding="utf-8")
    assert "FAIL" in visual
    assert "Asset Integration" in visual
    assert NON_PRODUCTION_MARK in visual or "placeholder" in visual.lower()
    for index in (1, 5, 36, 37, 48):
        assert (OUTPUT_DIR / "previews" / f"page_{index:02d}.png").is_file()
    assert (OUTPUT_DIR / "previews" / "contact_sheet.png").is_file()
    assert (OUTPUT_DIR / "previews" / "page_48.png").is_file()
    assert not (OUTPUT_DIR / "previews" / "page_49.png").is_file()
