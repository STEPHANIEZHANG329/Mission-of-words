from mission_of_words.bible import bind_mission_record, load_all_canons, load_canon
from mission_of_words.book_manifest import load_book_record, load_mission_records


EXPECTED = {
    "mission_01": ("matthew_5_16", "Matthew 5:16"),
    "mission_02": ("genesis_1_14", "Genesis 1:14"),
    "mission_03": ("psalm_107_1", "Psalm 107:1"),
    "mission_04": ("isaiah_41_10", "Isaiah 41:10"),
    "mission_05": ("hebrews_13_16", "Hebrews 13:16"),
    "mission_06": ("ephesians_4_32", "Ephesians 4:32"),
    "mission_07": ("genesis_1_31", "Genesis 1:31"),
    "mission_08": ("1_thessalonians_5_18", "1 Thessalonians 5:18"),
}


def test_all_eight_canons_are_source_locked_public_domain():
    records = load_all_canons()
    assert set(records) == {item[0] for item in EXPECTED.values()}
    for canon_id, record in records.items():
        assert record["translation"] == "KJV"
        assert "1769" in record["source_edition"]
        assert record["license"] == "public_domain"
        assert "public domain" in record["license_note"].lower()
        assert record["source_text"].strip()
        assert record["child_paraphrase"].strip()
        assert record["child_paraphrase"].strip() != record["source_text"].strip()
        assert "pumpkin" not in record["source_text"].lower()
        assert record["allowed_visual_motifs"]
        assert record["forbidden_claims"]


def test_each_mission_binds_its_locked_canon():
    book = load_book_record()
    missions = load_mission_records()
    assert book["canon_ids"] == [EXPECTED[mission_id][0] for mission_id in book["mission_ids"]]
    for mission in missions:
        canon_id, reference = EXPECTED[mission["id"]]
        assert mission["canon_id"] == canon_id
        assert mission["scripture_reference"] == reference
        bound = bind_mission_record(mission)
        assert bound["canon_id"] == canon_id
        assert bound["reference"] == reference


def test_mission_7_locks_genesis_1_31_not_psalm_19():
    record = load_canon("genesis_1_31")
    assert record["reference"] == "Genesis 1:31"
    assert "it was very good" in record["source_text"]
    assert "Psalm 19" not in record["source_text"]
    assert "Psalm 19:1 was not used" in record["lock_note"]


def test_mission_6_keeps_ephesians_4_32():
    record = load_canon("ephesians_4_32")
    assert "be ye kind one to another" in record["source_text"]
    assert "forgiving one another" in record["source_text"]


def test_hebrews_communicate_is_sharing_not_talking():
    record = load_canon("hebrews_13_16")
    assert "communicate" in record["source_text"]
    assert "share" in record["child_paraphrase"].lower()
    assert any("talk" in claim.lower() for claim in record["forbidden_claims"])
