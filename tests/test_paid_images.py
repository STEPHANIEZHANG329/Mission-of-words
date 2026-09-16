import inspect

import pytest

from mission_of_words import paid_images
from mission_of_words.paid_images import (
    CONFIRM_PHRASE,
    MAX_PAID_CALLS,
    PaidImageError,
    generation_authorized,
    generate_png,
)


def test_generation_refuses_without_env_gate(monkeypatch):
    monkeypatch.delenv("ALLOW_PAID_IMAGE_CALLS", raising=False)
    monkeypatch.delenv("BRIGHT_HEARTS_CONFIRM_PAID_GENERATION", raising=False)
    monkeypatch.delenv("GPT2", raising=False)
    ok, reason = generation_authorized(confirm="nope")
    assert ok is False
    assert "ALLOW_PAID_IMAGE_CALLS" in reason


def test_generation_refuses_without_confirm_even_if_secret_present(monkeypatch):
    monkeypatch.setenv("ALLOW_PAID_IMAGE_CALLS", "1")
    monkeypatch.setenv("GPT2", "must-not-be-used")
    ok, reason = generation_authorized(confirm="wrong")
    assert ok is False
    assert "confirm" in reason


def test_generate_png_does_not_open_network_when_unauthorized(monkeypatch, tmp_path):
    monkeypatch.setenv("GPT2", "must-not-be-used")
    monkeypatch.delenv("ALLOW_PAID_IMAGE_CALLS", raising=False)

    def boom(*_args, **_kwargs):
        raise AssertionError("network opened")

    monkeypatch.setattr(paid_images, "_post", boom)
    with pytest.raises(PaidImageError, match="refused"):
        generate_png(
            prompt="draw a lantern with no text",
            dest=tmp_path / "x.png",
            asset_id="test",
            role="coloring_hero",
            remaining_calls=24,
        )


def test_owner_cap_is_24():
    assert MAX_PAID_CALLS == 24
    assert CONFIRM_PHRASE == "OWNER_PHASE_C_GPT2_REBUILD"


def test_paid_images_never_prints_secret_constant():
    source = inspect.getsource(paid_images)
    assert "sk-" not in source
    assert "print(os.environ.get(\"GPT2\"))" not in source
    assert "[REDACTED]" in source
