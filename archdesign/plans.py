"""Draws one floor plan with a Pen: walls with openings, doors, windows, stairs, labels, dims."""
import math

from . import geom
from .cad import arc_between, split_rect

T = geom.EXT_WALL


def area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def outer_walls(o):
    x0, y0, x1, y1 = o
    return [(x0, y1 - T, x1, y1), (x0, y0, x1, y0 + T), (x0, y0 + T, x0 + T, y1 - T),
            (x1 - T, y0 + T, x1, y1 - T)]


def draw_walls(pen, outline, walls, openings, ext=None):
    cuts = [op[1:5] for op in openings]
    for w in (ext or outer_walls(outline)) + walls:
        for piece in split_rect(w, cuts):
            pen.fill_rect(piece, "A-WALL-PATT", color=250)
            pen.rect(piece, "A-WALL")


def draw_door(pen, op):
    _, x0, y0, x1, y1, at_end, s = op
    if (x1 - x0) >= (y1 - y0):                       # horizontal wall
        width, face = x1 - x0, (y1 if s > 0 else y0)
        hinge = (x1 if at_end else x0, face)
        leaf = (hinge[0], face + s * width)
        a_leaf, a_closed = (90 if s > 0 else 270), (180 if at_end else 0)
    else:                                            # vertical wall
        width, face = y1 - y0, (x1 if s > 0 else x0)
        hinge = (face, y1 if at_end else y0)
        leaf = (face + s * width, hinge[1])
        a_leaf, a_closed = (0 if s > 0 else 180), (270 if at_end else 90)
    pen.line(hinge, leaf, "A-DOOR")
    pen.arc(hinge, width, *arc_between(a_leaf, a_closed), "A-DOOR")


def draw_pivot(pen, op):
    """Pivot door in a vertical wall: pivot `off` from the y0 jamb, the long part swings inside (+x)."""
    _, x0, y0, x1, y1, off = op
    xm, p = (x0 + x1) / 2, ((x0 + x1) / 2, y0 + off)
    inner = (y1 - y0) - off
    pen.line((xm - off, p[1]), (xm + inner, p[1]), "A-DOOR")
    pen.arc(p, inner, 0, 90, "A-DOOR")
    pen.arc(p, off, 180, 270, "A-DOOR")


def draw_slide(pen, op):
    _, x0, y0, x1, y1 = op[:5]
    if (x1 - x0) >= (y1 - y0):
        ym, L = (y0 + y1) / 2, x1 - x0
        pen.line((x0, ym - 0.03), (x0 + L * 0.55, ym - 0.03), "A-DOOR")
        pen.line((x1 - L * 0.55, ym + 0.03), (x1, ym + 0.03), "A-DOOR")
    else:
        xm, L = (x0 + x1) / 2, y1 - y0
        pen.line((xm - 0.03, y0), (xm - 0.03, y0 + L * 0.55), "A-DOOR")
        pen.line((xm + 0.03, y1 - L * 0.55), (xm + 0.03, y1), "A-DOOR")


def draw_window(pen, op):
    _, x0, y0, x1, y1 = op[:5]
    if (x1 - x0) >= (y1 - y0):
        for y in (y0, y1):
            pen.line((x0, y), (x1, y), "A-GLAZ")
        for y in ((y0 + y1) / 2 - 0.025, (y0 + y1) / 2 + 0.025):
            pen.line((x0, y), (x1, y), "A-GLAZ")
    else:
        for x in (x0, x1):
            pen.line((x, y0), (x, y1), "A-GLAZ")
        for x in ((x0 + x1) / 2 - 0.025, (x0 + x1) / 2 + 0.025):
            pen.line((x, y0), (x, y1), "A-GLAZ")


def draw_openings(pen, openings):
    for op in openings:
        {"door": draw_door, "pivot": draw_pivot, "slide": draw_slide, "window": draw_window}.get(
            op[0], lambda *_: None)(pen, op)


def draw_stair(pen, label):
    x0, y0, x1, y1 = geom.STAIR
    xm0, xm1 = (x0 + x1) / 2 - 0.05, (x0 + x1) / 2 + 0.05
    land = y1 - geom.STAIR_LANDING
    pen.rect(geom.STAIR, "A-FLOR-STRS")
    pen.rect((xm0, y0, xm1, land), "A-FLOR-STRS")
    pen.line((x0, land), (x1, land), "A-FLOR-STRS")
    step = (land - y0) / 8
    for i in range(1, 8):
        y = y0 + i * step
        pen.line((x0, y), (xm0, y), "A-FLOR-STRS")
        pen.line((xm1, y), (x1, y), "A-FLOR-STRS")
    a, b = (x0 + xm0) / 2, (xm1 + x1) / 2
    ym = (land + y1) / 2
    pen.poly([(a, y0 + 0.15), (a, ym), (b, ym), (b, y0 + 0.35)], "A-FLOR-STRS")
    pen.poly([(b - 0.12, y0 + 0.55), (b, y0 + 0.35), (b + 0.12, y0 + 0.55)], "A-FLOR-STRS")
    pen.text(label, (a, y0 - 0.12), h=1.8, layer="A-ANNO-TEXT")


def draw_lift(pen):
    x0, y0, x1, y1 = geom.LIFT
    pen.rect(geom.LIFT, "A-FLOR-STRS")
    pen.line((x0, y0), (x1, y1), "A-FLOR-STRS")
    pen.line((x0, y1), (x1, y0), "A-FLOR-STRS")
    pen.text("LIFT", ((x0 + x1) / 2, (y0 + y1) / 2 + 0.18), h=1.6)
    pen.text("آسانسور", ((x0 + x1) / 2, (y0 + y1) / 2 - 0.2), h=1.7, rtl=True)


def label(pen, en, alt_name, a, at):
    small = a < 3.6
    h1, h2, h3, gap = (1.5, 1.6, 1.4, 0.2) if small else (2.2, 2.4, 1.8, 0.32)
    x, y = at
    pen.text(en, (x, y + gap), h=h1, layer="A-AREA-IDEN")
    pen.text(alt_name, (x, y), h=h2, layer="A-AREA-IDEN", rtl=True)
    pen.text(f"{a:.1f} m²", (x, y - gap), h=h3, layer="A-AREA-IDEN")


def draw_rooms(pen, floor):
    for en, alt_name, r, at in floor["rooms"]:
        label(pen, en, alt_name, area(r), at or ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2))
    en, alt_name, r, minus, at = floor["open_space"]
    label(pen, en, alt_name, area(r) - sum(area(m) for m in minus), at)


DIRS = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}


def _ellipse(c, ax, ay, n=28):
    return [(c[0] + ax * math.cos(2 * math.pi * i / n), c[1] + ay * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def _local(pen, origin, d, pts, layer, close=True):
    """Draw points given as (across, along) the facing direction d, from origin."""
    fx, fy = DIRS[d]
    pen.poly([(origin[0] + a * fy + b * fx, origin[1] - a * fx + b * fy) for a, b in pts],
             layer, close=close)


def draw_wc(pen, x, y, d):
    """Western WC: (x, y) is the wall face behind the cistern, d the way the pan faces."""
    _local(pen, (x, y), d, [(-0.225, 0), (0.225, 0), (0.225, 0.2), (-0.225, 0.2)], "A-FURN")
    _local(pen, (x, y), d, [(a, b + 0.44) for a, b in _ellipse((0, 0), 0.18, 0.24)], "A-FURN")


def draw_squat(pen, x, y, d):
    """Squat toilet pan centred on (x, y), long side along d."""
    _local(pen, (x, y), d, [(-0.21, -0.3), (0.21, -0.3), (0.21, 0.3), (-0.21, 0.3)], "A-FURN")
    _local(pen, (x, y), d, [(a, b + 0.06) for a, b in _ellipse((0, 0), 0.09, 0.15)], "A-FURN")


def draw_basin(pen, r):
    pen.rect(r, "A-FURN")
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    ax, ay = (r[2] - r[0]) * 0.32, (r[3] - r[1]) * 0.32
    pen.poly(_ellipse((cx, cy), ax, ay), "A-FURN", close=True)


def draw_furniture(pen, f):
    for b in f.get("bed", []):
        r, head = b[:4], (b[4] if len(b) > 4 else "N")
        pen.rect(r, "A-FURN")
        if head in ("N", "S"):
            y = r[3] - 0.35 if head == "N" else r[1] + 0.35
            pen.line((r[0], y), (r[2], y), "A-FURN")
        else:
            x = r[2] - 0.35 if head == "E" else r[0] + 0.35
            pen.line((x, r[1]), (x, r[3]), "A-FURN")
    for kind in ("counter", "island", "table"):
        for r in f.get(kind, []):
            pen.rect(r, "A-FURN")
    for r in f.get("sofa", []) + f.get("tub", []):
        pen.rect(r, "A-FURN")
        pen.rect((r[0] + 0.15, r[1] + 0.15, r[2] - 0.15, r[3] - 0.15), "A-FURN")
    for r in f.get("shower", []):
        pen.rect(r, "A-FURN")
        pen.line((r[0], r[1]), (r[2], r[3]), "A-FURN")
    for r in f.get("fridge", []):                    # full-height fridge
        pen.rect(r, "A-FURN")
        pen.rect((r[0] + 0.04, r[1] + 0.04, r[2] - 0.04, r[3] - 0.04), "A-FURN")
        pen.text("REF", ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2), h=1.4, layer="A-FURN")
    for x0, y0, x1, y1, wall in f.get("tv", []):     # low unit, screen drawn on the wall side
        pen.rect((x0, y0, x1, y1), "A-FURN")
        if wall in ("W", "E"):
            x, k = (x0 + 0.06 if wall == "W" else x1 - 0.06), (y1 - y0) * 0.1
            pen.rect((x - 0.025, y0 + k, x + 0.025, y1 - k), "A-FURN")
        else:
            y, k = (y0 + 0.06 if wall == "S" else y1 - 0.06), (x1 - x0) * 0.1
            pen.rect((x0 + k, y - 0.025, x1 - k, y + 0.025), "A-FURN")
    for x, y in f.get("toilet", []):
        pen.circle((x, y), 0.17, "A-FURN")
    for x, y, d in f.get("wc", []):
        draw_wc(pen, x, y, d)
    for x, y, d in f.get("squat", []):
        draw_squat(pen, x, y, d)
    for r in f.get("basin", []):
        draw_basin(pen, r)


def draw_overall_dims(pen, o):
    x0, y0, x1, y1 = o
    pen.dim((x0, y0), (x1, y0), -1.3)
    pen.dim((x1, y0), (x1, y1), 1.3, vertical=True)


def draw_chains(pen, floor, o):
    xs, ys = floor.get("chain_x", []), floor.get("chain_y", [])
    for a, b in zip(xs, xs[1:]):
        pen.dim((a, o[3]), (b, o[3]), 0.9)
    for a, b in zip(ys, ys[1:]):
        pen.dim((o[0], a), (o[0], b), -0.9, vertical=True)


def draw_level(pen, at, text, r=0.15):
    x, y = at
    pen.circle(at, r, "A-FLOR-LEVL")
    pen.line((x - r * 1.4, y), (x + r * 1.4, y), "A-FLOR-LEVL")
    pen.line((x, y - r * 1.4), (x, y + r * 1.4), "A-FLOR-LEVL")
    for sx, sy in ((1, 1), (-1, -1)):
        pts = [(x, y)] + [(x + sx * r * c, y + sy * r * s) for c, s in
                          ((1, 0), (0.92, 0.38), (0.71, 0.71), (0.38, 0.92), (0, 1))]
        pen.fill(pts, "A-FLOR-LEVL")
    pen.text(text, (x + r * 2.0, y), h=2.0, layer="A-FLOR-LEVL", align="MIDDLE_LEFT")


def draw_notes(pen, notes):
    for en, alt_name, (x, y) in notes:
        pen.text(en, (x, y + 0.14), h=1.6, layer="A-ANNO-TEXT")
        pen.text(alt_name, (x, y - 0.16), h=1.7, layer="A-ANNO-TEXT", rtl=True)


def draw_terrace(pen):
    for x0, y0, x1, y1 in geom.TERRACE:
        pen.rect((x0, y0, x1, y1), "A-ELEV")
        pen.poly([(x0 + 0.3, y1 - 0.08), (x1 - 0.08, y1 - 0.08), (x1 - 0.08, y0 + 0.3)], "A-FLOR-LEVL")
        a = (x1 - x0 - 0.3) * (y1 - y0 - 0.3)
        label(pen, "Covered terrace", "تراس مسقف", a, ((x0 + x1) / 2 + 0.15, (y0 + y1) / 2 + 0.2))


def draw_roof_edge(pen):
    x0, y0, x1, y1 = geom.HOUSE
    o = geom.ROOF_OVERHANG
    pen.rect((x0 - o, y0 - o, x1 + o, y1 + o), "A-ROOF", linetype="DASHED", ltscale=6)
    pen.text("Roof edge above", (x1 + o - 0.1, y1 + o + 0.18), h=1.5, layer="A-ROOF",
             align="MIDDLE_RIGHT")


def draw_section_marks(pen):
    """Section lines A-A (y = 7.0, looking north) and B-B (x = 15.5, looking west)."""
    hx0, hy0, hx1, hy1 = geom.HOUSE
    ya, xb = geom.SECTION_AA_Y, geom.SECTION_BB_X
    for a, b, tag, look in (((hx0 - 1.4, ya), (hx1 + 1.4, ya), "A", (0, 1)),
                            ((xb, hy0 - 1.4), (xb, hy1 + 1.4), "B", (-1, 0))):
        pen.poly([a, b], "A-ANNO-SYMB", linetype="DASHDOT", ltscale=4)
        for end in (a, b):
            pen.circle(end, 0.32, "A-ANNO-SYMB")
            pen.text(tag, end, h=3.0, layer="A-ANNO-SYMB")
            tip = (end[0] + look[0] * 0.75, end[1] + look[1] * 0.75)
            side = (look[1] * 0.25, -look[0] * 0.25)
            base = (end[0] + look[0] * 0.32, end[1] + look[1] * 0.32)
            pen.fill([(base[0] + side[0], base[1] + side[1]), tip,
                      (base[0] - side[0], base[1] - side[1])], "A-ANNO-SYMB")


def draw_undug(pen, r):
    pen.fill_rect(r, "A-SITE-PLNT", color=254)
    x0, y0, x1, y1 = r
    k = 0.4
    x = x0 - (y1 - y0)
    while x < x1:
        a = (max(x, x0), y0 + max(0.0, x0 - x))
        b = (min(x + (y1 - y0), x1), y0 + min(y1 - y0, x1 - x))
        if b[0] > a[0]:
            pen.line(a, b, "A-SITE-PLNT")
        x += k
    pen.text("Not dug out (soil)", ((x0 + x1) / 2, (y0 + y1) / 2 + 0.15), h=1.7)
    pen.text("بدون گودبرداری", ((x0 + x1) / 2, (y0 + y1) / 2 - 0.2), h=1.8, rtl=True)


def draw_plan(pen, floor, outline, stair_label, dims_outline=None):
    if floor.get("undug"):
        draw_undug(pen, floor["undug"])
    draw_walls(pen, outline, floor["walls"], floor["openings"], floor.get("ext_walls"))
    draw_openings(pen, floor["openings"])
    draw_stair(pen, stair_label)
    draw_lift(pen)
    draw_furniture(pen, floor.get("furniture", {}))
    draw_rooms(pen, floor)
    draw_notes(pen, floor.get("notes", []))
    draw_overall_dims(pen, dims_outline or outline)
    draw_chains(pen, floor, outline)
    draw_section_marks(pen)
