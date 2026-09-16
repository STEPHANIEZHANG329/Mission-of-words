# Mission-of-words

Clean rebuild of **Little Lampkeepers: Shine Your Light This Fall**, a 48-page KDP-ready Christian children's activity book.

Artwork is generated only through the repository secret `GPT2` calling the OpenAI image API. Code owns layout, mazes, Search & Find placement, answer keys, typography, and PDF export.

Preflight (no paid calls):

```
pip install -r requirements.txt
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m llk.preflight --before-paid
```

Paid production is the GitHub Actions workflow `kdp-production.yml`, triggered by `ops/AUTHORIZE_PAID_RUN`. Cap: 48 image API calls.
