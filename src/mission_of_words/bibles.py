"""Cast/style and composition bibles — the page-architecture source of truth."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from mission_of_words.book_manifest import load_mission_records
from mission_of_words.paths import CONTENT_DIR

CAST_BIBLE = CONTENT_DIR / "cast_style_bible.json"
COMPOSITION_BIBLE = CONTENT_DIR / "composition_bible.json"

MISSION_IDS = tuple(f"mission_{index:02d}" for index in range(1, 9))
HERO_KEYS = ("banner",)
SEARCH_KEYS = ("scene_frame",)
MAZE_KEYS = ("environment_kind",)
FAITH_KEYS = ("card_layout", "drawing_shape", "prayer_treatment")


@lru_cache(maxsize=1)
def load_cast_bible() -> dict[str, Any]:
    return json.loads(CAST_BIBLE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_composition_bible() -> dict[str, Any]:
    return json.loads(COMPOSITION_BIBLE.read_text(encoding="utf-8"))


def mission_recipe(mission_id: str) -> dict[str, Any]:
    bible = load_composition_bible()
    recipe = bible["missions"].get(mission_id)
    if not recipe:
        raise KeyError(f"composition bible missing {mission_id}")
    return recipe


def hiding_zones_for(mission: dict[str, Any]) -> list[dict[str, Any]]:
    """Named environment pockets that must contain the eight code-placed targets."""
    recipe = mission_recipe(mission["id"])
    environment = str(recipe["environment"])
    zones = []
    for target in mission["pages"][1]["targets"]:
        x = float(target["x"])
        y = float(target["y"])
        scale = float(target["scale"])
        pad = max(0.07, scale * 0.7)
        zx = max(0.0, x - pad)
        zy = max(0.0, y - pad)
        zones.append(
            {
                "id": f"{target['name']}_zone",
                "target": target["name"],
                "environment": environment,
                "x": round(zx, 4),
                "y": round(zy, 4),
                "w": round(min(1.0 - zx, scale + pad * 2), 4),
                "h": round(min(1.0 - zy, scale + pad * 2), 4),
            }
        )
    return zones


def target_in_zone(target: dict[str, Any], zone: dict[str, Any]) -> bool:
    return (
        zone["x"] - 0.001 <= float(target["x"]) <= zone["x"] + zone["w"] + 0.001
        and zone["y"] - 0.001 <= float(target["y"]) <= zone["y"] + zone["h"] + 0.001
    )


def uniqueness_report() -> dict[str, Any]:
    bible = load_composition_bible()
    missions = bible["missions"]
    buckets = {
        "hero.banner": [missions[mid]["hero"]["banner"] for mid in MISSION_IDS],
        "search.scene_frame": [missions[mid]["search"]["scene_frame"] for mid in MISSION_IDS],
        "maze.environment_kind": [missions[mid]["maze"]["environment_kind"] for mid in MISSION_IDS],
        "faith.card_layout": [missions[mid]["faith"]["card_layout"] for mid in MISSION_IDS],
        "faith.drawing_shape": [missions[mid]["faith"]["drawing_shape"] for mid in MISSION_IDS],
        "motif": [missions[mid]["motif"] for mid in MISSION_IDS],
    }
    cloned = {key: values for key, values in buckets.items() if len(set(values)) != 8}
    fractions = []
    legend = []
    windows = []
    for mid in MISSION_IDS:
        hero = missions[mid]["hero"]
        search = missions[mid]["search"]
        maze = missions[mid]["maze"]
        fractions.append(float(hero["art_fraction"]))
        legend.append(float(search["legend_fraction"]))
        windows.append(bool(maze.get("white_window")))
    return {
        "mission_count": len(missions),
        "cloned_keys": cloned,
        "unique": not cloned,
        "hero_art_fractions": fractions,
        "search_legend_fractions": legend,
        "any_maze_white_window": any(windows),
    }


def validate_bibles() -> list[str]:
    failures: list[str] = []
    cast = load_cast_bible()
    names = [member["id"] for member in cast.get("cast") or []]
    if names != ["mira", "eli", "joy", "caleb", "pip"]:
        failures.append(f"cast must be Mira, Eli, Joy, Caleb, Pip; got {names}")
    if "no_text" not in json.dumps(cast).lower() and "NO titles" not in json.dumps(cast):
        failures.append("cast/style bible must lock a no-text rule")
    bible = load_composition_bible()
    report = uniqueness_report()
    if report["cloned_keys"]:
        failures.append(f"cloned mission compositions: {sorted(report['cloned_keys'])}")
    if report["any_maze_white_window"]:
        failures.append("maze white_window must be false for every mission")
    floors = bible["fractions"]
    for fraction in report["hero_art_fractions"]:
        if not (floors["hero_art_min"] - 0.001 <= fraction <= floors["hero_art_max"] + 0.001):
            failures.append(f"hero art fraction {fraction} outside 70-80%")
    for fraction in report["search_legend_fractions"]:
        if fraction > floors["search_legend_max"] + 0.001:
            failures.append(f"search legend fraction {fraction} exceeds 14%")
    for mission in load_mission_records():
        zones = hiding_zones_for(mission)
        if len(zones) != 8:
            failures.append(f"{mission['id']} does not have 8 hiding zones")
        by_name = {zone["target"]: zone for zone in zones}
        for target in mission["pages"][1]["targets"]:
            zone = by_name[target["name"]]
            if not target_in_zone(target, zone):
                failures.append(f"{mission['id']} target {target['name']} is outside its hiding zone")
        maze = mission_recipe(mission["id"])["maze"]
        if maze.get("white_window"):
            failures.append(f"{mission['id']} maze still uses a white window")
    if bible.get("owner_facing") is True:
        failures.append("composition bible must stay internal until GPT2 art exists")
    return failures
