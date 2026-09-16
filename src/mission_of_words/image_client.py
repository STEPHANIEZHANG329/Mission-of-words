"""DRY-RUN ONLY image client.

This module never opens a network connection, never reads image-API secrets,
and never increments a paid-call counter. A future owner-approved GitHub
Environment gate must be implemented before any generate HTTP call is added.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from mission_of_words.budget import BudgetError, assert_paid_call_forbidden

# Hard closed. Flipping this is not enough: a protected paid-image workflow
# and owner-edited budget must also exist before generate() may call a vendor.
PAID_GENERATION_GATE_IMPLEMENTED = False
DRY_RUN = True

_PAID_IMAGE_CALLS = 0


class PaidGenerationDisabled(RuntimeError):
    """Raised instead of performing a paid image API call."""


def paid_call_count() -> int:
    return _PAID_IMAGE_CALLS


def dry_run_info() -> dict[str, Any]:
    return {
        "mode": "dry-run",
        "dry_run": DRY_RUN,
        "paid_generation_gate_implemented": PAID_GENERATION_GATE_IMPLEMENTED,
        "network_allowed": False,
        "paid_image_calls": paid_call_count(),
    }


def request_id_for(*, model: str, prompt: str, size: str, role: str, seed: int) -> str:
    payload = json.dumps(
        {"model": model, "prompt": prompt, "role": role, "seed": seed, "size": size},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_image(
    *,
    prompt: str,
    role: str,
    request_id: str | None = None,
    model: str = "gpt-image-2",
    size: str = "1024x1024",
    seed: int = 0,
    estimated_usd: float = 0.0,
) -> dict[str, Any]:
    """Refuse generation. Does not touch the network."""
    _ = (prompt, role, request_id, model, size, seed)
    try:
        assert_paid_call_forbidden(
            estimated_usd=estimated_usd,
            gate_implemented=PAID_GENERATION_GATE_IMPLEMENTED,
        )
    except BudgetError as exc:
        raise PaidGenerationDisabled(str(exc)) from exc
    raise PaidGenerationDisabled(
        "Paid image generation is disabled. image_client is DRY-RUN ONLY. "
        "No network request was sent."
    )
