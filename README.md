# Mission-of-words

Bright Hearts publishing production lab.

Current authorized work: **Phase C** of Issue #9 — Art Bible, production-asset/prompt manifest, accepted-asset ingestion, upgraded Search & Find difficulty, expanded visual QA, and a manual paid-generation workflow that stays **disabled by default**.

Build from the green Phase B 48-page technical proof. Do not return to rejected earlier PDFs.

- Models draw; code decides. Final page text is rendered by code.
- `technical_pass` can stay true for the marked NON-PRODUCTION 48-page proof.
- `production_pass` stays false until every required production asset is `accepted` and human visual review is PASS.
- Ordinary PR CI must make zero paid image calls.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m mission_of_words.build_book
PYTHONPATH=src python -m mission_of_words.build_production
```
