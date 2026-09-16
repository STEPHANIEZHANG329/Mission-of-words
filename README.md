# Mission-of-words

Bright Hearts publishing production lab.

Current authorized work: **Phase C** of Issue #6 — GPT2 production rebuild on the Phase B 48-page factory. Ordinary PR CI still makes **zero** paid image calls. A separate workflow uses `secrets.GPT2` with a hard cap of **24** paid image requests.

- Models draw; code decides. Final page text is rendered by code.
- Reusable templates wrap long mission titles, keep the mission badge from colliding with headings, and fail closed on bbox collisions.
- Search targets are code assets. Mazes are deterministic and unique. Faith in Action is code layout.
- `technical_pass` and `production_pass` stay separate. `production_pass` cannot become true while placeholders, collisions, or missing visual review remain.
- Paid spend is recorded in `ops/asset_ledger.json`. Already-billed asset ids are never requested again, even if PNG files were lost. Owner cap remains 24 (`remaining_calls` is 6 after run 35146572312).

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m mission_of_words.build_book
# Production candidate (uses accepted assets if present):
PYTHONPATH=src python -m mission_of_words.build_production
```
