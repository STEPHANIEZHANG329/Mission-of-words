from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from llk import PAID_CALL_CAP
from llk.paths import CANON, CONTENT, MISSIONS
from llk import style as prompts

PAGE_COUNT = 48
MISSION_COUNT = 8
TARGETS_PER_SEARCH = 8


@dataclass(frozen=True)
class Target:
    name: str
    x: float
    y: float
    scale: float


@dataclass(frozen=True)
class MissionPage:
    slot: str
    type: str
    title: str
    mechanic: str
    instruction: str
    bible_connection: str
    visual_prompt: str
    required_objects: list[str]
    targets: tuple[Target, ...] = ()
    choices: tuple[dict[str, str], ...] = ()
    drawing_prompt: str = ""
    prayer: str = ""
    start_label: str = "START"
    finish_label: str = "FINISH"
    maze_seed: int = 0
    maze_grid: tuple[int, int] = (8, 10)


@dataclass(frozen=True)
class Mission:
    id: str
    title: str
    scripture_reference: str
    canon_id: str
    sequence: int
    global_page_start: int
    pages: tuple[MissionPage, ...]


@dataclass(frozen=True)
class Canon:
    canon_id: str
    reference: str
    source_text: str
    child_paraphrase: str
    translation: str
    license: str


@dataclass(frozen=True)
class AssetSpec:
    asset_id: str
    role: str
    group: str
    size: str
    prompt: str
    sheet_names: tuple[str, ...] = ()


@dataclass(frozen=True)
class BookSpec:
    meta: dict[str, Any]
    missions: tuple[Mission, ...]
    canon: dict[str, Canon]
    assets: tuple[AssetSpec, ...]
    pages: tuple[dict[str, Any], ...]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_book_meta() -> dict[str, Any]:
    return _load_json(CONTENT / "book.json")


def load_canon() -> dict[str, Canon]:
    out: dict[str, Canon] = {}
    for path in sorted(CANON.glob("*.json")):
        raw = _load_json(path)
        item = Canon(
            canon_id=raw["canon_id"],
            reference=raw["reference"],
            source_text=raw["source_text"],
            child_paraphrase=raw["child_paraphrase"],
            translation=raw["translation"],
            license=raw["license"],
        )
        out[item.canon_id] = item
    return out


def load_missions() -> tuple[Mission, ...]:
    missions: list[Mission] = []
    for path in sorted(MISSIONS.glob("mission_*.json")):
        raw = _load_json(path)
        pages: list[MissionPage] = []
        slots = "ABCD"
        for i, p in enumerate(raw["pages"]):
            targets = tuple(
                Target(name=t["name"], x=float(t["x"]), y=float(t["y"]), scale=float(t["scale"]))
                for t in p.get("targets", [])
            )
            choices = tuple(p.get("choices", ()))
            grid = p.get("grid") or [8, 10]
            pages.append(
                MissionPage(
                    slot=slots[i],
                    type=p["type"],
                    title=p["title"],
                    mechanic=p["activity_mechanic"],
                    instruction=p.get("child_instruction") or p.get("instruction") or "",
                    bible_connection=p.get("bible_connection", ""),
                    visual_prompt=p.get("visual_prompt", ""),
                    required_objects=list(p.get("required_objects", [])),
                    targets=targets,
                    choices=choices,
                    drawing_prompt=p.get("drawing_prompt", ""),
                    prayer=p.get("prayer", ""),
                    start_label=p.get("start_label", "START"),
                    finish_label=p.get("finish_label", "FINISH"),
                    maze_seed=int(p.get("seed") or (20260916 + raw["sequence"])),
                    maze_grid=(int(grid[0]), int(grid[1])),
                )
            )
        missions.append(
            Mission(
                id=raw["id"],
                title=raw["title"],
                scripture_reference=raw["scripture_reference"],
                canon_id=raw["canon_id"],
                sequence=int(raw["sequence"]),
                global_page_start=int(raw["global_page_start"]),
                pages=tuple(pages),
            )
        )
    missions.sort(key=lambda m: m.sequence)
    return tuple(missions)


def _sheet_groups(missions: tuple[Mission, ...]) -> list[tuple[str, tuple[str, ...]]]:
    names: list[str] = []
    for mission in missions:
        search = next(p for p in mission.pages if p.type == "search_find")
        for t in search.targets:
            names.append(t.name)
    # 8 missions * 8 targets = 64 names, packed into 4 sheets of 16.
    sheets = []
    for i in range(0, len(names), 16):
        chunk = tuple(names[i : i + 16])
        a = (i // 16) * 2 + 1
        b = a + 1
        sheets.append((f"targets_m{a}{b}", chunk))
    return sheets


def planned_assets(missions: tuple[Mission, ...] | None = None) -> tuple[AssetSpec, ...]:
    missions = missions or load_missions()
    assets: list[AssetSpec] = [
        AssetSpec("title_scene", "title_lockup", "front", "1024x1536", prompts.title_prompt()),
        AssetSpec("welcome_cast", "welcome_spot", "front", "1024x1536", prompts.welcome_prompt()),
        AssetSpec("missions_map", "missions_map", "front", "1024x1536", prompts.map_prompt()),
        AssetSpec("parent_spot", "parent_letter", "front", "1024x1536", prompts.parent_prompt()),
    ]
    for mission in missions:
        mid = mission.id
        coloring = mission.pages[0]
        search = mission.pages[1]
        maze = mission.pages[2]
        faith = mission.pages[3]
        target_names = [t.name for t in search.targets]
        assets.append(
            AssetSpec(
                f"coloring_{mid}",
                "coloring_hero",
                "coloring",
                "1024x1536",
                prompts.coloring_prompt(coloring.visual_prompt, coloring.required_objects),
            )
        )
        assets.append(
            AssetSpec(
                f"search_bg_{mid}",
                "search_background",
                "search",
                "1024x1536",
                prompts.search_background_prompt(search.visual_prompt, target_names),
            )
        )
        assets.append(
            AssetSpec(
                f"maze_scene_{mid}",
                "maze_scene",
                "maze",
                "1024x1536",
                prompts.maze_scene_prompt(maze.visual_prompt, maze.required_objects),
            )
        )
        assets.append(
            AssetSpec(
                f"faith_{mid}",
                "faith_frame",
                "faith",
                "1024x1536",
                prompts.faith_prompt(faith.visual_prompt, [c["label"] for c in faith.choices]),
            )
        )
    for sheet_id, names in _sheet_groups(missions):
        assets.append(
            AssetSpec(
                sheet_id,
                "search_target_sheet",
                "targets",
                "1024x1024",
                prompts.target_sheet_prompt(list(names)),
                sheet_names=names,
            )
        )
    assets.extend(
        [
            AssetSpec("certificate_frame", "certificate_frame", "back", "1024x1536", prompts.certificate_prompt()),
            AssetSpec("closing_scene", "closing_lockup", "back", "1024x1536", prompts.closing_prompt()),
            AssetSpec("gratitude_spot", "bonus_activity", "back", "1024x1536", prompts.gratitude_prompt()),
            AssetSpec("cover_front", "cover", "cover", "1024x1536", prompts.cover_prompt()),
        ]
    )
    if len(assets) > PAID_CALL_CAP:
        raise RuntimeError(f"planned assets {len(assets)} exceed paid cap {PAID_CALL_CAP}")
    return tuple(assets)


def page_map(missions: tuple[Mission, ...] | None = None) -> tuple[dict[str, Any], ...]:
    missions = missions or load_missions()
    meta = load_book_meta()
    pages: list[dict[str, Any]] = [
        {"page": 1, "type": "title", "title": meta["title"], "art": "title_scene"},
        {"page": 2, "type": "welcome", "title": meta["welcome_title"], "art": "welcome_cast"},
        {"page": 3, "type": "contents", "title": meta["map_title"], "art": "missions_map"},
        {"page": 4, "type": "parent_note", "title": meta["parent_title"], "art": "parent_spot"},
    ]
    for mission in missions:
        start = mission.global_page_start
        kinds = ["coloring", "search_find", "maze", "faith_interaction"]
        arts = [
            f"coloring_{mission.id}",
            f"search_bg_{mission.id}",
            f"maze_scene_{mission.id}",
            f"faith_{mission.id}",
        ]
        for i, (kind, art) in enumerate(zip(kinds, arts)):
            mp = mission.pages[i]
            pages.append(
                {
                    "page": start + i,
                    "type": kind,
                    "title": mp.title,
                    "art": art,
                    "mission_id": mission.id,
                    "mission_sequence": mission.sequence,
                    "canon_id": mission.canon_id,
                    "slot": mp.slot,
                }
            )
    for i, mission in enumerate(missions):
        pages.append(
            {
                "page": 37 + i,
                "type": "answer_key",
                "title": f"Answer Key: {mission.title}",
                "art": f"coloring_{mission.id}",
                "mission_id": mission.id,
                "mission_sequence": mission.sequence,
                "canon_id": mission.canon_id,
                "answers_activity_pages": [mission.global_page_start + 1, mission.global_page_start + 2],
            }
        )
    pages.extend(
        [
            {"page": 45, "type": "bonus_gratitude", "title": meta["gratitude_title"], "art": "gratitude_spot"},
            {"page": 46, "type": "bonus_prayer_walk", "title": meta["prayer_walk_title"], "art": "gratitude_spot"},
            {"page": 47, "type": "certificate", "title": meta["certificate_title"], "art": "certificate_frame"},
            {"page": 48, "type": "closing", "title": meta["closing_title"], "art": "closing_scene"},
        ]
    )
    if len(pages) != PAGE_COUNT:
        raise RuntimeError(f"page map has {len(pages)} pages, expected {PAGE_COUNT}")
    return tuple(pages)


def load_spec() -> BookSpec:
    missions = load_missions()
    return BookSpec(
        meta=load_book_meta(),
        missions=missions,
        canon=load_canon(),
        assets=planned_assets(missions),
        pages=page_map(missions),
    )


def target_catalog(missions: tuple[Mission, ...] | None = None) -> dict[str, tuple[str, int, int]]:
    """Map target name -> (sheet_id, col, row) in a 4x4 sheet."""
    missions = missions or load_missions()
    catalog: dict[str, tuple[str, int, int]] = {}
    for sheet_id, names in _sheet_groups(missions):
        for i, name in enumerate(names):
            catalog[name] = (sheet_id, i % 4, i // 4)
    return catalog
