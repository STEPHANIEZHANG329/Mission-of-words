from pathlib import Path

from mission_of_words.visual_qa import evaluate_visual


def _composition(page: int, page_type: str, required: list[str], drawn: list[str], **extra) -> dict:
    record = {
        "page": page,
        "type": page_type,
        "required_objects": required,
        "drawn_objects": drawn,
        "text_in_artwork": False,
        "asset_integration": "ok",
        "child_instruction": "Color the children carrying lanterns to church.",
    }
    record.update(extra)
    return record


def test_visual_qa_fails_without_human_review(tmp_path: Path):
    comps = [
        _composition(1, "coloring", ["church", "children"], ["church", "children", "lanterns"]),
        _composition(
            2,
            "search_find",
            ["search_background", "lantern"],
            ["search_background", "lantern", "pumpkin", "apple", "leaf", "acorn", "scarf", "basket", "Bible"],
        ),
        _composition(
            3,
            "maze",
            ["child_with_lantern", "welcome_table"],
            ["child_with_lantern", "welcome_table", "hedge_maze", "start_label", "finish_label"],
        ),
        _composition(
            4,
            "faith_interaction",
            ["lantern_frame", "drawing_lantern"],
            ["lantern_frame", "drawing_lantern", "choice_cards", "prayer_ribbon"],
            drawing_area_sqin=12,
            choice_count=4,
        ),
    ]
    pdf = tmp_path / "interior.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    previews = [tmp_path / f"p{i}.png" for i in range(4)]
    for path in previews:
        path.write_bytes(b"png")
    report = evaluate_visual(
        compositions=comps,
        preview_paths=previews,
        interior_pdf=pdf,
        human_findings=[],
    )
    assert report["pass"] is False
    assert any("visual review" in item.lower() for item in report["failures"])


def test_prompt_to_art_fails_when_required_object_missing(tmp_path: Path):
    comps = [
        _composition(1, "coloring", ["church", "string_lights"], ["church"]),
        _composition(
            2,
            "search_find",
            ["search_background"],
            ["search_background", "lantern", "pumpkin", "apple", "leaf", "acorn", "scarf", "basket", "Bible"],
        ),
        _composition(
            3,
            "maze",
            ["child_with_lantern"],
            ["child_with_lantern", "welcome_table", "hedge_maze", "start_label", "finish_label"],
        ),
        _composition(
            4,
            "faith_interaction",
            ["lantern_frame"],
            ["lantern_frame", "drawing_lantern", "choice_cards", "prayer_ribbon"],
            drawing_area_sqin=12,
            choice_count=4,
        ),
    ]
    pdf = tmp_path / "interior.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    previews = [tmp_path / f"p{i}.png" for i in range(4)]
    for path in previews:
        path.write_bytes(b"png")
    report = evaluate_visual(
        compositions=comps,
        preview_paths=previews,
        interior_pdf=pdf,
        human_findings=[{"page": i, "pass": True, "notes": "ok"} for i in range(1, 5)],
    )
    assert report["pass"] is False
    assert report["pages"][0]["prompt_to_art"]["pass"] is False
