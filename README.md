# Mission-of-words

Bright Hearts publishing production lab.

Current authorized work: **Phase B** of Issue #6 — deterministic 48-page technical proof. Paid image generation, merge, KDP publishing, and `production_pass` stay closed.

The approved 4-page Shine Your Light prototype remains the quality floor. It is not the 48-page book.

- Models draw; code decides. Final page text is rendered by code.
- Eight missions are source-locked to public-domain 1769 KJV short quotations. Child paraphrase is a separate field.
- Search & Find answer keys must be generated from the compositor manifest. Maze keys must come from the unique path.
- `technical_pass` and `production_pass` are separate. Phase B can earn `technical_pass` only for a marked NON-PRODUCTION proof.
- `paid_image_calls` must remain 0.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m mission_of_words.build_book
```
