# Mission-of-words

Bright Hearts publishing production lab.

Current scope: rebuild and validate a **4-page** Shine Your Light prototype to the Issue #4 zero-defect gates. Paid image generation, merge, expansion past 4 pages, and KDP publishing stay closed.

- Models draw; code decides. This pass uses unpaid procedural line art so the layout/QA factory can be proven with `paid_image_calls == 0`.
- Canon lock: `canon/matthew_5_16.json` (KJV 1769, public domain) is the only scripture source. Child paraphrase is a separate field.
- Search & Find targets are independent assets. The answer key is generated from the compositor manifest.
- Maze path is a perfect maze (unique route), drawn as one garden scene.
- Visual preflight (`output/visual_qa.md`) is independent from technical `qa_report.json`.

```bash
pip install -r requirements.txt
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m mission_of_words.build_sample
```
