from llk.openai_images import calls_used
from llk.preflight import run_preflight


def test_preflight_report_is_green_without_network():
    report = run_preflight()
    assert report["ok"] is True
    assert report["pages"] == 48
    assert report["planned_paid_assets"] <= 48
    assert report["paid_call_cap"] == 48


def test_ledger_starts_empty_in_this_checkout():
    # Factory checkout must not already owe paid calls.
    assert calls_used() == 0
