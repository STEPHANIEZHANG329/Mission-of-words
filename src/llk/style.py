from __future__ import annotations

LINE_ART_BIBLE = (
    "Professional US children's coloring-book illustration for ages 5-8, "
    "commercially publishable KDP retail quality. Clean confident black ink outlines "
    "on pure white paper. No gray shading, no watercolor, no pencil grain, no photorealism, "
    "no cross-hatching, no screentones, no gradients. Large open colorable shapes with "
    "medium scene density, not micro-detail. Friendly commercial children's-book anatomy "
    "and proportions, expressive faces, correct hands and eyes. Warm Christian autumn "
    "storytelling. Recurring children: Mira, about 7, shoulder-length dark bob with a side "
    "part and a tiny maple-leaf hair clip, round cheeks, cardigan over a simple dress and "
    "boots; Eli, about 6 or 7, short textured dark hair, hoodie and sneakers, sibling "
    "resemblance to Mira. Optional adult: Pastor Grace, modest fall clothing, correct adult "
    "proportions. Maximum 3-5 people. Do not draw God as a person or cartoon. "
    "ABSOLUTELY NO TEXT, letters, numbers, captions, signs, speech bubbles, watermarks, "
    "signatures, logos, or readable writing on books. Books and Bibles are closed objects "
    "with a simple cover cross, never lettering. No copyrighted franchise characters."
)

COLOR_COVER_BIBLE = (
    "Full-color children's picture-book cover painting, polished commercial quality, "
    "warm autumn sunset golds, russet leaves, and lantern glow. Painterly but clear, "
    "not a coloring-book page. Mira and Eli in the foreground with glowing lanterns, "
    "a small white country church with an intact steeple cross, pumpkins and falling "
    "leaves, inviting and gentle. No text, letters, numbers, logos, or watermarks."
)

NO_TEXT = "Do not include any text, letters, numbers, or signage in the image."


def coloring_prompt(visual: str, required: list[str]) -> str:
    objects = ", ".join(required)
    return (
        f"{LINE_ART_BIBLE} Full-page portrait coloring scene, one integrated illustration "
        f"with clear foreground children, midground activity, and background place. "
        f"{visual} Required visible objects: {objects}. {NO_TEXT}"
    )


def search_background_prompt(visual: str, target_names: list[str]) -> str:
    banned = ", ".join(target_names)
    return (
        f"{LINE_ART_BIBLE} Full-page portrait Search-and-Find BACKGROUND only. "
        f"A lively fall scene with enough clutter to hide objects later, but DO NOT draw "
        f"any of these hunt targets: {banned}. No duplicate lookalikes of those targets. "
        f"{visual} Leave natural pockets of space in the lower two-thirds where small "
        f"objects could later be placed. {NO_TEXT}"
    )


def maze_scene_prompt(visual: str, required: list[str]) -> str:
    objects = ", ".join(required)
    return (
        f"{LINE_ART_BIBLE} Wide portrait coloring illustration for a maze page. "
        f"LEFT side: the START story object. RIGHT side: the FINISH story object. "
        f"CENTER: a large empty pure-white rounded rectangle occupying at least the middle "
        f"50 percent of the image, completely blank, no paths, no hedges drawn as a maze, "
        f"no walls, no people in the center. Decorative autumn environment around the "
        f"empty center. {visual} Required: {objects}. {NO_TEXT}"
    )


def faith_prompt(visual: str, choice_labels: list[str]) -> str:
    icons = "; ".join(choice_labels)
    return (
        f"{LINE_ART_BIBLE} Portrait faith-in-action worksheet illustration. "
        f"Top: a decorative illustrated banner with four small circular icon drawings "
        f"showing: {icons}. Bottom: one large empty white drawing rectangle with a simple "
        f"illustrated frame, empty inside for a child to draw. {visual} {NO_TEXT}"
    )


def title_prompt() -> str:
    return (
        f"{LINE_ART_BIBLE} Portrait title illustration with no lettering. Mira and Eli "
        f"stand in front of a small white church at a fall festival, each holding a glowing "
        f"lantern. Pumpkins, maple leaves, string lights on the church porch, intact steeple "
        f"cross, welcome table with apples. Rich but colorable scene, heroes in the foreground. "
        f"{NO_TEXT}"
    )


def welcome_prompt() -> str:
    return (
        f"{LINE_ART_BIBLE} Portrait welcome illustration. Mira and Eli waving, sitting on "
        f"a church-garden bench with a closed picture Bible, crayons, and a small lantern. "
        f"Autumn trees behind them. Friendly, uncluttered, large coloring areas. {NO_TEXT}"
    )


def map_prompt() -> str:
    return (
        f"{LINE_ART_BIBLE} Portrait illustrated story-map of a village in autumn: a winding "
        f"leafy path visiting eight distinct stations (church festival, orchard, barn, woods "
        f"porch, neighbor house, game booth, creek hillside, family table). Tiny Mira and Eli "
        f"walk the path. No labels. Station buildings are clear and colorable. {NO_TEXT}"
    )


def parent_prompt() -> str:
    return (
        f"{LINE_ART_BIBLE} Small gentle portrait vignette of a parent and two children "
        f"reading a closed Bible together on a couch with a window of falling leaves. "
        f"Lots of open white space around the vignette, as if it is a letterhead drawing. "
        f"{NO_TEXT}"
    )


def certificate_prompt() -> str:
    return (
        f"{LINE_ART_BIBLE} Portrait certificate frame only: leafy autumn wreath with lanterns, "
        f"maple leaves, wheat, and a small church silhouette at the top. Very large empty "
        f"white center for later typography. No lettering. {NO_TEXT}"
    )


def closing_prompt() -> str:
    return (
        f"{LINE_ART_BIBLE} Portrait closing scene: Mira and Eli walking away down a dusk "
        f"lane carrying lanterns, looking back with smiles, church and harvest moon behind "
        f"them. Hopeful, not sad. {NO_TEXT}"
    )


def gratitude_prompt() -> str:
    return (
        f"{LINE_ART_BIBLE} Portrait journal header illustration: an open blank journal, "
        f"crayons, a small lantern, apples, and leaves on a wooden table. Large empty space "
        f"in the lower half. {NO_TEXT}"
    )


def cover_prompt() -> str:
    return (
        f"{COLOR_COVER_BIBLE} Portrait cover painting filling the frame. Mira slightly left, "
        f"Eli slightly right, lantern light on their faces, church centered in the middle "
        f"distance, fall trees, pumpkins, golden hour. Leave a little calmer sky in the top "
        f"fifth for a title overlay, but do not draw any title. {NO_TEXT}"
    )


def target_sheet_prompt(names: list[str]) -> str:
    labeled = ", ".join(f"{i+1}:{n.replace('_', ' ')}" for i, n in enumerate(names))
    n = len(names)
    rows = 4
    cols = 4
    return (
        f"{LINE_ART_BIBLE} A strict {rows} by {cols} grid of {n} separate coloring-book icons "
        f"on a pure white background. Each cell contains exactly one object, centered, with "
        f"even padding, no overlapping cells, no extra doodles in the gutters. Equal cell "
        f"sizes. Objects: {labeled}. Do not render the numbers or names. Each icon is a "
        f"simple toy-like object with thick outlines, no people. {NO_TEXT}"
    )
