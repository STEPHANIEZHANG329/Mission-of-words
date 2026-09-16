from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
CONTENT = ROOT / "content"
MISSIONS = CONTENT / "missions"
CANON = ROOT / "canon"
FONTS = ROOT / "fonts"
ASSETS_GENERATED = ROOT / "assets" / "generated"
ASSETS_ACCEPTED = ROOT / "assets" / "accepted"
PROVENANCE = ROOT / "assets" / "provenance"
OUTPUT = ROOT / "output"
OPS = ROOT / "ops"
LEDGER = OPS / "ledger.jsonl"
BUDGET = OPS / "budget.json"


def ensure_dirs() -> None:
    for path in (ASSETS_GENERATED, ASSETS_ACCEPTED, PROVENANCE, OUTPUT, OPS):
        path.mkdir(parents=True, exist_ok=True)
