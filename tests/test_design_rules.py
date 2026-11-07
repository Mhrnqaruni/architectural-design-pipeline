"""The design rules as tests. They read the same data the drawings and the 3D model are built from,
so a design change that breaks a rule fails here before anyone sees a drawing."""
import copy
import math

import pytest

from archdesign import areas, checks, floors, geom, plans


def polygon_area(pts):
    return abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))) / 2


def distance_to_line(p, a, b):
    (x0, y0), (x1, y1) = a, b
    return abs((x1 - x0) * (y0 - p[1]) - (x0 - p[0]) * (y1 - y0)) / math.dist(a, b)


def test_land_matches_the_survey():
    pts = geom.PLOT
    assert polygon_area(pts) > 0
    sides = dict(zip("NESW", (math.dist(a, b) for a, b in zip(pts, pts[1:] + pts[:1]))))
    for side, length in geom.PLOT_SIDES.items():
        assert sides[side] == pytest.approx(length, abs=0.01)


def test_setbacks_meet_the_requirements():
    x0, y0, x1, y1 = geom.HOUSE
    road = (geom.PLOT[3], geom.PLOT[0])                      # the west boundary runs along the road
    mean = (distance_to_line((x0, y0), *road) + distance_to_line((x0, y1), *road)) / 2
    assert abs(mean - geom.ROAD_SETBACK) < 0.1                # the boundary is angled, so check the mean
    assert geom.PLOT[0][1] - y1 > geom.NORTH_SETBACK_MIN


@pytest.mark.parametrize("tag", ["B", "G", "T"])
def test_every_floor_is_within_its_area_limit(tag):
    built = areas.built_area(tag) + (areas.terrace_area() if tag == "T" else 0.0)
    assert built <= areas.LIMITS[tag]


@pytest.mark.parametrize("tag", ["B", "G", "T"])
def test_area_table_adds_up_to_the_built_area(tag):
    rows = areas.breakdown(tag)
    assert sum(a for _, _, a in rows) == pytest.approx(round(areas.built_area(tag), 2), abs=1e-6)
    assert all(a > 0 for _, _, a in rows)
    assert 10 < rows[-1][2] < 16, "the walls row is the remainder; outside this range rooms overlap"


@pytest.mark.parametrize("name, floor, start", checks.FLOORS)
def test_every_room_can_be_reached_from_the_entrance(name, floor, start):
    assert checks.check_reach(name, floor, start) == 0


@pytest.mark.parametrize("name, floor, start", checks.FLOORS)
def test_no_door_swings_into_anything(name, floor, start):
    assert checks.check_swings(name, floor) == 0


def test_reach_check_catches_the_old_dead_end():
    """Regression: an earlier ground floor had no way from the entrance into the living room."""
    old = copy.deepcopy(floors.GROUND)
    old["walls"] = floors.WET_WALLS + floors.SUITE_WALLS_T + floors.CORE_WALLS
    old["openings"] = [op for op in old["openings"] if op[:5] != ("door", 9.15, 8.43, 9.95, 8.53)]
    old["openings"].append(("door", 9.0, 8.5, 9.1, 9.3, 1, +1))
    old["rooms"] = [r for r in old["rooms"] if r[0] != "Corridor"]
    assert checks.check_reach("old ground floor", old, (5.0, 8.0)) == 1


def test_first_floor_keeps_a_large_master():
    first = next(r for r in floors.TOP["rooms"] if r[0] == "Master bedroom")
    assert plans.area(first[2]) > 11.0                         # the brief asks for a large master upstairs


def test_kitchens_have_a_full_height_fridge_and_a_wide_aisle():
    for floor in (floors.GROUND, floors.TOP):
        assert floor["furniture"].get("fridge"), "each kitchen needs a place for a full-height fridge"
    counter, island = (11.9, 11.48, 14.9, 12.07), floors.GROUND["furniture"]["island"][0]
    assert counter[1] - island[3] >= 1.0                       # ground floor: counter to island
    counter, island = (12.75, 5.58, 14.8, 6.18), floors.TOP["furniture"]["island"][0]
    assert island[1] - counter[3] >= 1.0                       # first floor


def test_3d_scene_and_loose_furniture():
    from archdesign import export3d, web_model
    scene = export3d.build()
    assert {"boxes", "items", "labels", "terrain", "roof"} <= scene.keys()
    assert len(scene["items"]) > 60
    assert web_model.check_furniture(log=lambda *_: None) == 0


def test_generated_dxf_files_pass_the_audit(tmp_path):
    from archdesign import drawing_set
    assert drawing_set.build(tmp_path, only={"A-102"}, log=lambda *_: None) == []
    model = tmp_path / "model_1to1_metres.dxf"
    drawing_set.build_model_dxf(model)
    assert drawing_set.audit_dxf(model) == []


def test_cli_check_command():
    from archdesign.cli import main
    assert main(["check"]) == 0
