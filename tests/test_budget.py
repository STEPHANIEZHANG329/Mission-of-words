import json
from pathlib import Path

from mission_of_words.budget import (
    BudgetError,
    append_ledger,
    assert_paid_call_forbidden,
    load_budget,
    paid_calls_disabled,
    read_ledger,
)
from mission_of_words.paths import BUDGET_PATH, LEDGER_PATH


def test_repo_budget_keeps_paid_calls_disabled():
    budget = load_budget()
    assert budget["paid_calls_enabled"] is False
    assert budget["allow_paid_image_calls"] is False
    assert budget["max_paid_calls"] == 0
    assert budget["max_usd"] == 0
    assert budget["spent_calls"] == 0
    assert budget["spent_usd"] == 0
    assert paid_calls_disabled(budget) is True
    assert BUDGET_PATH.is_file()


def test_assert_paid_call_forbidden_even_if_budget_file_is_opened():
    try:
        assert_paid_call_forbidden(estimated_usd=0.01, gate_implemented=False)
    except BudgetError as exc:
        assert "disabled" in str(exc).lower()
    else:
        raise AssertionError("expected BudgetError")


def test_ledger_is_append_only(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_ledger({"request_id": "a", "paid_call": False, "actor": "test"}, path=path)
    append_ledger({"request_id": "b", "paid_call": False, "actor": "test"}, path=path)
    rows = read_ledger(path)
    assert [row["request_id"] for row in rows] == ["a", "b"]
    original = path.read_text(encoding="utf-8")
    append_ledger({"request_id": "c", "paid_call": False, "actor": "test"}, path=path)
    assert path.read_text(encoding="utf-8").startswith(original)
    assert LEDGER_PATH.read_text(encoding="utf-8") == ""
