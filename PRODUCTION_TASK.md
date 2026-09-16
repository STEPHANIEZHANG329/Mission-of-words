# FINAL PRODUCTION CONTRACT

Goal: build and deliver a finished 48-page KDP-ready interior PDF for **Little Lampkeepers: Shine Your Light This Fall**, plus matching KDP cover PDF.

## Non-negotiable product spec
- 48 interior pages exactly
- 8.5 x 11 in trim
- black-and-white interior
- 300 DPI raster assets where raster is used
- embedded fonts
- safe margins and gutter suitable for KDP
- no placeholder pages
- no technical proof labels
- no wireframes
- no procedural stick-figure art
- no empty boxes
- no worksheet-engineering aesthetic
- no owner-facing file until the full book is assembled

## Visual floor
Match the Owner-approved commercial examples: polished children's coloring-book line art, expressive recurring children, detailed but colorable church/fall environments, integrated activities, playful hierarchy, commercially publishable appearance.

## Production split
- Use repository secret `GPT2` for all paid image generation through the OpenAI image API.
- Do NOT substitute Codex, local procedural drawing, or placeholder graphics for final art.
- Generate image assets without text whenever practical; render titles, scripture references, instructions, page numbers, maze labels, and answer-key text in code to avoid image-text defects.
- Code owns layout, pagination, maze logic, search-and-find target placement, answers, PDF export, preflight, and KDP geometry.

## Content structure
Front matter + 8 missions + answer keys + back matter = exactly 48 pages.
Each mission should include a commercial mix of coloring, search & find, maze, and faith/reflection activity pages. Use public-domain/source-safe Bible wording or original child-friendly paraphrase + references; do not bulk quote copyrighted translations.

## Required final outputs
- `output/LittleLampkeepers_48Page_Interior_KDP.pdf`
- `output/LittleLampkeepers_Cover_KDP.pdf`
- `output/contact_sheet_all_pages.jpg`

## Acceptance
Do not stop at CI green. Do not report a proof as product. The job is complete only when the 48-page interior and cover exist and are visually inspected page-by-page for clipping, overlap, missing art, bad text, blank panels, unreadable answers, broken maze/search mechanics, and inconsistent style.
