"""Complete 48-page production asset and prompt manifest.

Models draw; code decides. Prompts never include final page titles,
instructions, scripture quotations, labels, or page numbers.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from mission_of_words.art_bible import (
    ART_BIBLE_VERSION,
    CHARACTER_BIBLE_VERSION,
    NEGATIVE_PROMPT,
    NO_TEXT_CONTRACT,
    PROMPT_VERSION,
    STYLE_CONTRACT,
    load_art_bible,
)
from mission_of_words.book_manifest import TARGET_PAGE_COUNT, load_manifest, load_mission_records
from mission_of_words.layout import DPI, content_box
from mission_of_words.page_search import LEGEND_H, search_geometry
from mission_of_words.paths import PRODUCTION_ASSETS, SCHEMA_DIR
from mission_of_words.validate import validate_file, validate_instance

HEADER_RESERVE_PT = 110
FAITH_ICON_PX = 768
TARGET_PX = 1024
SPOT_PX = 1800

FORBIDDEN_PROMPT_SNIPPETS = (
    "child_instruction",
    "page_number",
    "NON-PRODUCTION",
    "King James",
)

FRONT_SPECS = {
    1: {
        "role": "title_lockup",
        "scene": (
            "Wide autumn churchyard scene used as a title-page illustration: Mira Bright "
            "and Eli Bright in the foreground holding closed lanterns, a small church with "
            "an intact steeple cross in the midground, pumpkins and falling leaves, string "
            "lights with empty bulb shapes, and a simple path. Leave a large open sky and "
            "foreground for later typesetting. No people holding signs."
        ),
        "cast": ["mira_bright", "eli_bright"],
    },
    2: {
        "role": "welcome_spot",
        "scene": (
            "A compact spot illustration of Mira and Eli sitting on a leaf-strewn blanket "
            "with a closed coloring book and a lantern between them, church-festival trees "
            "behind. Generous white space around the figures so editorial type can sit beside them."
        ),
        "cast": ["mira_bright", "eli_bright"],
    },
    3: {
        "role": "missions_map",
        "scene": (
            "A pictorial autumn path winding past eight distinct landmark vignettes "
            "(church festival, orchard dusk, harvest wagon, woods porch, neighbor porch, "
            "festival booth, hillside creek, family table) connected by a leaf-lined trail. "
            "No numerals, no captions, no map keys. Landmarks must be visually distinct."
        ),
        "cast": ["mira_bright"],
    },
    4: {
        "role": "parent_letter",
        "scene": (
            "A small heading ornament: an open adult hand and a child's hand sharing a "
            "lantern, oak leaves, and a tiny intact church cross. Lots of white space. "
            "No lettering on a ribbon or card."
        ),
        "cast": [],
    },
}

BACK_SPECS = {
    45: {
        "role": "bonus_activity",
        "scene": (
            "Gratitude-journal header art: Mira drawing in an open blank notebook at a "
            "window with falling leaves, a small heart-shaped locket (no words), and a "
            "lantern on the sill. Large empty page area below the illustration."
        ),
        "cast": ["mira_bright"],
    },
    46: {
        "role": "bonus_activity",
        "scene": (
            "Prayer-walk header art: Eli and an adult walking a quiet autumn lane, "
            "noticing a bird and a leaf, lantern in hand. Wide sky and path. No street signs."
        ),
        "cast": ["eli_bright", "pastor_grace"],
    },
    47: {
        "role": "certificate_frame",
        "scene": (
            "Certificate ornamental frame of oak leaves, lanterns, and an intact cross, "
            "with a large empty white center for later typesetting. No names, dates, or mottoes."
        ),
        "cast": [],
    },
    48: {
        "role": "closing_lockup",
        "scene": (
            "Closing scene distinct from the title page: Mira and Eli walking away down a "
            "lantern-lit path at dusk, church small in the distance, hearts suggested by "
            "leaf shapes rather than text. Generous sky."
        ),
        "cast": ["mira_bright", "eli_bright"],
    },
}

MISSION_CAST = {
    "mission_01": ["mira_bright", "eli_bright"],
    "mission_02": ["mira_bright"],
    "mission_03": ["mira_bright", "eli_bright", "pastor_grace"],
    "mission_04": ["eli_bright"],
    "mission_05": ["mira_bright", "eli_bright", "neighbor_han"],
    "mission_06": ["mira_bright", "eli_bright", "supporting_child"],
    "mission_07": ["mira_bright"],
    "mission_08": ["mira_bright", "eli_bright", "pastor_grace"],
}

FAITH_ICON_SCENES = {
    "help": "two children, one offering a basket of food to the other, no letters",
    "share": "two children exchanging an apple, no letters",
    "kind": "a simple heart held in two small hands, no letters",
    "thank": "a child with clasped hands beside a closed lantern, no letters",
    "sunrise": "a rising sun over an orchard hill, no letters",
    "moon": "a crescent moon over quiet trees, no letters",
    "leaf": "a single detailed autumn leaf, no letters",
    "pray": "a child with clasped hands looking up, no letters",
    "bread": "a round loaf on a cloth, no letters",
    "family": "two children and one adult in a small group hug, no letters",
    "hands": "an adult hand helping a child hand, no letters",
    "song": "a simple songbird on a fence, no letters",
    "adult": "a child reaching toward a standing grown-up, no letters",
    "heart": "a clear heart shape with a small lantern inside, no letters",
    "friend": "two children walking side by side, no letters",
    "apple": "a child handing an apple to another child, no letters",
    "clock": "a simple round analog clock with blank face (no numerals)",
    "smile": "a round badge with a simple smile, no letters",
    "coat": "a child offering a coat to a friend, no letters",
    "words": "two children facing each other with open friendly mouths, no letters",
    "include": "two children waving a third child toward an extra chair, no letters",
    "forgive": "two children shaking hands, no letters",
    "turn": "two children beside a simple game ring, one stepping back, no letters",
    "bin": "a child dropping a wrapper into a bin, no letters",
    "plant": "small hands watering a potted plant, no letters",
    "bird": "a child watching a bird on a branch, no letters",
    "meal": "a set table with empty plates, no letters",
    "people": "three simple figures holding hands, no letters",
    "cloud": "a small rain cloud over a child with a lantern, no letters",
}

TARGET_SCENES = {
    "lantern": "closed handheld lantern with handle, glass panes, and a teardrop flame",
    "pumpkin": "intact pumpkin with stem and lobe lines, no carved face",
    "apple": "single apple with stem and one leaf",
    "leaf": "maple-style autumn leaf with simple veins",
    "acorn": "acorn with cap and tiny stem",
    "scarf": "folded winter scarf with short fringe",
    "basket": "picnic basket with high handle, empty inside",
    "Bible": "closed Bible with an intact Latin cross on the cover and no readable type",
    "sun_disk": "simple sun disk with eight short rays",
    "crescent_moon": "crescent moon, no face",
    "star": "five-point star, closed outline",
    "cloud": "puffy three-bump cloud",
    "sundial": "garden sundial on a short pedestal, blank face",
    "hourglass": "hourglass with empty bulbs",
    "sparrow": "small side-view sparrow",
    "season_leaf": "oval autumn leaf distinct from a maple leaf",
    "wheat_sheaf": "tied sheaf of wheat",
    "corn_cob": "corn cob with a few husk tips",
    "loaf": "round rustic loaf with score marks",
    "pitcher": "simple pitcher with handle",
    "pie": "whole pie with three simple slice lines",
    "hymn_book": "closed hymn book with a small cross, no type",
    "heart": "clear heart shape",
    "thank_you_card": "folded blank card with a tiny heart, no writing",
    "hiking_boot": "child hiking boot",
    "walking_stick": "wooden walking stick with a curved handle",
    "small_lantern": "compact lantern, distinct from the larger festival lantern",
    "trail_map": "folded blank trail map with a simple path line, no words",
    "compass": "round compass with a needle, no N/S/E/W letters",
    "owl": "perched owl, friendly not scary",
    "blanket": "folded striped blanket",
    "brave_badge": "round badge with a small star, no letters",
    "extra_apple": "apple with a noticeable extra leaf so it is not identical to the Mission 1 apple",
    "shared_loaf": "loaf with one slice started, distinct from Mission 3 loaf",
    "soup_pot": "covered soup pot with two handles",
    "empty_bowl": "empty bowl",
    "pair_of_gloves": "pair of child mittens",
    "jam_jar": "jam jar with a cloth lid, no label type",
    "note_card": "blank folded note, no writing",
    "wagon": "small garden wagon",
    "ticket": "blank carnival ticket stub, no numbers",
    "cider_cup": "mug of cider with a handle",
    "kind_note": "blank folded note with a heart, no writing",
    "extra_chair": "empty wooden chair",
    "smile_badge": "round smile badge, no letters",
    "bandage": "simple adhesive bandage",
    "shared_pretzel": "soft pretzel",
    "game_ring": "ring-toss ring",
    "oak_leaf": "lobed oak leaf",
    "pinecone": "pinecone",
    "deer": "small standing deer",
    "creek_fish": "simple fish",
    "mushroom": "toadstool mushroom",
    "bird_nest": "nest with two unmarked eggs",
    "pebble": "smooth creek pebble",
    "ladybug": "ladybug with a few spots, no numbers",
    "plate": "empty dinner plate",
    "cup": "simple cup",
    "napkin": "folded cloth napkin",
    "chair": "dining chair distinct from the extra festival chair",
    "bread_basket": "basket with a loaf peeking out",
    "candle": "unlit taper candle",
    "place_card": "blank folded place card, no name",
    "serving_spoon": "large serving spoon",
}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _content_pixels(page_number: int) -> tuple[int, int]:
    left, bottom, right, top = content_box(page_number)
    width_in = (right - left) / 72.0
    height_in = (top - bottom) / 72.0
    return max(1, round(width_in * DPI)), max(1, round(height_in * DPI))


def _hero_pixels(page_number: int) -> tuple[int, int]:
    left, bottom, right, top = content_box(page_number)
    width_in = (right - left) / 72.0
    height_in = max(1.0, (top - bottom - HEADER_RESERVE_PT) / 72.0)
    return max(1, round(width_in * DPI)), max(1, round(height_in * DPI))


def _search_pixels(page_number: int) -> tuple[int, int]:
    box, legend_h = search_geometry(page_number, marked_proof=False)
    left, bottom, right, top = box
    width_in = (right - left) / 72.0
    height_in = max(1.0, (top - bottom - legend_h - HEADER_RESERVE_PT) / 72.0)
    return max(1, round(width_in * DPI)), max(1, round(height_in * DPI))


def _cast_line(ids: list[str], bible: dict[str, Any]) -> str:
    by_id = {item["id"]: item for item in bible.get("cast") or []}
    parts = []
    for ident in ids:
        person = by_id[ident]
        parts.append(
            f"{person['name']} ({person['role']}, {person.get('hair', 'consistent hair')}, "
            f"locked Bright Hearts face language)"
        )
    if not parts:
        return "No required recurring characters; keep the same line style."
    return "Recurring cast: " + "; ".join(parts) + "."


def _prompt(*, scene: str, role: str, extra: str, cast_line: str) -> str:
    return (
        f"{STYLE_CONTRACT} Role: {role.replace('_', ' ')}. {cast_line} "
        f"{scene.strip()} {extra.strip()} {NO_TEXT_CONTRACT}"
    )


def _asset(
    *,
    asset_id: str,
    page: int,
    role: str,
    prompt: str,
    width_px: int,
    height_px: int,
    crop_rules: str,
    mission_id: str | None = None,
    target_name: str | None = None,
    choice_icon: str | None = None,
    required_objects: list[str] | None = None,
    excluded_targets: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "page": page,
        "mission_id": mission_id,
        "role": role,
        "needs_ai_art": True,
        "prompt_version": PROMPT_VERSION,
        "art_bible_version": ART_BIBLE_VERSION,
        "character_bible_version": CHARACTER_BIBLE_VERSION,
        "width_px": width_px,
        "height_px": height_px,
        "dpi": DPI,
        "status": "pending",
        "provider": None,
        "model": None,
        "cost_usd": 0.0,
        "attempt": 0,
        "accepted": False,
        "rejected": False,
        "rejection_reason": None,
        "source_prompt_hash": _sha(prompt),
        "final_file_hash": None,
        "prompt": prompt,
        "negative_prompt": NEGATIVE_PROMPT,
        "crop_rules": crop_rules,
        "target_name": target_name,
        "choice_icon": choice_icon,
        "required_objects": list(required_objects or []),
        "excluded_targets": list(excluded_targets or []),
        "file": None,
    }


def _page_row(
    *,
    page: int,
    page_type: str,
    needs_ai_art: bool,
    asset_ids: list[str],
    mission_id: str | None = None,
    reuses: list[int] | None = None,
) -> dict[str, Any]:
    row = {
        "page": page,
        "type": page_type,
        "mission_id": mission_id,
        "needs_ai_art": needs_ai_art,
        "layout": "ai_plus_code" if needs_ai_art else "code_only",
        "asset_ids": list(asset_ids),
    }
    if reuses:
        row["reuses_activity_pages"] = list(reuses)
    return row


def build_production_manifest(
    *,
    missions: list[dict[str, Any]] | None = None,
    manifest: dict[str, Any] | None = None,
    bible: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bible = bible or load_art_bible()
    missions = missions or load_mission_records()
    book_pages = list((manifest or load_manifest()).get("pages") or [])
    assets: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []

    for number, spec in FRONT_SPECS.items():
        width, height = _hero_pixels(number) if spec["role"] == "title_lockup" else (SPOT_PX, SPOT_PX)
        if spec["role"] == "missions_map":
            width, height = _hero_pixels(number)
        prompt = _prompt(
            scene=spec["scene"],
            role=spec["role"],
            extra="Keep a clear focal area. Preserve white open regions.",
            cast_line=_cast_line(spec["cast"], bible),
        )
        asset_id = f"p{number:02d}_{spec['role']}"
        assets.append(
            _asset(
                asset_id=asset_id,
                page=number,
                role=spec["role"],
                prompt=prompt,
                width_px=width,
                height_px=height,
                crop_rules="Place inside the live safety box under code-rendered type. Do not crop into 0.50 in outer / 0.625 in inner margins.",
            )
        )
        pages.append(
            _page_row(
                page=number,
                page_type={1: "title", 2: "welcome", 3: "contents", 4: "parent_note"}[number],
                needs_ai_art=True,
                asset_ids=[asset_id],
            )
        )

    for mission in missions:
        start = int(mission["global_page_start"])
        mission_id = str(mission["id"])
        cast_ids = MISSION_CAST[mission_id]
        coloring = mission["pages"][0]
        search = mission["pages"][1]
        maze = mission["pages"][2]
        faith = mission["pages"][3]

        coloring_id = f"{mission_id}_coloring_hero"
        coloring_prompt = _prompt(
            scene=str(coloring["visual_prompt"]),
            role="coloring_hero",
            extra=(
                "One integrated scene, not clip-art. 3-5 human figures maximum. "
                f"Required story objects: {', '.join(coloring['required_objects'])}."
            ),
            cast_line=_cast_line(cast_ids, bible),
        )
        cw, ch = _hero_pixels(start)
        assets.append(
            _asset(
                asset_id=coloring_id,
                page=start,
                role="coloring_hero",
                prompt=coloring_prompt,
                width_px=cw,
                height_px=ch,
                crop_rules="Full live art box under the code-rendered header. Keep a 12px white pad. No baked type.",
                mission_id=mission_id,
                required_objects=list(coloring["required_objects"]),
            )
        )
        pages.append(
            _page_row(
                page=start,
                page_type="coloring",
                needs_ai_art=True,
                asset_ids=[coloring_id],
                mission_id=mission_id,
            )
        )

        search_page = start + 1
        bg_id = f"{mission_id}_search_background"
        names = [str(target["name"]) for target in search["targets"]]
        sw, sh = _search_pixels(search_page)
        bg_prompt = _prompt(
            scene=str(search["visual_prompt"]),
            role="search_background",
            extra=(
                "Generate the environment only. Do not include any of these hunt targets: "
                f"{', '.join(names)}. Environment clutter is allowed if it cannot be mistaken "
                "for those eight objects."
            ),
            cast_line="No hunt-target objects. Recurring cast may appear as tiny distant figures without holding a hunt object.",
        )
        assets.append(
            _asset(
                asset_id=bg_id,
                page=search_page,
                role="search_background",
                prompt=bg_prompt,
                width_px=sw,
                height_px=sh,
                crop_rules="Fill the search scene rectangle above the code-rendered legend. Keep a 16px edge pad for target safety.",
                mission_id=mission_id,
                required_objects=["search_background"],
                excluded_targets=names,
            )
        )
        search_ids = [bg_id]
        for target in search["targets"]:
            name = str(target["name"])
            target_id = f"{mission_id}_target_{name}"
            scene = TARGET_SCENES[name]
            target_prompt = _prompt(
                scene=(
                    f"Single transparent-background coloring-book icon of a {scene}. "
                    "Centered, closed outline, no environment, no cast, no shadow block."
                ),
                role="search_target",
                extra="RGBA PNG with true transparent background. One object only.",
                cast_line="No recurring characters.",
            )
            assets.append(
                _asset(
                    asset_id=target_id,
                    page=search_page,
                    role="search_target",
                    prompt=target_prompt,
                    width_px=TARGET_PX,
                    height_px=TARGET_PX,
                    crop_rules="Keep a 8% transparent pad. Object must remain recognizable at 7-14% of scene width.",
                    mission_id=mission_id,
                    target_name=name,
                    required_objects=[name],
                )
            )
            search_ids.append(target_id)
        pages.append(
            _page_row(
                page=search_page,
                page_type="search_find",
                needs_ai_art=True,
                asset_ids=search_ids,
                mission_id=mission_id,
            )
        )

        maze_page = start + 2
        maze_id = f"{mission_id}_maze_scene"
        mw, mh = _hero_pixels(maze_page)
        maze_prompt = _prompt(
            scene=str(maze["visual_prompt"]),
            role="maze_scene",
            extra=(
                "Reserve a large empty white rectangle in the center 64% width by 48% height "
                "for a code-drawn maze. Do not draw maze walls, hedges-as-grid, arrows, or "
                "start/finish lettering. Story start and finish objects may sit outside that rectangle."
            ),
            cast_line=_cast_line(cast_ids[:1], bible),
        )
        assets.append(
            _asset(
                asset_id=maze_id,
                page=maze_page,
                role="maze_scene",
                prompt=maze_prompt,
                width_px=mw,
                height_px=mh,
                crop_rules="Full live art box. Center rectangle must stay empty white so maze walls remain readable.",
                mission_id=mission_id,
                required_objects=list(maze["required_objects"]),
            )
        )
        pages.append(
            _page_row(
                page=maze_page,
                page_type="maze",
                needs_ai_art=True,
                asset_ids=[maze_id],
                mission_id=mission_id,
            )
        )

        faith_page = start + 3
        frame_id = f"{mission_id}_faith_frame"
        fw, fh = _hero_pixels(faith_page)
        faith_prompt = _prompt(
            scene=str(faith["visual_prompt"]),
            role="faith_frame",
            extra=(
                "Editorial worksheet frame with a large empty drawing area. Do not draw "
                "choice cards, checkboxes, labels, or prayer ribbons with words. Leave open "
                "white panels for code-rendered interaction."
            ),
            cast_line="No required figures inside the drawing area.",
        )
        assets.append(
            _asset(
                asset_id=frame_id,
                page=faith_page,
                role="faith_frame",
                prompt=faith_prompt,
                width_px=fw,
                height_px=fh,
                crop_rules="Frame the live box. Keep the inner drawing area empty and at least 10 square inches after layout.",
                mission_id=mission_id,
                required_objects=["drawing_area"],
            )
        )
        faith_ids = [frame_id]
        for choice in faith["choices"]:
            icon = str(choice["icon"])
            choice_id = f"{mission_id}_faith_{icon}"
            icon_scene = FAITH_ICON_SCENES[icon]
            choice_prompt = _prompt(
                scene=f"Square transparent coloring-book choice icon: {icon_scene}.",
                role="faith_choice",
                extra="One pictogram. No captions. Closed shapes sized for a 1.2 inch card.",
                cast_line=_cast_line(["mira_bright"] if "child" in icon_scene else [], bible)
                if "child" in icon_scene
                else "Optional tiny Bright Hearts children only when the pictogram needs a figure.",
            )
            assets.append(
                _asset(
                    asset_id=choice_id,
                    page=faith_page,
                    role="faith_choice",
                    prompt=choice_prompt,
                    width_px=FAITH_ICON_PX,
                    height_px=FAITH_ICON_PX,
                    crop_rules="Centered icon with 10% transparent pad. Code places it on the choice card.",
                    mission_id=mission_id,
                    choice_icon=icon,
                    required_objects=[icon],
                )
            )
            faith_ids.append(choice_id)
        pages.append(
            _page_row(
                page=faith_page,
                page_type="faith_interaction",
                needs_ai_art=True,
                asset_ids=faith_ids,
                mission_id=mission_id,
            )
        )

    for page in book_pages:
        number = int(page["page"])
        if number < 37:
            continue
        if page.get("type") == "answer_key":
            pages.append(
                _page_row(
                    page=number,
                    page_type="answer_key",
                    needs_ai_art=False,
                    asset_ids=[],
                    mission_id=page.get("mission_id"),
                    reuses=list(page.get("answers_activity_pages") or []),
                )
            )
            continue
        spec = BACK_SPECS[number]
        width, height = _hero_pixels(number) if spec["role"] in {"certificate_frame", "closing_lockup"} else (SPOT_PX, 900)
        prompt = _prompt(
            scene=spec["scene"],
            role=spec["role"],
            extra="Leave open white regions for code-rendered writing lines.",
            cast_line=_cast_line(spec["cast"], bible),
        )
        asset_id = f"p{number:02d}_{spec['role']}"
        assets.append(
            _asset(
                asset_id=asset_id,
                page=number,
                role=spec["role"],
                prompt=prompt,
                width_px=width,
                height_px=height,
                crop_rules="Place in the live safety box. Code owns names, dates, and prompts.",
            )
        )
        pages.append(
            _page_row(
                page=number,
                page_type=str(page["type"]),
                needs_ai_art=True,
                asset_ids=[asset_id],
            )
        )

    pages.sort(key=lambda item: int(item["page"]))
    return {
        "book_id": "bright_hearts_fall_01",
        "art_bible_version": ART_BIBLE_VERSION,
        "prompt_version": PROMPT_VERSION,
        "character_bible_version": CHARACTER_BIBLE_VERSION,
        "paid_generation_authorized": False,
        "pages": pages,
        "assets": assets,
    }


def prompt_text_violations(asset: dict[str, Any], *, missions: list[dict[str, Any]] | None = None) -> list[str]:
    prompt = str(asset.get("prompt") or "")
    failures: list[str] = []
    lowered = prompt.lower()
    for snippet in FORBIDDEN_PROMPT_SNIPPETS:
        if snippet.lower() in lowered:
            failures.append(f"{asset.get('asset_id')}: prompt contains forbidden snippet {snippet!r}")
    missions = missions or load_mission_records()
    for mission in missions:
        for page in mission["pages"]:
            instruction = str(page.get("child_instruction") or "").strip()
            if instruction and instruction in prompt:
                failures.append(f"{asset.get('asset_id')}: prompt contains child instruction text")
            title = str(page.get("title") or "").strip()
            if title and len(title) > 8 and title in prompt:
                failures.append(f"{asset.get('asset_id')}: prompt contains page title {title!r}")
            prayer = str(page.get("prayer") or "").strip()
            if prayer and prayer in prompt:
                failures.append(f"{asset.get('asset_id')}: prompt contains prayer text")
    return failures


def role_counts(manifest: dict[str, Any] | None = None) -> dict[str, int]:
    record = manifest or load_production_manifest()
    counts: dict[str, int] = {}
    for asset in record["assets"]:
        role = str(asset["role"])
        counts[role] = counts.get(role, 0) + 1
    return dict(sorted(counts.items()))


def load_production_manifest(path=None) -> dict[str, Any]:
    target = path or PRODUCTION_ASSETS
    return json.loads(target.read_text(encoding="utf-8"))


def write_production_manifest(manifest: dict[str, Any] | None = None, path=None):
    destination = path or PRODUCTION_ASSETS
    payload = manifest or build_production_manifest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return destination


def production_manifest_errors(manifest: dict[str, Any] | None = None) -> list[str]:
    record = manifest if manifest is not None else load_production_manifest()
    errors = validate_instance(
        record, SCHEMA_DIR / "production_assets.schema.json", label="production_assets"
    )
    rebuilt = build_production_manifest()
    if record.get("assets") != rebuilt.get("assets") or record.get("pages") != rebuilt.get("pages"):
        errors.append("committed production_assets.json does not match the generator")
    if len(record.get("pages") or []) != TARGET_PAGE_COUNT:
        errors.append("production manifest must describe 48 pages")
    counts = role_counts(record)
    expected = {
        "title_lockup": 1,
        "welcome_spot": 1,
        "missions_map": 1,
        "parent_letter": 1,
        "coloring_hero": 8,
        "search_background": 8,
        "search_target": 64,
        "maze_scene": 8,
        "faith_frame": 8,
        "faith_choice": 32,
        "bonus_activity": 2,
        "certificate_frame": 1,
        "closing_lockup": 1,
    }
    if counts != expected:
        errors.append(f"production role counts {counts} != {expected}")
    ai_pages = [page for page in record["pages"] if page["needs_ai_art"]]
    code_pages = [page for page in record["pages"] if not page["needs_ai_art"]]
    if len(code_pages) != 8:
        errors.append(f"expected 8 code-only answer-key pages, got {len(code_pages)}")
    if len(ai_pages) != 40:
        errors.append(f"expected 40 AI-art pages, got {len(ai_pages)}")
    if any(asset.get("accepted") for asset in record["assets"]):
        errors.append("no production asset may be marked accepted until human visual review PASSES")
    if record.get("paid_generation_authorized") is not False:
        errors.append("paid_generation_authorized must stay false in this pass")
    ids = [asset["asset_id"] for asset in record["assets"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate production asset_id values")
    for asset in record["assets"]:
        errors.extend(prompt_text_violations(asset))
        if asset.get("status") != "pending":
            errors.append(f"{asset['asset_id']} status must remain pending until accepted artwork exists")
        if int(asset.get("width_px") or 0) < 512 or int(asset.get("height_px") or 0) < 512:
            errors.append(f"{asset['asset_id']} is below the 512px generation floor")
        if asset.get("art_bible_version") != ART_BIBLE_VERSION:
            errors.append(f"{asset['asset_id']} art_bible_version mismatch")
    return errors


def validate_production_assets_file() -> list[str]:
    errors = []
    errors.extend(
        validate_file(
            PRODUCTION_ASSETS,
            SCHEMA_DIR / "production_assets.schema.json",
            label="production_assets",
        )
    )
    if PRODUCTION_ASSETS.is_file():
        errors.extend(production_manifest_errors())
    else:
        errors.append("missing production_assets.json")
    return errors


if __name__ == "__main__":
    path = write_production_manifest()
    payload = load_production_manifest(path)
    print(json.dumps({"path": str(path), "assets": len(payload["assets"]), "roles": role_counts(payload)}, indent=2))
