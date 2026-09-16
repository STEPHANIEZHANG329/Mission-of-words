"""Page 1: one integrated fall-festival coloring illustration."""

from __future__ import annotations

from reportlab.pdfgen import canvas

from mission_of_words import art
from mission_of_words.text import page_header


def draw_coloring_page(c: canvas.Canvas, spec: dict, canon: dict) -> dict:
    page = spec["mission"]["pages"][0]
    box, y = page_header(
        c,
        1,
        page["title"],
        page["child_instruction"],
        kicker=f"{canon['reference']}  ·  Color this picture",
    )
    left, bottom, right, top = box
    # Illustration lives in the remaining live area. No letters inside it.
    art_top = min(y, top - 72)
    art_bottom = bottom + 8
    art_left, art_right = left, right
    w = art_right - art_left
    h = art_top - art_bottom

    # sky clouds
    art.draw_cloud(c, art_left + w * 0.08, art_bottom + h * 0.82, w * 0.22)
    art.draw_cloud(c, art_left + w * 0.70, art_bottom + h * 0.86, w * 0.20)

    # ground and path
    art.draw_ground(c, art_left, art_bottom, w, h * 0.38)
    art.draw_path(
        c,
        [
            (art_left + w * 0.18, art_bottom + 8),
            (art_left + w * 0.36, art_bottom + h * 0.22),
            (art_left + w * 0.46, art_bottom + h * 0.36),
        ],
        width=w * 0.16,
    )

    # tree and string lights
    art.draw_tree(c, art_left + w * 0.02, art_bottom + h * 0.22, w * 0.22, h * 0.52)
    art.draw_church(c, art_left + w * 0.32, art_bottom + h * 0.32, w * 0.36, h * 0.52)
    art.draw_string_lights(
        c,
        art_left + w * 0.20,
        art_bottom + h * 0.70,
        art_left + w * 0.40,
        art_bottom + h * 0.78,
        bulbs=6,
    )
    art.draw_string_lights(
        c,
        art_left + w * 0.64,
        art_bottom + h * 0.78,
        art_left + w * 0.86,
        art_bottom + h * 0.62,
        bulbs=6,
    )

    art.draw_table(c, art_left + w * 0.72, art_bottom + h * 0.28, w * 0.22, h * 0.22)
    art.draw_lantern_post(c, art_left + w * 0.90, art_bottom + h * 0.28, h * 0.28)

    # pumpkins and leaves in the foreground (colorable closed shapes)
    art.draw_pumpkin(c, art_left + w * 0.06, art_bottom + h * 0.08, w * 0.10)
    art.draw_pumpkin(c, art_left + w * 0.16, art_bottom + h * 0.05, w * 0.08)
    art.draw_pumpkin(c, art_left + w * 0.78, art_bottom + h * 0.10, w * 0.09)
    art.draw_leaf(c, art_left + w * 0.28, art_bottom + h * 0.04, w * 0.07)
    art.draw_leaf(c, art_left + w * 0.62, art_bottom + h * 0.06, w * 0.06)
    art.draw_leaf(c, art_left + w * 0.84, art_bottom + h * 0.04, w * 0.07)

    # children carrying lanterns toward the church — foreground, thicker stroke
    art.draw_child(
        c,
        art_left + w * 0.28,
        art_bottom + h * 0.07,
        h * 0.34,
        facing=1,
        hair="bob",
        lantern=True,
    )
    art.draw_child(
        c,
        art_left + w * 0.66,
        art_bottom + h * 0.08,
        h * 0.36,
        facing=-1,
        hair="short",
        lantern=True,
    )

    return {
        "page": 1,
        "type": "coloring",
        "visual_prompt": page["visual_prompt"],
        "required_objects": list(page["required_objects"]),
        "drawn_objects": [
            "church",
            "steeple_cross",
            "children",
            "lanterns",
            "pumpkins",
            "leaves",
            "string_lights",
            "welcome_table",
            "tree",
        ],
        "text_in_artwork": False,
        "asset_integration": (
            "Single composed festival scene. Required objects are drawn in place, "
            "not patched onto a blank frame."
        ),
        "child_instruction": page["child_instruction"],
        "bible_connection": page["bible_connection"],
        "drawing_area_sqin": None,
    }
