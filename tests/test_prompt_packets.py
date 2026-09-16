from mission_of_words.prompt_packets import planned_packets, write_prompt_packets


def test_planned_packets_are_eighteen_and_text_free():
    packets = planned_packets()
    assert len(packets) == 18
    roles = [item["role"] for item in packets]
    assert roles.count("coloring_hero") == 8
    assert roles.count("search_background") == 8
    assert roles.count("cast_reference") == 1
    assert roles.count("cover_front") == 1
    for packet in packets:
        prompt = packet["prompt"].lower()
        assert "do not draw any letters" in prompt
        assert "numbers" in prompt
        assert "no text" in prompt
        assert packet["size"] == "1664x2160"


def test_write_prompt_packets(tmp_path):
    dest = tmp_path / "packets.json"
    packets = write_prompt_packets(dest)
    assert dest.is_file()
    assert len(packets) == 18
