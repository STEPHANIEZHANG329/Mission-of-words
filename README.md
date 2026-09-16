# Mission-of-words

Bright Hearts publishing production lab.

Current scope: V1 control plane on the Phase 0 4-page prototype. GitHub is the only orchestration layer. Paid image generation, merge, and KDP publishing stay closed.

- ChatGPT files work through `.github/ISSUE_TEMPLATE/task-packet.md`
- Cursor implements against this repository
- CI builds the deterministic 4-page PDF, writes `output/qa_report.json`, and fails if `paid_image_calls != 0`
- `src/mission_of_words/image_client.py` is dry-run only and refuses network generation
