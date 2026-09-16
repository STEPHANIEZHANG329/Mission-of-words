# Bright Hearts Art Bible — Phase C

**Version:** `c1.0`  
**Book:** Bright Hearts: Shine Your Light This Fall  
**Trim:** 8.5 × 11 in portrait, black-and-white interior, 300 DPI effective raster minimum  
**Audience:** ages 5–8  
**Principle:** models draw; code decides. Final page text is never generated inside artwork.

This file is the human-readable visual contract. `content/art_bible.json` is the machine-readable twin. Every production prompt must hash against this version.

## Quality target

A polished US children's Christian fall activity/coloring book sold at retail: professional black-and-white line art, dense but readable full scenes, clear editorial hierarchy, warm storytelling, and strong child usability. Pages must look like a real book, not programmer placeholders or teacher worksheets.

## Global line-art rules

- Clean, confident black outlines on white. Closed, colorable shapes.
- Consistent stroke hierarchy: heavier outer contours, lighter interior detail.
- No muddy gray fills, photoreal shading, watercolor, sketch noise, or over-hatching.
- Large open coloring areas sized for ages 5–8. Premium scene detail is required; micro-detail that frustrates crayon work is forbidden.
- Friendly commercial children's-book proportions. Anatomy must be correct. Hands, eyes, limbs, and held objects must pass human visual QA.
- No logos, watermarks, copyrighted franchise characters, competitor-specific compositions, or copied page layouts.
- Do **not** render titles, instructions, scripture, labels, START/FINISH, answer-key marks, page numbers, or branding in the image. Code renders all of that.
- No generated signage or words inside artwork. If a book, hymn book, or Bible appears, it is a closed object with an intact cross or simple cover lines — never readable type.
- Prefer public-domain / original child-friendly visual storytelling. Do not bake copyrighted Bible translation text into pictures.

## Recurring cast (stable proportions, variable clothes)

Clothing and handheld props may change by mission. Head-to-body ratio, face language, eye set, and line style must stay coherent across the book.

- **Mira Bright** — girl, about seven. Shoulder-length bob with a side part, round friendly face, visible ears, simple nose, small closed-mouth smile or gentle open smile. Child proportions (head about one-fifth of height). Often the lantern-bearer.
- **Eli Bright** — boy, about six or seven. Short textured hair, same face language as Mira (sibling resemblance), slightly broader shoulders. Child proportions. Often holds a basket, map, or second lantern.
- **Pastor Grace** — adult woman, modest fall clothing, warm expression, correct adult proportions (not a giant child). Appears only when a scene needs a church/community adult.
- **Neighbor Han** — adult man, kind, correct adult proportions. Porch/share scenes.
- **Supporting child** — one extra child at most, clearly younger or the same age, never a copy of Mira/Eli's exact hair+outfit combo.

Maximum 3–5 meaningful human figures unless the story genuinely needs more. Prefer two focal children in the foreground.

## Page-type contracts

### Coloring / hero

One integrated scene, not scattered clip-art. Clear focal child/children in the foreground plus supporting church/fall environment. Strong foreground / midground / background depth. Include story objects that reinforce the mission. Preserve white/open regions for coloring. No generated words.

### Search & Find

Full lively background generated **without** the eight hunt targets. Targets are independent transparent assets placed by code. Background may contain environment clutter, but never a duplicate of a hunt target. No letters.

### Maze scene

Illustrated environment around a large empty white rectangle reserved for the code-drawn maze. Do not draw maze walls, letters, or START/FINISH. Scene art must not invade the reserved maze rectangle.

### Faith in Action

Clean editorial worksheet frame: illustrated border and a large empty drawing area. Choice icons are separate assets. No letters, no checkboxes (code draws those), no prayer text.

### Front and closing spots

Decorative line-art lockups and spots without any title lettering. Code sets the words.

## Human visual QA dimensions

Anatomy, line consistency, coloring usability, composition, text-in-artwork, prompt-to-art, asset integration, age suitability, and brand consistency must all PASS before `production_pass` can become true.
