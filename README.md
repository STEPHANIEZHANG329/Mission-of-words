# Mission-of-words

Internal production lab for the **Little Lampkeepers** KDP interior (legacy repo/book ids may still say Bright Hearts).

Current authorized work: **Phase C** of Issue #6 — GPT2 production rebuild on the Phase B 48-page factory. Ordinary PR CI still makes **zero** paid image calls. The paid GPT2 workflow is **dispatch-only** and currently **Owner-stopped**.

- Consumer-facing title: `Little Lampkeepers: Shine Your Light This Fall`. Pages, cover, and listing copy must not display Bright Hearts.
- Models draw; code decides. Final page text is rendered by code.
- Paid spend is recorded in `ops/asset_ledger.json`. 18 calls from run 35146572312 are billed and lost. `remaining_calls` is 6 and cannot replace 18 files. Do not regenerate without a raised cap.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m mission_of_words.build_book
# Production candidate (uses accepted assets if present):
PYTHONPATH=src python -m mission_of_words.build_production
```
