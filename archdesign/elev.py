"""Elevations. Each facade is drawn in (u, z): u runs left to right as the viewer sees
it, z is the level in metres. Openings come straight from the floor plans."""
from . import floors, geom
from .plans import draw_level

EAVE, RIDGE, ROOF_T = geom.LEVELS["eaves"], geom.LEVELS["ridge"], 0.29
X0, Y0, X1, Y1 = geom.HOUSE
YM, O = (Y0 + Y1) / 2, geom.ROOF_OVERHANG
PITCH = (RIDGE - EAVE) / (YM - Y0)
FLOORS = [(floors.BASEMENT, -3.0), (floors.GROUND, 0.0), (floors.TOP, 3.0)]
TX0, TY0, TX1, TY1 = geom.TERRACE[0]


def under(y):
    """Roof underside level above plan position y (north-south)."""
    return EAVE + (min(y, 2 * YM - y) - Y0) * PITCH


def heights(op):
    w = max(op[3] - op[1], op[4] - op[2])
    if op[0] in ("door", "pivot"):
        return (0.0, 2.5) if op[1] < X0 + 0.31 else (0.0, 2.2)
    if op[0] == "slide":
        return 0.0, 2.4
    if len(op) > 5:
        return op[5], op[6]
    if w >= 2.4:
        return 0.1, 2.4
    return (1.5, 2.2) if w <= 0.9 else (0.9, 2.2)


# per face: u mapping, and a test for openings on that face (op, floor level) -> on face, set back
FACES = {
    "east": (lambda x, y: y, lambda op, z: (op[1] >= X1 - 0.31, False) if op[1] >= X1 - 0.31
             else ((True, True) if z == 3 and abs(op[1] - TX0) < 0.01 and op[3] - op[1] < 0.5
                   else (False, False))),
    "west": (lambda x, y: 20 - y, lambda op, z: (op[3] <= X0 + 0.31 and z >= 0, False)),
    "north": (lambda x, y: 30 - x, lambda op, z: (op[2] >= Y1 - 0.31, False)),
    "south": (lambda x, y: x, lambda op, z: (op[4] <= Y0 + 0.31, False)),
}


def draw_openings(pen, face):
    u_of, test = FACES[face]
    for floor, z in FLOORS:
        for op in floor["openings"]:
            on, behind = test(op, z)
            if op[0] == "opening" or not on:
                continue
            a, b = u_of(op[1], op[2]), u_of(op[3], op[4])
            u0, u1 = min(a, b), max(a, b)
            h0, h1 = heights(op)
            if z == 3 and face in ("north", "south") and op[0] == "window":
                h1 = min(h1, 1.95)
            layer = "A-ELEV-HIDD" if behind else "A-ELEV"
            pen.rect((u0, z + h0, u1, z + h1), layer)
            pen.rect((u0 + 0.06, z + h0 + 0.06, u1 - 0.06, z + h1 - 0.06), "A-GLAZ")
            if u1 - u0 > 1.6:
                um = (u0 + u1) / 2
                pen.line((um, z + h0 + 0.06), (um, z + h1 - 0.06), "A-GLAZ")
            if op[0] in ("door", "pivot") and op[1] < X0 + 0.31:   # front door: tall pivot door
                pen.line((u0 + 0.12, z + 1.1), (u0 + 0.12, z + 1.3), "A-ELEV")


def railing(pen, u0, u1, z=3.0):
    pen.line((u0, z + 1.0), (u1, z + 1.0), "A-ELEV")
    pen.line((u0, z + 0.1), (u1, z + 0.1), "A-ELEV-HIDD")


def gable_roof(pen, u_of_y):
    pts = [(u_of_y(Y0 - O), under(Y0) - O * PITCH), (u_of_y(YM), RIDGE),
           (u_of_y(Y1 + O), under(Y1) - O * PITCH)]
    top = [(u, z + ROOF_T) for u, z in pts]
    pen.poly(pts, "A-ROOF")
    pen.poly(top, "A-ELEV")
    pen.line(pts[0], top[0], "A-ELEV")
    pen.line(pts[2], top[2], "A-ELEV")


def roof_band(pen, u0, u1):
    z0, z1 = under(Y0) - O * PITCH, RIDGE + ROOF_T
    pen.rect((u0, z0, u1, z1), "A-ELEV")
    u = u0 + 0.5
    while u < u1:
        pen.line((u, z0), (u, z1), "A-ELEV-HIDD")
        u += 0.5


def ground(pen, pts):
    """Finished ground line; soil below is masked white so buried walls disappear."""
    poly = pts + [(pts[-1][0], -4.2), (pts[0][0], -4.2)]
    pen.fill(poly, "A-ANNO-NPLT").dxf.true_color = 0xFFFFFF
    pen.poly(pts, "A-SITE", lineweight=70)


def levels(pen, u, items):
    for z, name in items:
        draw_level(pen, (u, z), f"{z:+.2f}  {name}".replace("+0.00", "±0.00"))


def draw_elevation(pen, face):
    g = geom.ground_level
    lv = [(0.0, "ground floor"), (3.0, "first floor"), (EAVE, "eaves"), (RIDGE, "ridge")]
    if face == "east":
        pen.rect((Y0, -3.0, Y1, 3.0), "A-ELEV")
        pen.poly([(Y0, 3.0), (TY0, 3.0), (TY0, under(TY0)), (YM, RIDGE), (Y0, EAVE)], "A-ELEV",
                 close=True)
        pen.rect((Y1 - 0.3, 3.0, Y1, EAVE), "A-ELEV")
        pen.poly([(TY0 + 0.3, 3.0), (TY0 + 0.3, under(TY0 + 0.3)), (Y1, EAVE)], "A-ELEV-HIDD")
        railing(pen, TY0 + 0.3, Y1 - 0.3)
        glass = [(6.4, 5.65), (8.95, 5.65), (8.95, under(8.95) - 0.15), (YM, RIDGE - 0.15),
                 (6.4, under(6.4) - 0.15)]
        pen.poly(glass, "A-GLAZ", close=True)
        pen.line((7.7, 5.65), (7.7, under(7.7) - 0.15), "A-GLAZ")
        gable_roof(pen, lambda y: y)
        ground(pen, [(2.5, -3.0), (14.6, -3.0)])
        lv = [(-3.0, "basement / lower garden")] + lv
        right = 15.4
    elif face == "west":
        pen.poly([(20 - Y1, 0.0), (20 - Y0, 0.0), (20 - Y0, EAVE), (20 - YM, RIDGE), (20 - Y1, EAVE)],
                 "A-ELEV", close=True)
        gable_roof(pen, lambda y: 20 - y)
        ground(pen, [(5.5, 0.0), (17.0, 0.0)])
        right = 17.8
    elif face == "north":
        u_e, u_w, u_t = 30 - X1, 30 - X0, 30 - TX0
        pen.rect((u_e, -3.0, u_w, 0.0), "A-ELEV")
        pen.rect((u_e, 0.0, u_w, 3.0), "A-ELEV")
        pen.rect((u_t, 3.0, u_w, EAVE), "A-ELEV")
        pen.rect((u_e, 3.0, u_e + 0.3, EAVE), "A-ELEV")
        railing(pen, u_e + 0.3, u_t)
        roof_band(pen, u_e - O, u_w + O)
        for ux in (19.2, 20.7, 24.0):                     # roof windows in the north slope
            pen.rect((ux, 5.75, ux + 1.0, 6.45), "A-GLAZ")
            pen.rect((ux - 0.06, 5.69, ux + 1.06, 6.51), "A-ELEV")
        ground(pen, [(5.6, -3.0), (u_e, -3.0), (u_e, g(X1, 13.3)), (30 - 10.0, g(10.0, 13.3)),
                     (30 - 4.0, g(4.0, 13.3)), (29.8, g(0.2, 13.3))])
        lv = [(-3.0, "basement / lower garden")] + lv
        right = 30.6
    else:  # south
        pen.rect((8.6, -3.0, X1, 0.0), "A-ELEV")
        pen.rect((X0, -1.0, 8.6, 0.0), "A-ELEV")
        pen.rect((X0, 0.0, X1, 3.0), "A-ELEV")
        pen.rect((X0, 3.0, X1, EAVE), "A-ELEV")
        roof_band(pen, X0 - O, X1 + O)
        sx0 = geom.PATIO_SOUTH[0]
        ground(pen, [(1.1, 0.0), (6.6, 0.0), (6.6, g(6.6, 0.5)), (sx0, g(sx0, 0.5)), (sx0, 0.0),
                     (X1, 0.0), (X1, -3.0), (19.6, -3.0)])
        pen.rect((sx0, g(sx0, 0.5), X1, 0.0), "A-ELEV")
        lv = [(-3.0, "lower garden")] + [(0.0, "ground floor / patio")] + lv[1:]
        right = 20.4
    draw_openings(pen, face)
    levels(pen, right, lv)
