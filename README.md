# Mission-of-words

Bright Hearts publishing production lab.

Current scope: V1 control plane on the Phase 0 4-page prototype. GitHub is the only orchestration layer. Paid image generation, merge, and KDP publishing stay closed.

- ChatGPT files work through `.github/ISSUE_TEMPLATE/task-packet.md`
- Cursor implements against this repository
- CI builds the deterministic 4-page PDF, writes `output/qa_report.json`, and fails if `paid_image_calls != 0`
- `technical_pass` is the factory/PDF gate. `prototype_pass` / `production_pass` / `pass` stay false while art is `placeholder_only` or visual QA evidence is missing
- `src/mission_of_words/image_client.py` is dry-run only and refuses network generation
