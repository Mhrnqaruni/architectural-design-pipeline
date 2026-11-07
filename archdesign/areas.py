"""Area breakdown of each floor, so the area table adds up to the built area exactly.

Named rooms use the same rectangles as the plan labels. Stairs and lift, the other unnamed
passages (lift hall, short links) and the walls are measured on a 1 cm grid, so nothing is counted
twice. The built area is the outside size: the house rectangle, less the undug corner (basement)
or the covered terrace (first floor).
"""
import numpy as np

from . import floors, geom, plans

STEP = 0.01
LIMITS = {"B": 70.0, "G": 80.0, "T": 50.0 + 30.0}     # first floor: 50 m² plus a 30 m² terrace
FLOOR = {"B": floors.BASEMENT, "G": floors.GROUND, "T": floors.TOP}


def house_area():
    x0, y0, x1, y1 = geom.HOUSE
    return (x1 - x0) * (y1 - y0)


def terrace_area():
    return sum(plans.area(t) for t in geom.TERRACE)


def built_area(tag):
    if tag == "B":
        return house_area() - plans.area(floors.BASEMENT["undug"])
    if tag == "T":
        return house_area() - terrace_area()
    return house_area()


def named_rooms(fl):
    rows = [(en, alt_name, plans.area(r)) for en, alt_name, r, _ in fl["rooms"]]
    en, alt_name, r, minus, _ = fl["open_space"]
    rows.append((en, alt_name, plans.area(r) - sum(plans.area(m) for m in minus)))
    return rows


def breakdown(tag):
    """Rows (name, second-language name, m²) that add up to the built area, rounded to 0.01 m²."""
    fl = FLOOR[tag]
    x0, y0, x1, y1 = geom.HOUSE
    nx, ny = int(round((x1 - x0) / STEP)), int(round((y1 - y0) / STEP))
    gx, gy = np.meshgrid(x0 + (np.arange(nx) + 0.5) * STEP, y0 + (np.arange(ny) + 0.5) * STEP,
                         indexing="ij")

    def box(r):
        return (gx >= r[0]) & (gx <= r[2]) & (gy >= r[1]) & (gy <= r[3])

    used = np.zeros_like(gx, bool)
    for w in (fl.get("ext_walls") or plans.outer_walls(geom.HOUSE)) + fl["walls"]:
        used |= box(w)
    for _, _, r, _ in fl["rooms"]:
        used |= box(r)
    _, _, r, minus, _ = fl["open_space"]
    space = box(r)
    for m in minus:
        space &= ~box(m)
    used |= space
    if tag == "B":
        used |= box(floors.BASEMENT["undug"])
    if tag == "T":
        for t in geom.TERRACE:
            used |= box(t)
    core = (box(geom.STAIR) | box(geom.LIFT)) & ~used
    used |= core
    passages = ~used
    cell = STEP * STEP
    rows = [(en, alt_name, round(a, 2)) for en, alt_name, a in named_rooms(fl)]
    rows.append(("Stairs and lift", "پله و آسانسور", round(core.sum() * cell, 2)))
    rows.append(("Lift hall and passages", "راهروهای دیگر", round(passages.sum() * cell, 2)))
    walls = round(built_area(tag), 2) - sum(a for _, _, a in rows)
    rows.append(("Walls", "دیوارها", round(walls, 2)))
    return rows
