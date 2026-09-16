from io import BytesIO

from reportlab.pdfgen import canvas

from mission_of_words.bibles import uniqueness_report, validate_bibles
from mission_of_words.geometry import measuring_canvas, wrap_lines
from mission_of_words.layout import PAGE_H, PAGE_W, content_box
from mission_of_words.page_factory import draw_activity_header, measure_activity_header
from mission_of_words.typefaces import BODY, DISPLAY, FORBIDDEN_PRIMARY, primary_faces, register


def test_long_mission_title_wraps_instead_of_overflowing():
    register()
    title = "Kindness at the Fall Festival"
    c = measuring_canvas()
    left, _bottom, right, _top = content_box(25)
    width = right - left
    lines, overflow = wrap_lines(c, title, DISPLAY, 20, width)
    assert overflow == []
    assert lines
    for line in lines:
        assert c.stringWidth(line, DISPLAY, 20) <= width + 0.01


def test_badge_and_title_do_not_collide_on_search_heading():
    plan = measure_activity_header(
        25,
        mission_number=6,
        mission_title="Kindness at the Fall Festival",
        activity_title="Find the Kindness Gifts",
        reference="Ephesians 4:32",
        activity_label="Search & Find",
        instruction="Find and circle all 8 kindness gifts. Each one can help you be kind at the festival.",
    )
    assert plan.state.ok(), plan.state.as_fields()
    names = [box.name for box in plan.state.bboxes]
    assert any(name.startswith("mission_badge") for name in names)
    assert any(name.startswith("mission_title") for name in names)
    assert any(name.startswith("instruction") for name in names)


def test_hero_header_uses_larger_instruction_type():
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    plan = draw_activity_header(
        c,
        5,
        mission_number=1,
        mission_title="Shine Your Light",
        activity_title="Shine Your Light",
        reference="Matthew 5:16",
        activity_label="Color this picture",
        instruction="Color the children carrying lanterns to the church fall festival.",
        hero=True,
    )
    assert plan.state.ok(), plan.state.as_fields()
    art_h = plan.art_box[3] - plan.art_box[1]
    assert art_h > 480
    assert 0.70 <= plan.art_fraction <= 0.80


def test_odd_even_headers_stay_inside_safety():
    for page in (5, 6, 25, 26, 37, 38):
        plan = measure_activity_header(
            page,
            mission_number=6,
            mission_title="Kindness at the Fall Festival",
            activity_title="Find the Kindness Gifts",
            reference="Ephesians 4:32",
            activity_label="Search & Find",
            instruction="Find and circle all 8 kindness gifts.",
        )
        assert plan.state.clipped == []
        assert plan.state.ok(), (page, plan.state.as_fields())


def test_primary_faces_are_not_helvetica():
    faces = primary_faces()
    for face in faces:
        assert face not in FORBIDDEN_PRIMARY
    assert DISPLAY in faces
    assert BODY in faces
