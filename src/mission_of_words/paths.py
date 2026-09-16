"""Repository locations for the Bright Hearts control plane."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANON_DIR = ROOT / "canon"
CONTENT_DIR = ROOT / "content"
SCHEMA_DIR = CONTENT_DIR / "schemas"
BOOK_DIR = CONTENT_DIR / "books" / "bright_hearts_fall_01"
BOOK_RECORD = BOOK_DIR / "book.json"
BOOK_MANIFEST = BOOK_DIR / "book_manifest.json"
PRODUCTION_ASSETS = BOOK_DIR / "production_assets.json"
FRONT_MATTER = BOOK_DIR / "front_matter.json"
BACK_MATTER = BOOK_DIR / "back_matter.json"
ART_BIBLE_MD = CONTENT_DIR / "art_bible.md"
ART_BIBLE_JSON = CONTENT_DIR / "art_bible.json"
MISSIONS_DIR = CONTENT_DIR / "missions"
MISSION_SPEC = CONTENT_DIR / "mission_01.json"
ASSETS_DIR = ROOT / "assets"
OPS_DIR = ROOT / "ops"
BUDGET_PATH = OPS_DIR / "budget.json"
LEDGER_PATH = OPS_DIR / "ledger.jsonl"
TASK_PACKET_SCHEMA = OPS_DIR / "task-packet.schema.json"
OUTPUT_DIR = ROOT / "output"
