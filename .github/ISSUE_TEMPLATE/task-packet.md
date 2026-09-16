---
name: Task Packet
about: Durable ChatGPT-to-Cursor handoff. Paid calls stay disabled unless Owner later approves a gate.
title: "[task-packet] "
labels:
  - task-packet
---

Paste **one JSON object** that matches `ops/task-packet.schema.json`.

Rules for this factory:

- `paid_calls_allowed` must be `false`
- `max_paid_calls` must be `0`
- Do not merge, publish, or call GPT2 / OpenAI image generation
- Cursor returns durable evidence (PR, CI URL, `qa_report.json`, `paid_image_calls`)

## Packet

```json
{
  "request_id": "replace-with-new-id",
  "goal": "Describe the smallest change Cursor should make",
  "book_id": "bright_hearts_fall_01",
  "mission_id": "mission_01",
  "allowed_files": [],
  "paid_calls_allowed": false,
  "max_paid_calls": 0,
  "acceptance_checks": [
    "pytest passes",
    "qa_report.json pass==true",
    "paid_image_calls==0"
  ],
  "out_of_scope": [
    "KDP upload",
    "paid image generation",
    "merge to main",
    "local ChatGPT"
  ]
}
```

## Notes for Cursor

- Keep production and publishing gates closed
- If CI is red, stop and report the specific failure
- Do not invent Bible facts; use `canon/` records only
