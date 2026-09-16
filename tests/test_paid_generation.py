import inspect
import os

import pytest

from mission_of_words import paid_generation
from mission_of_words.image_client import paid_call_count
from mission_of_words.paid_generation import (
    CONFIRM_PHRASE,
    PaidGenerationRefused,
    run_manual_generation,
    workflow_gates,
)


def test_manual_workflow_is_disabled_by_default():
    reasons = workflow_gates()
    assert reasons
    assert paid_call_count() == 0


def test_manual_generation_refuses_even_with_env(monkeypatch):
    monkeypatch.setenv("ALLOW_PAID_IMAGE_CALLS", "1")
    with pytest.raises(PaidGenerationRefused, match="No network call was made"):
        run_manual_generation(
            asset_ids=["p01_title_lockup"],
            approved_budget_usd=25,
            call_cap=10,
            confirm_phrase=CONFIRM_PHRASE,
        )
    assert paid_call_count() == 0


def test_paid_generation_source_has_no_vendor_http():
    source = inspect.getsource(paid_generation)
    for needle in ("urllib", "requests", "httpx", "openai", "http.client", "aiohttp"):
        assert needle not in source
    assert "GPT2" not in source


def test_cli_refuses(monkeypatch):
    monkeypatch.delenv("ALLOW_PAID_IMAGE_CALLS", raising=False)
    assert paid_generation.main(["--approved-budget-usd", "0", "--call-cap", "0"]) == 2
    assert os.environ.get("ALLOW_PAID_IMAGE_CALLS") in {None, ""}
