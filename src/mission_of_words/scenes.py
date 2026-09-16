"""Unique integrated coloring scenes for each Bright Hearts mission."""

from __future__ import annotations

from reportlab.pdfgen import canvas

from mission_of_words import art


def draw_coloring_scene(c: canvas.Canvas, mission_id: str, box: tuple[float, float, float, float]) -> list[str]:
    drawers = {
        "mission_01": _festival_lanterns,
        "mission_02": _sky_orchard,
        "mission_03": _harvest_wagon,
        "mission_04": _courage_path,
        "mission_05": _porch_sharing,
        "mission_06": _include_a_friend,
        "mission_07": _creation_hillside,
        "mission_08": _thankful_table,
    }
    if mission_id not in drawers:
        raise ValueError(f"no coloring scene for {mission_id}")
    return drawers[mission_id](c, box)


def _festival_lanterns(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_cloud(c, left + w * 0.08, bottom + h * 0.82, w * 0.22)
    art.draw_cloud(c, left + w * 0.70, bottom + h * 0.86, w * 0.20)
    art.draw_ground(c, left, bottom, w, h * 0.38)
    art.draw_path(
        c,
        [(left + w * 0.18, bottom + 8), (left + w * 0.36, bottom + h * 0.22), (left + w * 0.46, bottom + h * 0.36)],
        width=w * 0.16,
    )
    art.draw_tree(c, left + w * 0.02, bottom + h * 0.22, w * 0.22, h * 0.52)
    art.draw_church(c, left + w * 0.32, bottom + h * 0.32, w * 0.36, h * 0.52)
    art.draw_string_lights(c, left + w * 0.20, bottom + h * 0.70, left + w * 0.40, bottom + h * 0.78, bulbs=6)
    art.draw_string_lights(c, left + w * 0.64, bottom + h * 0.78, left + w * 0.86, bottom + h * 0.62, bulbs=6)
    art.draw_table(c, left + w * 0.72, bottom + h * 0.28, w * 0.22, h * 0.22)
    art.draw_lantern_post(c, left + w * 0.90, bottom + h * 0.28, h * 0.28)
    art.draw_pumpkin(c, left + w * 0.06, bottom + h * 0.08, w * 0.10)
    art.draw_pumpkin(c, left + w * 0.16, bottom + h * 0.05, w * 0.08)
    art.draw_pumpkin(c, left + w * 0.78, bottom + h * 0.10, w * 0.09)
    art.draw_leaf(c, left + w * 0.28, bottom + h * 0.04, w * 0.07)
    art.draw_leaf(c, left + w * 0.62, bottom + h * 0.06, w * 0.06)
    art.draw_child(c, left + w * 0.28, bottom + h * 0.07, h * 0.34, facing=1, hair="bob", lantern=True)
    art.draw_child(c, left + w * 0.66, bottom + h * 0.08, h * 0.36, facing=-1, hair="short", lantern=True)
    return ["church", "steeple_cross", "children", "lanterns", "pumpkins", "leaves", "string_lights", "welcome_table", "tree"]


def _sky_orchard(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_sun(c, left + w * 0.16, bottom + h * 0.78, w * 0.08)
    art.draw_moon(c, left + w * 0.78, bottom + h * 0.80, w * 0.07)
    art.draw_star(c, left + w * 0.42, bottom + h * 0.88, w * 0.03)
    art.draw_star(c, left + w * 0.55, bottom + h * 0.84, w * 0.025)
    art.draw_star(c, left + w * 0.64, bottom + h * 0.90, w * 0.02)
    art.draw_cloud(c, left + w * 0.28, bottom + h * 0.86, w * 0.16)
    art.draw_ground(c, left, bottom, w, h * 0.42)
    art.draw_path(c, [(left + w * 0.12, bottom + 6), (left + w * 0.40, bottom + h * 0.28), (left + w * 0.70, bottom + h * 0.34)], width=w * 0.14)
    art.draw_tree(c, left + w * 0.04, bottom + h * 0.20, w * 0.22, h * 0.48)
    art.draw_tree(c, left + w * 0.52, bottom + h * 0.22, w * 0.24, h * 0.50)
    art.draw_tree(c, left + w * 0.76, bottom + h * 0.18, w * 0.20, h * 0.44)
    art.draw_apple(c, left + w * 0.12, bottom + h * 0.18, w * 0.05)
    art.draw_apple(c, left + w * 0.58, bottom + h * 0.16, w * 0.05)
    art.draw_child(c, left + w * 0.36, bottom + h * 0.06, h * 0.32, facing=1, hair="short", lantern=False)
    return ["setting_sun", "rising_moon", "stars", "apple_trees", "orchard_path", "child_looking_up"]


def _harvest_wagon(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_cloud(c, left + w * 0.62, bottom + h * 0.84, w * 0.18)
    art.draw_ground(c, left, bottom, w, h * 0.40)
    art.draw_barn(c, left + w * 0.08, bottom + h * 0.28, w * 0.36, h * 0.52)
    art.draw_wagon(c, left + w * 0.46, bottom + h * 0.16, w * 0.32, h * 0.28)
    art.draw_wheat(c, left + w * 0.52, bottom + h * 0.36, h * 0.16)
    art.draw_wheat(c, left + w * 0.58, bottom + h * 0.34, h * 0.18)
    art.draw_wheat(c, left + w * 0.64, bottom + h * 0.36, h * 0.14)
    art.rect(c, left + w * 0.70, bottom + h * 0.34, w * 0.04, h * 0.16, 1.5)
    art.oval(c, left + w * 0.68, bottom + h * 0.46, left + w * 0.76, bottom + h * 0.58, 1.4)
    art.draw_pumpkin(c, left + w * 0.82, bottom + h * 0.10, w * 0.08)
    art.draw_child(c, left + w * 0.40, bottom + h * 0.06, h * 0.30, facing=1, hair="bob", lantern=False)
    art.draw_child(c, left + w * 0.86, bottom + h * 0.06, h * 0.32, facing=-1, hair="short", lantern=False)
    art.draw_bible(c, left + w * 0.36, bottom + h * 0.08, w * 0.07)
    return ["harvest_wagon", "wheat_sheaves", "corn_stalks", "barn", "thankful_family", "hymn_book"]


def _courage_path(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_cloud(c, left + w * 0.10, bottom + h * 0.86, w * 0.18)
    art.draw_ground(c, left, bottom, w, h * 0.36)
    art.draw_tree(c, left + w * 0.02, bottom + h * 0.22, w * 0.20, h * 0.56)
    art.draw_tree(c, left + w * 0.18, bottom + h * 0.26, w * 0.18, h * 0.50)
    art.draw_tree(c, left + w * 0.40, bottom + h * 0.24, w * 0.16, h * 0.46)
    art.draw_path(
        c,
        [(left + w * 0.10, bottom + 8), (left + w * 0.36, bottom + h * 0.20), (left + w * 0.70, bottom + h * 0.28)],
        width=w * 0.12,
    )
    art.draw_porch(c, left + w * 0.62, bottom + h * 0.28, w * 0.34, h * 0.48, lit=True)
    art.draw_leaf(c, left + w * 0.22, bottom + h * 0.06, w * 0.06)
    art.draw_leaf(c, left + w * 0.48, bottom + h * 0.04, w * 0.07)
    art.draw_child(c, left + w * 0.30, bottom + h * 0.06, h * 0.32, facing=1, hair="short", lantern=True)
    return ["walking_child", "autumn_path", "tall_trees", "lit_porch", "handheld_light", "fallen_leaves"]


def _porch_sharing(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_cloud(c, left + w * 0.70, bottom + h * 0.84, w * 0.16)
    art.draw_ground(c, left, bottom, w, h * 0.34)
    art.draw_porch(c, left + w * 0.42, bottom + h * 0.26, w * 0.50, h * 0.56, lit=False)
    art.draw_child(c, left + w * 0.22, bottom + h * 0.06, h * 0.32, facing=1, hair="bob", lantern=False)
    art.draw_child(c, left + w * 0.38, bottom + h * 0.06, h * 0.34, facing=1, hair="short", lantern=False)
    art.draw_child(c, left + w * 0.72, bottom + h * 0.18, h * 0.30, facing=-1, hair="bob", lantern=False)
    art.draw_basket(c, left + w * 0.28, bottom + h * 0.08, w * 0.10)
    art.draw_apple(c, left + w * 0.30, bottom + h * 0.16, w * 0.05)
    art.draw_loaf(c, left + w * 0.46, bottom + h * 0.10, w * 0.10)
    art.rect(c, left + w * 0.56, bottom + h * 0.12, w * 0.04, h * 0.08, 1.4)
    art.rect(c, left + w * 0.61, bottom + h * 0.10, w * 0.04, h * 0.10, 1.4)
    return ["sharing_children", "neighbor_porch", "apple_basket", "shared_loaf", "neighbor_at_door", "jars_on_step"]


def _include_a_friend(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_ground(c, left, bottom, w, h * 0.36)
    art.draw_booth(c, left + w * 0.28, bottom + h * 0.28, w * 0.46, h * 0.50)
    art.draw_string_lights(c, left + w * 0.18, bottom + h * 0.78, left + w * 0.80, bottom + h * 0.80, bulbs=7)
    art.draw_chair(c, left + w * 0.58, bottom + h * 0.10, w * 0.12, h * 0.22)
    art.draw_child(c, left + w * 0.22, bottom + h * 0.06, h * 0.30, facing=1, hair="bob", lantern=False)
    art.draw_child(c, left + w * 0.36, bottom + h * 0.06, h * 0.32, facing=1, hair="short", lantern=False)
    art.draw_child(c, left + w * 0.78, bottom + h * 0.06, h * 0.30, facing=-1, hair="bob", lantern=False)
    art.circle(c, left + w * 0.48, bottom + h * 0.18, w * 0.03, 1.5)
    art.circle(c, left + w * 0.54, bottom + h * 0.16, w * 0.03, 1.5)
    art.oval(c, left + w * 0.62, bottom + h * 0.36, left + w * 0.70, bottom + h * 0.46, 1.3)
    art.oval(c, left + w * 0.72, bottom + h * 0.36, left + w * 0.80, bottom + h * 0.46, 1.3)
    return ["game_booth", "ring_toss", "inviting_children", "lonely_child", "extra_chair", "cider_cups"]


def _creation_hillside(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_cloud(c, left + w * 0.12, bottom + h * 0.86, w * 0.18)
    art.draw_cloud(c, left + w * 0.70, bottom + h * 0.88, w * 0.16)
    art.draw_ground(c, left, bottom, w, h * 0.46)
    art.draw_creek(c, left + w * 0.08, bottom + h * 0.10, w * 0.84, h * 0.28)
    art.draw_tree(c, left + w * 0.06, bottom + h * 0.28, w * 0.22, h * 0.50)
    art.draw_tree(c, left + w * 0.72, bottom + h * 0.30, w * 0.24, h * 0.52)
    art.draw_deer(c, left + w * 0.42, bottom + h * 0.18, w * 0.22, h * 0.28)
    art.draw_child(c, left + w * 0.22, bottom + h * 0.16, h * 0.26, facing=1, hair="short", lantern=False)
    art.circle(c, left + w * 0.60, bottom + h * 0.72, 6, 1.3)
    art.circle(c, left + w * 0.66, bottom + h * 0.76, 5, 1.3)
    art.circle(c, left + w * 0.54, bottom + h * 0.78, 4, 1.3)
    return ["autumn_hillside", "creek", "oak_trees", "deer", "birds", "child_on_rock"]


def _thankful_table(c: canvas.Canvas, box: tuple[float, float, float, float]) -> list[str]:
    left, bottom, right, top = box
    w, h = right - left, top - bottom
    art.draw_window(c, left + w * 0.08, bottom + h * 0.58, w * 0.28, h * 0.28)
    art.draw_leaf(c, left + w * 0.12, bottom + h * 0.52, w * 0.06)
    art.draw_leaf(c, left + w * 0.22, bottom + h * 0.50, w * 0.05)
    art.draw_table(c, left + w * 0.22, bottom + h * 0.22, w * 0.56, h * 0.32)
    art.draw_chair(c, left + w * 0.08, bottom + h * 0.10, w * 0.14, h * 0.28)
    art.draw_chair(c, left + w * 0.78, bottom + h * 0.10, w * 0.14, h * 0.28)
    art.draw_chair(c, left + w * 0.42, bottom + h * 0.06, w * 0.14, h * 0.22)
    art.draw_basket(c, left + w * 0.46, bottom + h * 0.46, w * 0.12)
    art.draw_loaf(c, left + w * 0.48, bottom + h * 0.52, w * 0.10)
    art.draw_child(c, left + w * 0.28, bottom + h * 0.08, h * 0.28, facing=1, hair="bob", lantern=False)
    art.draw_child(c, left + w * 0.68, bottom + h * 0.08, h * 0.30, facing=-1, hair="short", lantern=False)
    return ["family_table", "autumn_meal", "empty_chair", "clasped_hands", "bread_basket", "leafy_window"]
