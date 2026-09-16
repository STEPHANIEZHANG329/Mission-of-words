from llk.images import fit_rect, largest_white_rect, open_lineart
from llk.search_place import place_targets
from llk.spec import load_spec


def test_fit_rect_never_stretches():
    x, y, w, h = fit_rect(1024, 1536, 0, 0, 200, 100)
    assert abs((w / h) - (1024 / 1536)) < 1e-6
    assert w <= 200 and h <= 100


def test_search_targets_avoid_heavy_ink():
    spec = load_spec()
    mission = next(m for m in spec.missions if m.id == "mission_06")
    bg = open_lineart("search_bg_mission_06")
    placed = place_targets(bg, mission.pages[1].targets)
    assert len(placed) == 8
    assert len({p.name for p in placed}) == 8
    gray = bg.convert("L").resize((64, 64))
    px = gray.load()
    for p in placed:
        cx = min(63, int((p.x + p.scale / 2) * 64))
        cy = min(63, int((p.y + p.scale / 2) * 64))
        # Center of a target must not sit on a very dark contour (faces/hands).
        assert px[cx, cy] > 150, f"{p.name} landed on ink at {cx},{cy} val={px[cx, cy]}"


def test_certificate_white_field_is_large_and_centered():
    img = open_lineart("certificate_frame")
    x, y, w, h = largest_white_rect(img)
    assert w > 0.28 and h > 0.18
    # Field should sit in the open center, not over the bottom figures.
    assert y + h < 0.72
    assert x > 0.08
    assert x + w < 0.95
