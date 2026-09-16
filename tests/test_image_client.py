import inspect

import pytest

from mission_of_words import image_client
from mission_of_words.image_client import (
    PAID_GENERATION_GATE_IMPLEMENTED,
    PaidGenerationDisabled,
    dry_run_info,
    generate_image,
    paid_call_count,
    request_id_for,
)


def test_dry_run_mode_is_closed():
    info = dry_run_info()
    assert info["mode"] == "dry-run"
    assert info["network_allowed"] is False
    assert info["paid_generation_gate_implemented"] is False
    assert PAID_GENERATION_GATE_IMPLEMENTED is False
    assert paid_call_count() == 0


def test_generate_image_refuses_without_network(monkeypatch):
    monkeypatch.setenv("GPT2", "must-not-be-used")
    monkeypatch.setenv("ALLOW_PAID_IMAGE_CALLS", "1")

    def boom(*_args, **_kwargs):
        raise AssertionError("network socket opened")

    monkeypatch.setattr("socket.socket", boom)
    with pytest.raises(PaidGenerationDisabled, match="No network call was made"):
        generate_image(prompt="draw a lantern", role="search_target")
    assert paid_call_count() == 0


def test_image_client_source_has_no_http_or_vendor_client():
    source = inspect.getsource(image_client)
    for needle in ("urllib", "requests", "httpx", "openai", "http.client", "aiohttp"):
        assert needle not in source
    assert "os.environ" not in source
    assert "GPT2" not in source


def test_request_id_is_stable():
    first = request_id_for(model="gpt-image-2", prompt="a", size="1024x1024", role="x", seed=1)
    second = request_id_for(model="gpt-image-2", prompt="a", size="1024x1024", role="x", seed=1)
    third = request_id_for(model="gpt-image-2", prompt="b", size="1024x1024", role="x", seed=1)
    assert first == second
    assert first != third
    assert len(first) == 64
