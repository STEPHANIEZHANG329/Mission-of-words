"""Exact prompt packets for the bounded Phase C GPT2 run.

18 planned images: 1 cast sheet, 8 heroes, 8 search backgrounds, 1 cover.
Repair slots are separate and counted against the same 24-call cap.
"""

from __future__ import annotations

import json
from typing import Any

from mission_of_words.book_manifest import load_mission_records
from mission_of_words.paths import CONTENT_DIR, ROOT

ART_BIBLE = CONTENT_DIR / "art_bible.json"

NO_TEXT = (
    "ABSOLUTE RULE: do not draw any letters, numbers, words, titles, captions, "
    "Bible verses, signs, logos, name tags, book text, or watermarks. Blank "
    "pages, blank lanterns, blank collar tags, blank banners. All final text "
    "will be added later by layout code."
)

STYLE = (
    "Commercial US children's coloring and activity book plate. Pure black "
    "line art on white. Thick clean outlines. Large easy-to-color shapes. "
    "Coherent single scene, not a collage. Cute but not babyish, ages 5-8. "
    "No gray wash, no photorealism, no 3D render, no anime, no horror, no text."
)


def load_art_bible() -> dict[str, Any]:
    return json.loads(ART_BIBLE.read_text(encoding="utf-8"))


def cast_block(bible: dict[str, Any] | None = None) -> str:
    bible = bible or load_art_bible()
    lines = ["Recurring cast, keep them identical in every picture:"]
    for member in bible["cast"]:
        lines.append(f"- {member['name']}: {member['look']}")
    return "\n".join(lines)


def _packet(asset_id: str, role: str, prompt: str, *, model: str, mission_id: str | None = None) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "role": role,
        "mission_id": mission_id,
        "model": model,
        "quality": "high",
        "size": "1664x2160",
        "prompt": prompt,
        "status": "pending",
        "max_attempts": 1,
    }


def planned_packets() -> list[dict[str, Any]]:
    bible = load_art_bible()
    cast = cast_block(bible)
    packets = [
        _packet(
            "cast_reference_sheet",
            "cast_reference",
            (
                f"{STYLE}\n{NO_TEXT}\n{cast}\n"
                "Full-body character reference sheet: Mira, Eli, Joy, Caleb, and Pip the dog "
                "standing in a loose row on a simple autumn ground, facing the viewer, "
                "white background, even spacing, no props with writing, no panel labels. "
                "Each child distinct. Pip sits at their feet."
            ),
            model="gpt-image-2.5-sunburst",
        )
    ]
    missions = load_mission_records()
    hero_extras = {
        "mission_01": "Church fall festival at dusk, intact steeple cross, string lights, pumpkins, leaves, welcome table, Mira and Eli carrying lanterns with no writing, Joy and Caleb nearby, Pip at their feet.",
        "mission_02": "Evening orchard: setting sun, rising moon, stars, apple trees, a path, Caleb looking up, Mira pointing at the sky, Pip sitting, no writing on anything.",
        "mission_03": "Harvest wagon of wheat and corn, barn, family including all four children, a simple hymn book shown closed with a blank cover, pumpkins, Pip, not a church festival.",
        "mission_04": "Child (Eli) walking an autumn woods path toward a warmly lit porch, tall trees, fallen leaves, a small handheld light, Mira waiting on the porch, Pip beside Eli. Do not depict God as a person.",
        "mission_05": "Mira and Joy on a neighbor porch handing over a basket of apples and a loaf, an older neighbor at the door, jars on the step, Eli and Caleb and Pip nearby. Not a church festival.",
        "mission_06": "Fall-festival game booth, ring-toss, cider cups, Mira and Eli waving lonely Joy over to an extra empty chair, Caleb at the booth, Pip. Not the church-and-lanterns scene.",
        "mission_07": "Autumn hillside, creek, oak trees, a deer at the water, birds, Caleb sitting on a rock looking out, Mira Eli Joy and Pip nearby. Not an orchard of sun and moon.",
        "mission_08": "Family table with a simple autumn meal, extra chair being pulled in, clasped hands before eating, bread basket, window with falling leaves, all four children and Pip. Not a harvest wagon scene.",
    }
    search_extras = {
        "mission_01": "Festival grounds background with booths, trees, pumpkins in the distance, string lights. Do NOT include a lantern, pumpkin close-up as a hunt object, apple, leaf icon, acorn, scarf, basket, or Bible.",
        "mission_02": "Dusk orchard background with trees and sky. Do NOT include a sun disk, crescent moon, star, cloud icon, sundial, hourglass, sparrow, or a single highlighted season leaf.",
        "mission_03": "Barn-yard background. Do NOT include a wheat sheaf, corn cob, loaf, pitcher, pie, hymn book, heart, or thank-you card.",
        "mission_04": "Woods-path background. Do NOT include a hiking boot, walking stick, small lantern, map, compass, owl, blanket, or badge.",
        "mission_05": "Porch-and-yard background. Do NOT include an extra apple, loaf, soup pot, empty bowl, pair of gloves, jar of jam, note card, or wagon.",
        "mission_06": "Festival-booth background. Do NOT include a ticket, cider cup, kind note, extra chair, smile badge, bandage, pretzel, or game ring.",
        "mission_07": "Hillside-and-creek background. Do NOT include an oak leaf, pinecone, deer, fish, mushroom, bird nest, pebble, or ladybug as isolated hunt objects.",
        "mission_08": "Dining-room background with a table. Do NOT include a plate, cup, napkin, chair, bread basket, candle, place card, or serving spoon as isolated hunt objects.",
    }
    for mission in missions:
        mid = mission["id"]
        coloring = mission["pages"][0]
        search = mission["pages"][1]
        packets.append(
            _packet(
                f"{mid}_hero",
                "coloring_hero",
                (
                    f"{STYLE}\n{NO_TEXT}\n{cast}\n"
                    f"Portrait coloring page scene for '{mission['title']}'. "
                    f"{hero_extras[mid]} {coloring['visual_prompt']} "
                    "Fill the frame with one integrated scene. Leave a little breathing room at the top "
                    "because layout code will add the title later. No text."
                ),
                model="gpt-image-2.5-flare",
                mission_id=mid,
            )
        )
        excluded = ", ".join(target["name"] for target in search["targets"])
        packets.append(
            _packet(
                f"{mid}_search_background",
                "search_background",
                (
                    f"{STYLE}\n{NO_TEXT}\n"
                    "Dense but readable hidden-object BACKGROUND ONLY for ages 5-8. "
                    "Do not draw the children as the focus; small distant figures are ok if they are not holding hunt items. "
                    f"{search_extras[mid]} {search['visual_prompt']} "
                    f"Do not draw these hunt targets at all: {excluded}. "
                    "Busy autumn environment, still readable, no text."
                ),
                model="gpt-image-2.5-flare",
                mission_id=mid,
            )
        )
    packets.append(
        _packet(
            "cover_front",
            "cover_front",
            (
                "Full-color children's paperback cover illustration, autumn Christian family activity book mood, "
                "warm daylight, four children (Mira, Eli, Joy, Caleb) and Pip the dog at a fall festival with lanterns, "
                "pumpkins, a small church in the distance with an intact steeple cross, harvest baskets. "
                f"{cast_block(bible)} "
                "NO TEXT, no title, no author name, no Bible verse, no logos. Leave a calm sky area in the upper third "
                "so layout code can place the title later. Painting-and-ink storybook color, not photoreal."
            ),
            model="gpt-image-2.5-sunburst",
        )
    )
    return packets


def write_prompt_packets(path=None) -> list[dict[str, Any]]:
    packets = planned_packets()
    dest = path or (ROOT / "content" / "books" / "bright_hearts_fall_01" / "prompt_packets.json")
    dest.write_text(
        json.dumps(
            {
                "max_paid_image_calls": 24,
                "planned_count": len(packets),
                "repair_slots": 6,
                "packets": packets,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return packets
