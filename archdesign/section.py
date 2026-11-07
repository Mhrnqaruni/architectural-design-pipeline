"""Sections A-A (west-east, looking north) and B-B (south-north, looking west), in (u, z)."""
from . import floors, geom
from .elev import EAVE, O, PITCH, RIDGE, ROOF_T, X0, X1, Y0, Y1, YM, under
from .plans import draw_level

SLAB = geom.SLAB


def cut(pen, r):
    pen.fill_rect(r, "A-WALL-PATT", color=250)
    pen.rect(r, "A-SECT")


def wall(pen, u0, u1, z0, z1, gaps=()):
    """A cut wall from z0 to z1, interrupted by (g0, g1) openings drawn as glass."""
    edges = [z0]
    for g0, g1 in gaps:
        edges += [g0, g1]
    edges.append(z1)
    for a, b in zip(edges[::2], edges[1::2]):
        if b - a > 0.01:
            cut(pen, (u0, a, u1, b))
    for g0, g1 in gaps:
        um = (u0 + u1) / 2
        pen.line((um - 0.03, g0), (um - 0.03, g1), "A-GLAZ")
        pen.line((um + 0.03, g0), (um + 0.03, g1), "A-GLAZ")


def partitions(pen, floor, z, along_x, at, top=None):
    for w in floor["walls"]:
        lo, hi = (w[1], w[3]) if along_x else (w[0], w[2])
        if lo <= at <= hi:
            u0, u1 = (w[0], w[2]) if along_x else (w[1], w[3])
            if u1 - u0 <= 0.12:
                cut(pen, (u0, z, u1, top if top else z + 2.7))


def soil(pen, pts):
    poly = pts + [(pts[-1][0], -4.0), (pts[0][0], -4.0)]
    pen.fill(poly, "A-SITE-PLNT", color=254)
    pen.poly(pts, "A-SITE", lineweight=70)


def label(pen, en, alt_name, u, z):
    pen.text(en, (u, z + 0.2), h=1.8)
    pen.text(alt_name, (u, z - 0.15), h=1.9, rtl=True)


def section_aa(pen, y=geom.SECTION_AA_Y):
    xw, xe = geom.west_x(y), geom.east_x(y)
    soil(pen, [(xw, 0.0), (X0, 0.0), (X0, -SLAB), (8.6, -SLAB), (8.6, -3.3), (X1, -3.3),
               (X1, -3.0), (xe, -3.0)])
    pen.poly([(xw, 0.0), (xe, -3.0)], "A-SITE-PLNT", linetype="DASHED", ltscale=6)
    cut(pen, (8.6, -3.0 - SLAB, X1, -3.0))
    cut(pen, (X0, -SLAB, X1, 0.0))
    cut(pen, (X0, 3.0 - SLAB, X1, 3.0))
    wall(pen, 8.6, 8.9, -3.0, -SLAB)
    wall(pen, X1 - 0.3, X1, -3.0, -SLAB, [(-3.0, -0.6)])
    wall(pen, X0, X0 + 0.3, -1.0, -SLAB)
    wall(pen, X0, X0 + 0.3, 0.0, 3.0 - SLAB)
    wall(pen, X1 - 0.3, X1, 0.0, 3.0 - SLAB, [(0.1, 2.5)])
    zr = under(y)
    wall(pen, X0, X0 + 0.3, 3.0, zr)
    wall(pen, X1 - 0.3, X1, 3.0, zr, [(3.1, zr - 0.15)])
    for floor, z, top in ((floors.BASEMENT, -3.0, None), (floors.GROUND, 0.0, None),
                          (floors.TOP, 3.0, zr)):
        partitions(pen, floor, z, along_x=True, at=y, top=top)
    cut(pen, (X0 - O, zr, X1 + O, zr + ROOF_T))
    pen.line((X0 - O, RIDGE + ROOF_T), (X1 + O, RIDGE + ROOF_T), "A-ELEV-HIDD")
    for en, alt_name, u, z in (("Not dug out", "بدون گودبرداری", 6.3, -1.6),
                              ("Storage", "انباری", 9.65, -1.6),
                              ("Billiards lounge", "بیلیارد", 12.7, -1.6),
                              ("WC", "سرویس", 5.2, 1.4), ("Bathroom", "حمام", 7.0, 1.4),
                              ("Master bedroom", "اتاق‌خواب مستر", 10.5, 1.4),
                              ("Living", "پذیرایی", 13.5, 1.4),
                              ("Master bedroom", "اتاق‌خواب مستر", 10.5, 4.4),
                              ("Kitchen + living", "آشپزخانه و پذیرایی", 13.45, 4.4)):
        label(pen, en, alt_name, u, z)
    pen.text("Front yard ±0.00", (2.3, 0.35), h=1.8)
    pen.text("Lower garden -3.00", (18.7, -2.65), h=1.8)
    pen.text("natural ground", (2.6, -0.55), h=1.5, layer="A-SITE-PLNT")
    return 23.0


def section_bb(pen, x=geom.SECTION_BB_X):
    g = geom.ground_level
    sy0 = geom.PATIO_SOUTH[1]
    gs, gn = g(x, sy0), g(x, Y1)
    soil(pen, [(0.0, g(x, 0.0)), (sy0, gs), (sy0, 0.0), (Y0, 0.0), (Y0, -3.3), (Y1, -3.3),
               (Y1, gn), (14.23, g(x, 14.23))])
    cut(pen, (sy0, gs, sy0 + 0.25, 0.0))
    cut(pen, (Y0, -3.0 - SLAB, Y1, -3.0))
    cut(pen, (Y0, -SLAB, Y1, 0.0))
    cut(pen, (Y0, 3.0 - SLAB, Y1, 3.0))
    wall(pen, Y0, Y0 + 0.3, -3.0, -SLAB)
    wall(pen, Y1 - 0.3, Y1, -3.0, -SLAB)
    wall(pen, Y0, Y0 + 0.3, 0.0, 3.0 - SLAB, [(0.0, 2.4)])
    wall(pen, Y1 - 0.3, Y1, 0.0, 3.0 - SLAB, [(1.2, 2.2)])
    wall(pen, Y0, Y0 + 0.3, 3.0, under(Y0 + 0.3), [(4.0, 4.95)])
    ty = geom.TERRACE[0][1]
    wall(pen, ty, ty + 0.3, 3.0, under(ty + 0.3), [(3.0, 5.4)])
    partitions(pen, floors.BASEMENT, -3.0, along_x=False, at=x)
    under_pts = [(Y0 - O, under(Y0) - O * PITCH), (YM, under(YM)), (Y1 + O, under(Y1) - O * PITCH)]
    top_pts = [(u, z + ROOF_T) for u, z in under_pts]
    pen.fill(under_pts + top_pts[::-1], "A-WALL-PATT", color=250)
    pen.poly(under_pts + top_pts[::-1], "A-SECT", close=True)
    pen.line((Y1 - 0.08, 3.0), (Y1 - 0.08, 4.0), "A-ELEV")
    pen.line((ty + 0.3, 4.0), (Y1 - 0.08, 4.0), "A-ELEV")
    for en, alt_name, u, z in (("Billiards lounge", "بیلیارد", 7.3, -1.6),
                              ("WC", "سرویس", 10.0, -1.6), ("Boiler room", "موتورخانه", 11.35, -1.6),
                              ("Living", "پذیرایی", 7.3, 1.4), ("Kitchen", "آشپزخانه", 10.8, 1.4),
                              ("Kitchen + living", "آشپزخانه و پذیرایی", 7.2, 4.4),
                              ("Terrace", "تراس", 10.9, 4.4)):
        label(pen, en, alt_name, u, z)
    pen.text("South patio ±0.00", (3.0, 0.35), h=1.8)
    pen.text("retaining wall", (sy0 + 0.35, -0.6), h=1.5, align="MIDDLE_LEFT")
    pen.text("side path", (13.3, gn + 0.35), h=1.5)
    return 15.0


def levels(pen, u, with_basement=True):
    items = [(-3.0, "basement")] if with_basement else []
    items += [(0.0, "ground floor"), (3.0, "first floor"), (EAVE, "eaves"), (RIDGE, "ridge")]
    for z, name in items:
        draw_level(pen, (u, z), f"{z:+.2f}  {name}".replace("+0.00", "±0.00"))
