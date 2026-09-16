from mission_of_words.validate import validate_repo, validate_task_packet


def test_control_plane_records_validate():
    assert validate_repo() == []


def test_valid_task_packet_is_accepted():
    packet = {
        "request_id": "req_v1_control_plane",
        "goal": "Keep paid generation disabled and preserve the 4-page prototype",
        "book_id": "bright_hearts_fall_01",
        "mission_id": "mission_01",
        "allowed_files": ["src/mission_of_words/qa.py", "tests/"],
        "paid_calls_allowed": False,
        "max_paid_calls": 0,
        "acceptance_checks": [
            "pytest passes",
            "qa_report.json pass==true",
            "paid_image_calls==0",
        ],
        "out_of_scope": ["KDP upload", "paid image generation", "merge to main"],
    }
    assert validate_task_packet(packet) == []


def test_task_packet_rejects_paid_calls():
    packet = {
        "request_id": "req_paid",
        "goal": "generate art",
        "book_id": "bright_hearts_fall_01",
        "mission_id": "mission_01",
        "paid_calls_allowed": True,
        "max_paid_calls": 3,
        "acceptance_checks": ["none"],
        "out_of_scope": [],
    }
    errors = validate_task_packet(packet)
    assert errors
    assert any("paid_calls_allowed" in item for item in errors)
