"""Repository locations for the Bright Hearts control plane."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANON_DIR = ROOT / "canon"
CONTENT_DIR = ROOT / "content"
SCHEMA_DIR = CONTENT_DIR / "schemas"
BOOK_RECORD = CONTENT_DIR / "books" / "bright_hearts_fall_01" / "book.json"
MISSION_SPEC = CONTENT_DIR / "mission_01.json"
ASSETS_DIR = ROOT / "assets"
OPS_DIR = ROOT / "ops"
BUDGET_PATH = OPS_DIR / "budget.json"
LEDGER_PATH = OPS_DIR / "ledger.jsonl"
TASK_PACKET_SCHEMA = OPS_DIR / "task-packet.schema.json"
OUTPUT_DIR = ROOT / "output"
