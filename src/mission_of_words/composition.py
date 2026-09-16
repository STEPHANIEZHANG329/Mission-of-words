"""Cast/style + composition bibles. Factory geometry reads these files.

Internal engineering only until Owner reopens the layout gate. Nothing here
authorizes GPT2 spend or an Owner-facing product PDF.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from mission_of_words.paths import CONTENT_DIR

ART_BIBLE_PATH = CONTENT_DIR / "art_bible.json"
COMPOSITION_BIBLE_PATH = CONTENT_DIR / "composition_bible.json"

MISSION_IDS = tuple(f"mission_{index:02d}" for index in range(1, 9))


class CompositionError(ValueError):
    """Raised when a bible is missing, incomplete, or cloned."""


@lru_cache(maxsize=1)
def load_art_bible() -> dict[str, Any]:
    if not ART_BIBLE_PATH.is_file():
        raise CompositionError("missing content/art_bible.json")
    return json.loads(ART_BIBLE_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_composition_bible() -> dict[str, Any]:
    if not COMPOSITION_BIBLE_PATH.is_file():
        raise CompositionError("missing content/composition_bible.json")
    return json.loads(COMPOSITION_BIBLE_PATH.read_text(encoding="utf-8"))


def live_rules() -> dict[str, Any]:
    return dict(load_composition_bible()["live_area"])


def hero_art_ratio_bounds() -> tuple[float, float]:
    rules = live_rules()
    return float(rules["hero_art_ratio_min"]), float(rules["hero_art_ratio_max"])


def search_legend_max_pt() -> float:
    return float(live_rules()["search_legend_max_pt"])


def search_legend_height() -> float:
    """Compact numbered-icon row. Secondary to the scene."""
    return min(44.0, search_legend_max_pt())


def maze_path_min_ratio() -> float:
    return float(live_rules()["maze_path_min_ratio"])


def faith_drawing_min_sqin() -> float:
    return float(live_rules()["faith_drawing_min_sqin"])


def mission_plan(mission_id: str) -> dict[str, Any]:
    missions = load_composition_bible().get("missions") or {}
    if mission_id not in missions:
        raise CompositionError(f"composition bible missing {mission_id}")
    return dict(missions[mission_id])


def maze_embed(mission_id: str) -> str:
    return str(mission_plan(mission_id)["maze_embed"])


def faith_rhythm(mission_id: str) -> str:
    return str(mission_plan(mission_id)["faith_rhythm"])


def art_ratio(art_box: tuple[float, float, float, float], live_box: tuple[float, float, float, float]) -> float:
    live_h = live_box[3] - live_box[1]
    art_h = art_box[3] - art_box[1]
    if live_h <= 0:
        return 0.0
    return art_h / live_h


def maze_path_box(art_box: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """The path occupies most of the scene. Not a floating window."""
    left, bottom, right, top = art_box
    width, height = right - left, top - bottom
    pad_x = min(40.0, width * 0.055)
    pad_y = min(44.0, height * 0.06)
    return left + pad_x, bottom + pad_y, right - pad_x, top - pad_y


def validate_bibles() -> list[str]:
    """Return human-readable defects. Empty list means the factory may proceed."""
    defects: list[str] = []
    art = load_art_bible()
    comp = load_composition_bible()
    lock = art.get("style_lock") or {}
    if "NO" not in str(lock.get("no_text") or "").upper() and "no_text" not in lock:
        defects.append("art bible is missing the no-text lock")
    names = [str(member.get("id")) for member in art.get("cast") or []]
    for required in ("mira", "eli", "joy", "caleb", "pip"):
        if required not in names:
            defects.append(f"art bible missing cast member {required}")
    for field in ("face_proportions", "clothing_logic", "line_weight", "environment_language", "icon_family"):
        if not lock.get(field):
            defects.append(f"art bible missing style_lock.{field}")

    brand = comp.get("brand") or {}
    if brand.get("consumer_title") != "Little Lampkeepers: Shine Your Light This Fall":
        defects.append("composition bible consumer title is not locked")
    if brand.get("forbidden_consumer_mark") != "Bright Hearts":
        defects.append("composition bible must forbid Bright Hearts on consumer output")

    missions = comp.get("missions") or {}
    embeds = []
    rhythms = []
    environments = []
    for mission_id in MISSION_IDS:
        plan = missions.get(mission_id)
        if not isinstance(plan, dict):
            defects.append(f"composition bible missing {mission_id}")
            continue
        for key in ("environment", "maze_embed", "faith_rhythm", "hero_cast", "hiding_zones"):
            if not plan.get(key):
                defects.append(f"{mission_id} missing {key}")
        embeds.append(plan.get("maze_embed"))
        rhythms.append(plan.get("faith_rhythm"))
        environments.append(plan.get("environment"))
        zones = plan.get("hiding_zones") or []
        if len(zones) < 4:
            defects.append(f"{mission_id} needs at least 4 hiding zones")
        cast = plan.get("hero_cast") or []
        if len(cast) < 3:
            defects.append(f"{mission_id} hero cast must include at least 3 characters")
    if len(set(embeds)) < 8:
        defects.append("maze embeds are cloned across missions")
    if len(set(environments)) < 8:
        defects.append("environments are cloned across missions")
    if len(set(rhythms)) < 6:
        defects.append("faith rhythms are not distinct enough")

    rules = comp.get("live_area") or {}
    if float(rules.get("hero_art_ratio_min") or 0) != 0.7:
        defects.append("hero_art_ratio_min must be 0.7")
    if float(rules.get("hero_art_ratio_max") or 0) != 0.8:
        defects.append("hero_art_ratio_max must be 0.8")
    if float(rules.get("search_legend_max_pt") or 0) > 48:
        defects.append("search legend is not compact")
    if comp.get("owner_facing_product") is True:
        defects.append("composition bible must not claim Owner-facing product status")
    return defects
