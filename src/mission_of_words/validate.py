"""Fail-closed JSON Schema validation for control-plane records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator
from jsonschema.exceptions import SchemaError as JsonSchemaError
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource

from mission_of_words.paths import (
    BOOK_RECORD,
    BUDGET_PATH,
    CANON_DIR,
    MISSION_SPEC,
    SCHEMA_DIR,
    TASK_PACKET_SCHEMA,
    VISUAL_QA_PATH,
)


class SchemaError(ValueError):
    """Raised when a control-plane record does not match its schema."""


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _registry_for(schema_dir: Path) -> Registry:
    registry = Registry()
    for sibling in schema_dir.glob("*.json"):
        contents = _load_json(sibling)
        if not isinstance(contents, dict) or "$schema" not in contents:
            continue
        resource = Resource.from_contents(contents)
        registry = registry.with_resource(sibling.name, resource)
        registry = registry.with_resource(sibling.as_uri(), resource)
        schema_id = contents.get("$id")
        if isinstance(schema_id, str) and schema_id:
            registry = registry.with_resource(schema_id, resource)
    return registry


def _validator(schema_path: Path) -> Draft7Validator:
    schema = _load_json(schema_path)
    return Draft7Validator(schema, registry=_registry_for(schema_path.parent))


def validate_instance(instance: Any, schema_path: Path, *, label: str) -> list[str]:
    if not schema_path.is_file():
        return [f"{label}: missing schema {schema_path}"]
    try:
        validator = _validator(schema_path)
    except (json.JSONDecodeError, JsonSchemaError, OSError) as exc:
        return [f"{label}: schema {schema_path.name} could not be loaded: {exc}"]
    try:
        validator.validate(instance)
    except ValidationError as exc:
        path = ".".join(str(part) for part in exc.path) or "$"
        return [f"{label}: {path}: {exc.message}"]
    return []


def validate_file(path: Path, schema_path: Path, *, label: str) -> list[str]:
    if not path.is_file():
        return [f"{label}: missing file {path}"]
    try:
        instance = _load_json(path)
    except json.JSONDecodeError as exc:
        return [f"{label}: invalid JSON in {path}: {exc}"]
    return validate_instance(instance, schema_path, label=label)


def validate_task_packet(packet: dict[str, Any]) -> list[str]:
    errors = validate_instance(packet, TASK_PACKET_SCHEMA, label="task-packet")
    if packet.get("paid_calls_allowed") is True:
        errors.append(
            "task-packet: paid_calls_allowed must be false until an owner-approved gate exists"
        )
    if int(packet.get("max_paid_calls") or 0) != 0:
        errors.append("task-packet: max_paid_calls must be 0 while paid generation is disabled")
    return errors


def validate_repo() -> list[str]:
    errors: list[str] = []
    errors.extend(validate_file(MISSION_SPEC, SCHEMA_DIR / "mission.schema.json", label="mission"))
    errors.extend(validate_file(BOOK_RECORD, SCHEMA_DIR / "book.schema.json", label="book"))
    errors.extend(
        validate_file(
            CANON_DIR / "matthew_5_16.json",
            SCHEMA_DIR / "canon.schema.json",
            label="canon",
        )
    )
    errors.extend(validate_file(BUDGET_PATH, SCHEMA_DIR / "budget.schema.json", label="budget"))
    errors.extend(
        validate_file(VISUAL_QA_PATH, SCHEMA_DIR / "visual_qa.schema.json", label="visual_qa")
    )
    if not TASK_PACKET_SCHEMA.is_file():
        errors.append("missing ops/task-packet.schema.json")
    else:
        try:
            schema = _load_json(TASK_PACKET_SCHEMA)
        except json.JSONDecodeError as exc:
            errors.append(f"task-packet schema is not valid JSON: {exc}")
        else:
            if not isinstance(schema, dict) or schema.get("type") != "object":
                errors.append("task-packet schema must describe an object")
            required = set(schema.get("required") or [])
            expected = {
                "request_id",
                "goal",
                "book_id",
                "mission_id",
                "paid_calls_allowed",
                "max_paid_calls",
                "acceptance_checks",
                "out_of_scope",
            }
            missing = expected - required
            if missing:
                errors.append(f"task-packet schema missing required keys: {sorted(missing)}")
    return errors
