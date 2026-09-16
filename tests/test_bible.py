from copy import deepcopy
import json

from mission_of_words.bible import CanonError, bind_mission_canon, load_canon
from mission_of_words.paths import MISSION_SPEC


def test_matthew_5_16_is_source_locked():
    record = load_canon("matthew_5_16")
    assert record["reference"] == "Matthew 5:16"
    assert record["translation"] == "KJV"
    assert "Let your light so shine before men" in record["source_text"]
    assert "glorify your Father which is in heaven" in record["source_text"]
    assert record["child_paraphrase"] != record["source_text"]
    assert "pumpkin" not in record["source_text"].lower()
    assert "lantern" not in record["source_text"].lower()


def test_missing_canon_record_fails_closed(tmp_path):
    try:
        load_canon("not_a_real_verse", canon_dir=tmp_path)
    except CanonError as exc:
        assert "missing canon record" in str(exc)
    else:
        raise AssertionError("expected CanonError")


def test_empty_source_text_fails_closed(tmp_path):
    path = tmp_path / "matthew_5_16.json"
    path.write_text(
        json.dumps(
            {
                "canon_id": "matthew_5_16",
                "reference": "Matthew 5:16",
                "source_text": "   ",
            }
        ),
        encoding="utf-8",
    )
    try:
        load_canon("matthew_5_16", canon_dir=tmp_path)
    except CanonError as exc:
        assert "empty source_text" in str(exc)
    else:
        raise AssertionError("expected CanonError")


def test_mission_requires_matching_canon_id():
    spec = json.loads(MISSION_SPEC.read_text(encoding="utf-8"))
    canon = bind_mission_canon(spec)
    assert canon["canon_id"] == "matthew_5_16"
    spec["mission"]["scripture_reference"] = "John 3:16"
    try:
        bind_mission_canon(spec)
    except CanonError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("expected CanonError")


def test_mission_without_canon_id_fails():
    spec = deepcopy(json.loads(MISSION_SPEC.read_text(encoding="utf-8")))
    spec["mission"].pop("canon_id")
    try:
        bind_mission_canon(spec)
    except CanonError as exc:
        assert "missing canon_id" in str(exc)
    else:
        raise AssertionError("expected CanonError")
