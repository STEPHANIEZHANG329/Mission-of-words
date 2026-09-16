import json

import pytest

from mission_of_words import paid_images
from mission_of_words.asset_ledger import billed_asset_ids, load_ledger, remaining_calls
from mission_of_words.generate_assets import generate_planned
from mission_of_words.paid_images import CONFIRM_PHRASE, PaidImageError
from mission_of_words.paths import ROOT


def test_committed_ledger_counts_lost_run_against_the_cap():
    ledger = load_ledger()
    assert ledger["paid_image_calls"] == 18
    assert remaining_calls(ledger) == 0
    billed = billed_asset_ids(ledger)
    assert "cast_reference_sheet" in billed
    assert "cover_front" in billed
    assert "mission_06_hero" in billed
    assert len(billed) == 18
    statuses = {row["status"] for row in ledger["assets"]}
    assert statuses == {"lost_ephemeral"}


def test_generate_skips_billed_assets_without_files_and_does_not_call_network(monkeypatch, tmp_path):
    monkeypatch.setenv("ALLOW_PAID_IMAGE_CALLS", "1")
    monkeypatch.setenv("GPT2", "must-not-be-used")
    monkeypatch.setenv("BRIGHT_HEARTS_CONFIRM_PAID_GENERATION", CONFIRM_PHRASE)

    def boom(*_args, **_kwargs):
        raise AssertionError("network opened")

    monkeypatch.setattr(paid_images, "_post", boom)
    monkeypatch.setattr(paid_images, "generate_png", boom)

    def authorized(*, confirm=None):
        return True, "authorized"

    monkeypatch.setattr("mission_of_words.generate_assets.generation_authorized", authorized)
    monkeypatch.setattr("mission_of_words.generate_assets.generate_png", boom)
    monkeypatch.setattr("mission_of_words.generate_assets.write_prompt_packets", lambda path=None: [])

    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(
        json.dumps(
            {
                "kind": "bright_hearts_asset_ledger",
                "max_paid_image_calls": 24,
                "paid_image_calls": 18,
                "estimated_spend_usd": 3.6,
                    "assets": [
                        {"asset_id": row["asset_id"], "paid_call": True, "status": "lost_ephemeral"}
                        for row in json.loads(
                            (ROOT / "ops" / "asset_ledger.json").read_text()
                        )["assets"]
                    ],
            }
        )
    )
    summary = generate_planned(
        confirm=CONFIRM_PHRASE,
        ledger_path=ledger_path,
        raw_dir=tmp_path / "raw",
        accepted_dir=tmp_path / "accepted",
    )
    assert summary["generated"] == []
    assert summary["new_paid_calls"] == 0
    assert summary["paid_image_calls"] == 18
    assert summary["remaining_calls"] == 0
    assert len(summary["skipped"]) == 18
    assert len(summary["missing_after_paid_call"]) == 18
    assert "Do not regenerate" in summary["blocker"]


def test_generate_refuses_when_unauthorized_even_if_ledger_has_room(monkeypatch, tmp_path):
    monkeypatch.delenv("ALLOW_PAID_IMAGE_CALLS", raising=False)
    monkeypatch.setenv("GPT2", "must-not-be-used")
    with pytest.raises(PaidImageError):
        generate_planned(confirm=CONFIRM_PHRASE, ledger_path=tmp_path / "missing.json")
