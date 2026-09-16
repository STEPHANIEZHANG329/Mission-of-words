# Mission-of-words

Bright Hearts publishing production lab.

Current authorized work: **Phase A** of Issue #6 — 48-page full-book blueprint, source-locked canon, schemas, and fail-closed QA. Paid image generation, merge, KDP publishing, and `production_pass` stay closed.

The approved 4-page Shine Your Light prototype remains the quality floor. It is not the 48-page book.

- Models draw; code decides. Final page text is rendered by code.
- Eight missions are source-locked to public-domain 1769 KJV short quotations. Child paraphrase is a separate field.
- Search & Find answer keys must be generated from the compositor manifest. Maze keys must come from the unique path.
- `technical_pass` and `production_pass` are separate. Phase A can earn `blueprint_pass` only.
- `paid_image_calls` must remain 0.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m mission_of_words.evaluate_full_book
PYTHONPATH=src python -m mission_of_words.build_sample
```
