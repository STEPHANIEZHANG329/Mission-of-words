from mission_of_words.budget import load_budget, paid_calls_disabled, read_ledger
from mission_of_words.full_book_qa import evaluate_full_book
from mission_of_words.image_client import PAID_GENERATION_GATE_IMPLEMENTED, paid_call_count
from mission_of_words.paths import LEDGER_PATH


def test_full_book_budget_accounting_stays_at_zero():
    budget = load_budget()
    assert paid_calls_disabled(budget) is True
    assert budget["spent_calls"] == 0
    assert budget["spent_usd"] == 0
    assert budget["max_paid_calls"] == 0
    assert budget["max_usd"] == 0
    assert PAID_GENERATION_GATE_IMPLEMENTED is False
    assert paid_call_count() == 0
    assert LEDGER_PATH.read_text(encoding="utf-8") == ""
    assert read_ledger() == []
    report = evaluate_full_book()
    assert report["paid_image_calls"] == 0
    assert report["estimated_spend_usd"] == 0
    assert report["paid_generation_gate_implemented"] is False
