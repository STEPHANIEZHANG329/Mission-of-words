from mission_of_words.composition import (
    MISSION_IDS,
    faith_rhythm,
    hero_art_ratio_bounds,
    maze_embed,
    maze_path_box,
    search_legend_height,
    validate_bibles,
)
from mission_of_words.layout import content_box
from mission_of_words.paths import ROOT
from mission_of_words.templates import measure_activity_header


def test_bibles_lock_cast_style_and_unique_mission_composition():
    defects = validate_bibles()
    assert defects == [], defects
    embeds = {maze_embed(mission_id) for mission_id in MISSION_IDS}
    rhythms = {faith_rhythm(mission_id) for mission_id in MISSION_IDS}
    assert len(embeds) == 8
    assert len(rhythms) >= 6


def test_hero_art_owns_seventy_to_eighty_percent_of_live_area():
    lo, hi = hero_art_ratio_bounds()
    assert (lo, hi) == (0.7, 0.8)
    for page, title in (
        (5, "Shine Your Light"),
        (25, "Kindness at the Fall Festival"),
    ):
        plan = measure_activity_header(
            page,
            mission_number=6 if page == 25 else 1,
            mission_title=title,
            activity_title=title,
            reference="Ephesians 4:32" if page == 25 else "Matthew 5:16",
            activity_label="Color this picture",
            instruction="Color the children carrying lanterns to the church fall festival.",
            hero=True,
        )
        assert plan.state.ok(), plan.state.as_fields()
        ratio = plan.art_height_ratio()
        assert lo <= ratio <= hi, (page, title, ratio)


def test_search_legend_is_compact_and_secondary():
    assert search_legend_height() <= 48
    plan = measure_activity_header(
        6,
        mission_number=1,
        mission_title="Shine Your Light",
        activity_title="Find the Festival Gifts",
        reference="Matthew 5:16",
        activity_label="Search & Find",
        instruction="Find and circle all 8 gifts.",
    )
    live = content_box(6)
    live_h = live[3] - live[1]
    art_h = plan.art_box[3] - plan.art_box[1]
    scene_h = art_h - search_legend_height()
    assert scene_h / live_h >= 0.62


def test_maze_path_is_the_environment_not_a_pasted_window():
    live = content_box(7)
    art = (live[0], live[1] + 80, live[2], live[3] - 70)
    path = maze_path_box(art)
    art_h = art[3] - art[1]
    path_h = path[3] - path[1]
    assert path_h / art_h >= 0.72
    maze_src = (ROOT / "src" / "mission_of_words" / "page_maze.py").read_text(encoding="utf-8")
    assert "draw_panel" not in maze_src
    assert "maze_embed" in maze_src


def test_internal_geometry_is_not_an_owner_facing_product():
    from mission_of_words.internal_geometry import PDF
    from mission_of_words.paths import ROOT
    import json

    assert "INTERNAL_ENGINEERING" in str(PDF)
    assert "GeometryOnly" in PDF.name
    gate = json.loads((ROOT / "ops" / "layout_gate.json").read_text(encoding="utf-8"))
    assert gate["approved_for_paid_generation"] is False
    assert gate["status"] != "PASS"
    paid = json.loads((ROOT / "ops" / "phase_c_paid_gate.json").read_text(encoding="utf-8"))
    assert paid["owner_stop"] is True
    assert paid["remaining_calls"] == 0
    assert paid["spent_calls"] == 18
    art_bible = (ROOT / "content" / "art_bible.json").read_text(encoding="utf-8")
    assert "NO titles" in art_bible or "no_text" in art_bible
    assert "letters" in art_bible.lower()
    composition = (ROOT / "content" / "composition_bible.json").read_text(encoding="utf-8")
    assert "Little Lampkeepers: Shine Your Light This Fall" in composition
    assert "Bright Hearts" in composition
    assert '"owner_facing_product": false' in composition
    coloring = (ROOT / "src" / "mission_of_words" / "page_coloring.py").read_text(encoding="utf-8")
    assert "draw_panel" not in coloring
