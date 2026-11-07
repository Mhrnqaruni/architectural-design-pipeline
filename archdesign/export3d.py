"""3D data for the furnished viewer (viewer3d.js).

Every floor becomes walls, glass, frames, doors, floor finishes and furniture. Two wall sets are
made from the same plan data:
  * 'cut' walls stop at 2.4 m, for the furnished floor views. The outside walls on the side that
    faces the camera have a second, 0.6 m version, so the rooms behind them stay visible.
  * 'full' walls go up to the roof, for the whole-house view.
Furniture comes from the floor plans (floors.py), plus loose items (rugs, plants, stools,
nightstands, lamps) placed clear of every door swing. Plan metres: x east, y north, z level.
"""
import math

from . import floors, geom
from .cad import split_rect
from .elev import EAVE, O, PITCH, RIDGE, ROOF_T, X0, X1, Y0, Y1, YM, heights, under
from .plans import outer_walls

T = geom.EXT_WALL
CUT, LOW = 2.4, 0.6
LEVEL = {"B": -3.0, "G": 0.0, "T": 3.0}
FLOOR = {"B": floors.BASEMENT, "G": floors.GROUND, "T": floors.TOP}
INNER = (X0 + T, Y0 + T, X1 - T, Y1 - T)
TERRACE = geom.TERRACE[0]
DECK = (TERRACE[0] + T, TERRACE[1] + T, TERRACE[2], TERRACE[3])
UNDUG = floors.BASEMENT["undug"]

# floor finishes laid over the base finish (base: wood upstairs, tiles in the basement)
FINISH = {
    "G": [((4.3, 5.53, 6.1, 7.3), "tile"), ((6.2, 5.53, 7.8, 7.3), "tile"),
          ((4.3, 7.4, 7.9, 8.78), "stone")],
    "T": [((4.3, 5.53, 6.1, 7.3), "tile"), ((6.2, 5.53, 7.8, 7.3), "tile")],
    "B": [((10.5, 5.53, 14.9, 9.43), "wood"), ((8.0, 9.53, 13.1, 12.07), "stone"),
          ((13.2, 10.58, 14.9, 12.07), "concrete"), ((8.9, 5.53, 10.4, 8.43), "concrete")],
}
BASE_FINISH = {"B": "tile", "G": "wood", "T": "wood"}

# what each plan "counter" is
COUNTER_KIND = {(11.9, 11.48, 14.9, 12.07): "kitchen", (8.05, 10.4, 8.65, 12.03): "wardrobe",
                (6.95, 7.45, 7.6, 7.8): "shoe", (7.95, 6.75, 8.95, 7.3): "hanging",
                (12.75, 5.58, 14.8, 6.18): "kitchen", (6.95, 7.4, 7.6, 8.0): "laundry",
                (10.6, 8.95, 12.6, 9.38): "bar", (4.35, 7.4, 5.25, 7.72): "shoe",
                (13.9, 5.55, 14.85, 5.85): "shoe"}
SHOE_HEIGHT = {(4.35, 7.4, 5.25, 7.72): 0.85, (13.9, 5.55, 14.85, 5.85): 0.45}

# loose furniture that is not on the plans, placed clear of door swings (checked by web_model.check_furniture)
DECOR = {
    "G": [
        dict(k="nightstand", r=(11.6, 5.7, 11.95, 6.13), d="W"),
        dict(k="nightstand", r=(11.6, 7.83, 11.95, 8.26), d="W"),
        dict(k="nightstand", r=(9.18, 11.63, 9.55, 12.03), d="S"),
        dict(k="rug", r=(9.45, 5.88, 11.35, 8.08), c="rugA"),
        dict(k="rug", r=(9.3, 9.75, 10.95, 11.3), c="rugB"),
        dict(k="rug", r=(12.75, 6.3, 14.6, 8.5), c="rugC"),
        dict(k="plant", p=(14.55, 8.95), s=0.17, h=1.5),
        dict(k="stools", r=(12.4, 9.6, 14.6, 10.45), n=4, sides="NS"),
    ],
    "T": [
        dict(k="nightstand", r=(11.5, 6.35, 11.95, 6.8), d="W"),
        dict(k="nightstand", r=(11.5, 8.5, 11.95, 8.95), d="W"),
        dict(k="rug", r=(9.5, 6.45, 11.4, 8.85), c="rugA"),
        dict(k="plant", p=(11.62, 5.88), s=0.17, h=1.35),
        dict(k="tv", r=(10.75, 10.58, 11.1, 11.88), d="W"),
        dict(k="coffee", r=(9.3, 10.85, 9.75, 11.6)),
        dict(k="rug", r=(9.05, 10.5, 10.6, 11.95), c="rugC"),
        dict(k="rug", r=(11.4, 10.75, 12.75, 11.95), c="rugB"),
        dict(k="stools", r=(12.6, 7.2, 14.0, 7.8), n=2, sides="NS"),
        dict(k="armchair", r=(14.1, 7.95, 14.75, 8.6), d="E"),
        dict(k="table_round", p=(14.2, 10.95), s=0.3),
        dict(k="chair", p=(14.2, 10.38), d="N"),
        dict(k="chair", p=(14.2, 11.52), d="S"),
        dict(k="plant", p=(13.56, 11.97), s=0.18, h=1.25),
    ],
    "B": [
        dict(k="barstool", p=(11.15, 8.72)),
        dict(k="barstool", p=(12.05, 8.72)),
        dict(k="cuerack", r=(10.5, 6.2, 10.58, 7.2), d="E"),
        dict(k="shelves", r=(8.9, 5.53, 9.3, 7.6), d="E"),
        dict(k="shelves", r=(10.0, 5.53, 10.4, 8.43), d="W"),
        dict(k="shelves", r=(9.3, 5.53, 10.0, 5.93), d="N"),
        dict(k="plant", p=(4.65, 8.05), s=0.17, h=1.3),
        dict(k="boiler", r=(13.2, 11.05, 13.55, 11.5), d="E"),
        dict(k="tank", p=(13.5, 11.8), s=0.24),
    ],
}

# outside: patio dining set, cars and trees (plan positions)
PATIO_SET = (13.4, 2.9)
CARS = [(1.5, 0.45, "carA"), (1.5, 2.95, "carB")]
TREES = [(21.8, 11.6, 1.1), (18.2, 13.3, 0.85), (1.6, 13.0, 0.9), (-5.0, 17.0, 1.3), (10.5, 19.5, 1.2),
         (28.0, 15.5, 1.4), (31.5, 6.0, 1.3), (6.0, -7.5, 1.0), (16.5, -8.0, 1.1)]
CONIFERS = [(-6.5, 9.0, 1.2), (5.5, 19.0, 1.1), (24.5, 19.0, 1.2), (34.0, 12.5, 1.1), (-3.0, 23.0, 1.0)]


class Scene:
    def __init__(self):
        self.boxes, self.prisms, self.quads, self.ao, self.items, self.labels = [], [], [], [], [], []

    def box(self, x0, y0, z0, x1, y1, z1, m, g):
        if x1 - x0 > 1e-3 and y1 - y0 > 1e-3 and z1 - z0 > 1e-3:
            self.boxes.append([round(v, 3) for v in (x0, y0, z0, x1, y1, z1)] + [m, g])


def inside(r, x, y, e=1e-6):
    return r[0] - e <= x <= r[2] + e and r[1] - e <= y <= r[3] + e


def indoor(tag, x, y):
    """Inside the floor's rooms (stairs and lift included)."""
    if not inside(INNER, x, y):
        return False
    if tag == "B" and x < UNDUG[2] + T and y < UNDUG[3] + T:
        return False
    if tag == "T" and x > TERRACE[0] and y > TERRACE[1]:
        return False
    return True


def floored(tag, x, y):
    """Where a floor finish is walked on (terrace included, stair and lift voids not)."""
    if inside(geom.LIFT, x, y) or (tag != "B" and inside(geom.STAIR, x, y)):
        return False
    return indoor(tag, x, y) or (tag == "T" and inside(DECK, x, y))


def rect_minus(r, holes):
    """Axis-aligned rectangle minus rectangles, as a list of rectangles."""
    out = [r]
    for h in holes:
        nxt = []
        for a in out:
            if h[0] >= a[2] or h[2] <= a[0] or h[1] >= a[3] or h[3] <= a[1]:
                nxt.append(a)
                continue
            if h[1] > a[1]:
                nxt.append((a[0], a[1], a[2], h[1]))
            if h[3] < a[3]:
                nxt.append((a[0], h[3], a[2], a[3]))
            y0, y1 = max(a[1], h[1]), min(a[3], h[3])
            if h[0] > a[0]:
                nxt.append((a[0], y0, h[0], y1))
            if h[2] < a[2]:
                nxt.append((h[2], y0, a[2], y1))
        out = nxt
    return out


def ext_walls(tag):
    return FLOOR[tag].get("ext_walls") or outer_walls(geom.HOUSE)


def all_walls(tag):
    return ext_walls(tag) + FLOOR[tag]["walls"]


def outward(tag, w):
    """Which way an outside wall faces (N, S, E or W)."""
    x0, y0, x1, y1 = w
    if (x1 - x0) >= (y1 - y0):
        xm = (x0 + x1) / 2
        return "N" if not indoor(tag, xm, y1 + 0.2) else ("S" if not indoor(tag, xm, y0 - 0.2) else None)
    ym = (y0 + y1) / 2
    return "E" if not indoor(tag, x1 + 0.2, ym) else ("W" if not indoor(tag, x0 - 0.2, ym) else None)


def touching(tag, r, tol=0.06):
    """Sides of rectangle r that stand against a wall face."""
    sides = set()
    for w in all_walls(tag):
        ox = min(r[2], w[2]) - max(r[0], w[0])
        oy = min(r[3], w[3]) - max(r[1], w[1])
        if ox > 0.05:
            if abs(r[1] - w[3]) <= tol:
                sides.add("S")
            if abs(r[3] - w[1]) <= tol:
                sides.add("N")
        if oy > 0.05:
            if abs(r[0] - w[2]) <= tol:
                sides.add("W")
            if abs(r[2] - w[0]) <= tol:
                sides.add("E")
    return sides


OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}


def back_side(tag, r, tol=0.06):
    """The wall side of a unit: its long side against a wall, else any wall side."""
    s = touching(tag, r, tol)
    long_sides = ("S", "N") if (r[2] - r[0]) >= (r[3] - r[1]) else ("W", "E")
    for side in long_sides:
        if side in s:
            return side
    return next(iter(sorted(s)), long_sides[0])


# --------------------------------------------------------------------------------------- walls
def is_lift_door(op):
    return op == floors.LIFT_DOOR


def glazing(s, r, z0, z1, g, kind, top_frame=True):
    """Glass pane on the wall centre line with a slim dark frame (and a middle bar if wide)."""
    horiz = (r[2] - r[0]) >= (r[3] - r[1])
    fw, fd = 0.05, 0.07
    if horiz:
        ym = (r[1] + r[3]) / 2
        s.box(r[0], ym - 0.012, z0, r[2], ym + 0.012, z1, "glass", g)
        s.box(r[0], ym - fd / 2, z0, r[0] + fw, ym + fd / 2, z1, "frame", g)
        s.box(r[2] - fw, ym - fd / 2, z0, r[2], ym + fd / 2, z1, "frame", g)
        s.box(r[0], ym - fd / 2, z0, r[2], ym + fd / 2, z0 + fw, "frame", g)
        if top_frame:
            s.box(r[0], ym - fd / 2, z1 - fw, r[2], ym + fd / 2, z1, "frame", g)
        if r[2] - r[0] > 1.6 or kind == "slide":
            xm = (r[0] + r[2]) / 2
            s.box(xm - fw / 2, ym - fd / 2, z0, xm + fw / 2, ym + fd / 2, z1, "frame", g)
    else:
        xm = (r[0] + r[2]) / 2
        s.box(xm - 0.012, r[1], z0, xm + 0.012, r[3], z1, "glass", g)
        s.box(xm - fd / 2, r[1], z0, xm + fd / 2, r[1] + fw, z1, "frame", g)
        s.box(xm - fd / 2, r[3] - fw, z0, xm + fd / 2, r[3], z1, "frame", g)
        s.box(xm - fd / 2, r[1], z0, xm + fd / 2, r[3], z0 + fw, "frame", g)
        if top_frame:
            s.box(xm - fd / 2, r[1], z1 - fw, xm + fd / 2, r[3], z1, "frame", g)
        if r[3] - r[1] > 1.6 or kind == "slide":
            ym = (r[1] + r[3]) / 2
            s.box(xm - fd / 2, ym - fw / 2, z0, xm + fd / 2, ym + fw / 2, z1, "frame", g)


def lift_doors(s, r, z0, z1, g):
    horiz = (r[2] - r[0]) >= (r[3] - r[1])
    if horiz:
        ym, xm = (r[1] + r[3]) / 2, (r[0] + r[2]) / 2
        s.box(r[0], ym - 0.02, z0, xm - 0.005, ym + 0.02, z1, "steel", g)
        s.box(xm + 0.005, ym - 0.02, z0, r[2], ym + 0.02, z1, "steel", g)
    else:
        xm, ym = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        s.box(xm - 0.02, r[1], z0, xm + 0.02, ym - 0.005, z1, "steel", g)
        s.box(xm - 0.02, ym + 0.005, z0, xm + 0.02, r[3], z1, "steel", g)


def build_wall(s, w, ops, z0, H, mat, g, cut, cap=None, ext=True):
    """Wall rectangle w standing from z0 to z0 + H, with its openings. In cut mode doors and plain
    openings run to the top of the cut, so they read clearly from above. cap limits window heads
    (first-floor south and north windows stop at 1.95 m, under the eaves, as on the elevations)."""
    cuts = []
    for op in ops:
        o = op[1:5]
        if o[0] >= w[2] or o[2] <= w[0] or o[1] >= w[3] or o[3] <= w[1]:
            continue
        cuts.append(o)
        r = (max(o[0], w[0]), max(o[1], w[1]), min(o[2], w[2]), min(o[3], w[3]))
        if op[0] in ("door", "pivot", "opening"):
            head = 2.1 if op[0] == "opening" else heights(op)[1]
            if not cut:
                s.box(r[0], r[1], z0 + head, r[2], r[3], z0 + H, mat, g)
            continue
        if op[0] == "slide" and not ext and not is_lift_door(op):     # inside sliding door: solid
            if (r[2] - r[0]) >= (r[3] - r[1]):
                ym = (r[1] + r[3]) / 2
                s.box(r[0], ym - 0.02, z0, r[2], ym + 0.02, z0 + min(2.1, H), "door", g)
            else:
                xm = (r[0] + r[2]) / 2
                s.box(xm - 0.02, r[1], z0, xm + 0.02, r[3], z0 + min(2.1, H), "door", g)
            if not cut and H > 2.1:
                s.box(r[0], r[1], z0 + 2.1, r[2], r[3], z0 + H, mat, g)
            continue
        h0, h1 = heights(op)
        if cap and op[0] == "window":
            h1 = min(h1, cap)
        if is_lift_door(op):
            h1 = 2.1
            lift_doors(s, r, z0, z0 + min(h1, H), g)
        if h0 > 0:
            s.box(r[0], r[1], z0, r[2], r[3], z0 + min(h0, H), mat, g)
        if h1 < H:
            s.box(r[0], r[1], z0 + h1, r[2], r[3], z0 + H, mat, g)
        if h0 < H and not is_lift_door(op):
            glazing(s, r, z0 + h0, z0 + min(h1, H), g, op[0], top_frame=h1 <= H)
    for piece in split_rect(w, cuts):
        s.box(piece[0], piece[1], z0, piece[2], piece[3], z0 + H, mat, g)
    return split_rect(w, cuts)


def cut_walls(s, tag):
    """Furnished-view walls: inside walls 2.4 m; outside walls 2.4 m plus a low (0.6 m) version,
    grouped by the side they face, so the viewer can drop the walls facing the camera."""
    f, z0 = FLOOR[tag], LEVEL[tag]
    for w in ext_walls(tag):
        side = outward(tag, w)
        cap = 1.95 if tag == "T" and side in ("N", "S") else None
        build_wall(s, w, f["openings"], z0, CUT, "wall", f"{tag}.hi{side}", True, cap)
        build_wall(s, w, f["openings"], z0, LOW, "wall", f"{tag}.lo{side}", True, cap)
    for w in f["walls"]:
        build_wall(s, w, f["openings"], z0, CUT, "wall", f"{tag}.cut", True, ext=False)


def wall_ao(s, tag):
    """Soft shadow strips on the floor along the foot of every wall."""
    f, z0 = FLOOR[tag], LEVEL[tag]
    cuts = [op[1:5] for op in f["openings"]]
    width = 0.32
    for w in all_walls(tag):
        for p in split_rect(w, cuts):
            horiz = (p[2] - p[0]) >= (p[3] - p[1])
            if horiz:
                if p[2] - p[0] < 0.12:
                    continue
                xm = (p[0] + p[2]) / 2
                if floored(tag, xm, p[3] + 0.15):
                    s.ao.append([p[0], p[3], p[2], p[3] + width, z0, "N", tag])
                if floored(tag, xm, p[1] - 0.15):
                    s.ao.append([p[0], p[1] - width, p[2], p[1], z0, "S", tag])
            else:
                if p[3] - p[1] < 0.12:
                    continue
                ym = (p[1] + p[3]) / 2
                if floored(tag, p[2] + 0.15, ym):
                    s.ao.append([p[2], p[1], p[2] + width, p[3], z0, "E", tag])
                if floored(tag, p[0] - 0.15, ym):
                    s.ao.append([p[0] - width, p[1], p[0], p[3], z0, "W", tag])


def gable_outline(ya, yb, z0=3.0):
    """(y, z) outline of a first-floor north-south wall from ya to yb, up to the roof."""
    pts = [(ya, z0), (yb, z0), (yb, under(yb))]
    if ya < YM < yb:
        pts.append((YM, RIDGE))
    pts.append((ya, under(ya)))
    return pts


def hole(y0, y1, z0, z1, pad=0.08):
    """Rectangular window hole in a gable, kept under the roof line."""
    return [(y0, z0), (y1, z0), (y1, min(z1, under(y1) - pad)), (y0, min(z1, under(y0) - pad))]


def full_walls(s):
    """Whole-house walls: basement and ground floor walls 3.0 m, first floor up to the roof."""
    for tag in ("B", "G"):
        f, z0 = FLOOR[tag], LEVEL[tag]
        for w in ext_walls(tag):
            build_wall(s, w, f["openings"], z0, 3.0, "stone" if tag == "B" else "render",
                       f"{tag}.full", False)
        for w in f["walls"]:
            build_wall(s, w, f["openings"], z0, 2.7, "wall", f"{tag}.full", False, ext=False)
    # first floor: east-west walls as boxes under the roof, north-south outside walls as gables
    f = FLOOR["T"]
    gables = {(4.0, 4.3): (Y0, Y1), (14.9, 15.2): (Y0, TERRACE[1]), (12.9, 13.2): (TERRACE[1] + T, Y1)}
    for w in ext_walls("T"):
        horiz = (w[2] - w[0]) >= (w[3] - w[1])
        if not horiz:
            continue
        x0, x1 = w[0], w[2]
        for (gx0, gx1), (gy0, gy1) in gables.items():
            if gy0 - 1e-6 <= w[1] and w[3] <= gy1 + 1e-6:
                if abs(x0 - gx0) < 1e-6:
                    x0 = gx1
                if abs(x1 - gx1) < 1e-6:
                    x1 = gx0
        top = min(under(w[1]), under(w[3]))
        build_wall(s, (x0, w[1], x1, w[3]), f["openings"], 3.0, top - 3.0, "render", "T.full", False,
                   cap=1.95 if outward("T", w) in ("N", "S") else None)
    for w in f["walls"]:
        top = min(under(w[1]), under(w[3]), 3.0 + 2.7) - 0.02
        build_wall(s, w, f["openings"], 3.0, top - 3.0, "wall", "T.full", False, ext=False)
    # gables with window holes; glass fills the holes
    west_holes = [hole(9.2, 11.7, 3.3, 5.7), hole(7.45, 8.65, 3.9, 5.2)]
    east_holes = [hole(5.8, 8.95, 3.1, 5.5),
                  [(6.4, 5.65), (8.95, 5.65), (8.95, under(8.95) - 0.15), (YM, RIDGE - 0.15),
                   (6.4, under(6.4) - 0.15)]]
    terr_holes = [hole(9.9, 11.7, 3.0, 5.4)]
    for (x0, x1), (ya, yb) in gables.items():
        holes = west_holes if x0 == 4.0 else (east_holes if x0 == 14.9 else terr_holes)
        s.prisms.append({"x0": x0, "x1": x1, "outer": gable_outline(ya, yb), "holes": holes,
                         "m": "render", "g": "T.full"})
        for h in holes:
            xm = (x0 + x1) / 2
            s.prisms.append({"x0": xm - 0.012, "x1": xm + 0.012, "outer": h, "holes": [],
                             "m": "glass", "g": "T.full"})
            if len(h) == 5:                          # glazed gable top: frame its outline
                pts = h + [h[0]]
                for (ya_, za), (yb_, zb) in zip(pts, pts[1:]):
                    dy, dz = yb_ - ya_, zb - za
                    n = math.hypot(dy, dz)
                    ny, nz = -dz / n * 0.05, dy / n * 0.05      # towards the inside of the glass
                    s.prisms.append({"x0": xm - 0.035, "x1": xm + 0.035, "m": "frame", "g": "T.full",
                                     "holes": [], "outer": [(ya_, za), (yb_, zb), (yb_ + ny, zb + nz),
                                                            (ya_ + ny, za + nz)]})
                s.box(xm - 0.035, 7.675, 5.65, xm + 0.035, 7.725, under(7.7) - 0.15, "frame", "T.full")
            if len(h) == 4:                          # rectangular windows get a frame
                ya_, yb_ = h[0][0], h[1][0]
                za, zb = h[0][1], min(h[2][1], h[3][1])
                for r in ((ya_, za, ya_ + 0.05, zb), (yb_ - 0.05, za, yb_, zb),
                          (ya_, za, yb_, za + 0.05), (ya_, zb - 0.05, yb_, zb)):
                    s.box(xm - 0.035, r[0], r[1], xm + 0.035, r[2], r[3], "frame", "T.full")
    # wood cladding around the entrance, on the road (west) face
    for r in ((7.15, 0.0, 7.45, 5.45), (8.65, 0.0, 8.95, 5.45), (7.45, 2.5, 8.65, 3.9),
              (7.45, 5.2, 8.65, 5.45)):
        s.box(X0 - 0.04, r[0], r[1], X0, r[2], r[3], "cladding", "G.full")
    # stone plinth under the ground floor where the basement is not dug
    s.box(X0, Y0, -1.0, UNDUG[2], Y0 + T, 0.0, "stone", "G.full")


# --------------------------------------------------------------------------------------- floors
def slabs_and_finishes(s):
    for tag, z0 in LEVEL.items():
        if tag == "B":
            plate, holes = (X0, Y0, X1, Y1), [UNDUG]
            base = rect_minus(INNER, [(X0, Y0, UNDUG[2] + T, UNDUG[3] + T)])
        else:
            plate, holes = (X0, Y0, X1, Y1), [geom.STAIR, geom.LIFT]
            base = rect_minus(INNER, [geom.STAIR, geom.LIFT])
        for p in rect_minus(plate, holes):
            s.box(p[0], p[1], z0 - 0.3, p[2], p[3], z0, "slab", tag)
        for p in base:
            s.quads.append([p[0], p[1], p[2], p[3], z0 + 0.001, BASE_FINISH[tag], tag])
        for r, m in FINISH[tag]:
            e = 0.05
            s.quads.append([r[0] - e, r[1] - e, r[2] + e, r[3] + e, z0 + 0.002, m, tag])
    s.quads.append([DECK[0], DECK[1], DECK[2], DECK[3], 3.0 + 0.001, "deck", "T"])


def undug_soil(s):
    """The corner under the entrance is not dug out: shown as soil."""
    s.box(UNDUG[0], UNDUG[1], -3.3, UNDUG[2], UNDUG[3], -2.6, "earth", "B")


def stairs(s):
    """U-stair: 2 flights of 9 risers (17 cm) per floor, landing at the north end."""
    x0, ya, x1, yb = geom.STAIR
    xm = (x0 + x1) / 2
    land = yb - geom.STAIR_LANDING
    run = (land - ya) / 8
    rise = 3.0 / 18

    def flights(zf, groups, clip=None, low=None):
        for i in range(8):
            for xa, xb, y_lo, y_hi, top in (
                    (x0 + 0.02, xm - 0.05, ya + i * run, ya + (i + 1) * run, zf + (i + 1) * rise),
                    (xm + 0.05, x1 - 0.02, land - (i + 1) * run, land - i * run, zf + 1.5 + (i + 1) * rise)):
                if (clip is not None and top > clip) or (low is not None and top < low):
                    continue
                for g in groups:
                    s.box(xa, y_lo, top - 0.05, xb, y_hi, top, "oak", g)
        for g in groups:
            if low is not None and zf + 1.5 < low:
                continue
            s.box(x0, land, zf + 1.5 - 0.2, x1, yb, zf + 1.5 - 0.04, "slabedge", g)
            s.box(x0, land, zf + 1.5 - 0.04, x1, yb, zf + 1.5, "oak", g)

    flights(-3.0, ["B.full"])
    flights(-3.0, ["B.cut"], clip=-3.0 + CUT)
    flights(0.0, ["G.full"])
    flights(0.0, ["G.cut"], clip=CUT)
    flights(-3.0, ["G.cut"], low=-1.2)       # the top of the flight below, seen through the opening
    flights(0.0, ["T.cut"], low=1.8)
    # spine wall between the flights; it is the guard on the first floor
    for g, za, zb in (("B.cut", -3.0, -3.0 + CUT), ("G.cut", -1.2, CUT), ("T.cut", 1.8, 4.0),
                      ("B.full", -3.0, 0.0), ("G.full", 0.0, 3.0), ("T.full", 3.0, 4.0)):
        s.box(xm - 0.05, ya, za, xm + 0.05, land, zb, "wall", g)
    # stairwell walls under the opening, so the flights below stay inside the building
    for g, za, zb in (("G.cut", -1.2, -0.3), ("T.cut", 1.8, 2.7)):
        for r in ((X0, ya - 0.1, x0, Y1), (X0, yb, x1 + 0.1, Y1), (x1, ya - 0.1, x1 + 0.1, yb),
                  (x0, ya - 0.1, x1, ya)):
            s.box(r[0], r[1], za, r[2], r[3], zb, "wall", g)
        s.box(x0, ya, za - 0.05, x1, yb, za, "slab", g)
    # first floor: glass guard across the open flight below
    for g in ("T.cut", "T.full"):
        s.box(x0, ya - 0.02, 3.0, xm - 0.05, ya + 0.02, 4.0, "glass", g)
        s.box(x0, ya - 0.03, 3.95, xm - 0.05, ya + 0.03, 4.0, "frame", g)


def lift(s):
    lx0, ly0, lx1, ly1 = geom.LIFT
    for tag, z0 in LEVEL.items():
        s.box(lx0 + 0.04, ly0 + 0.04, z0 - 0.06, lx1 - 0.04, ly1 - 0.04, z0, "steel", tag)
        s.box(lx0 + 0.04, ly1 - 0.08, z0, lx1 - 0.04, ly1 - 0.04, z0 + 2.15, "liftcab", tag)
        s.box(lx0 + 0.04, ly0 + 0.12, z0, lx0 + 0.08, ly1 - 0.04, z0 + 2.15, "liftcab", tag)
        s.box(lx1 - 0.08, ly0 + 0.12, z0, lx1 - 0.04, ly1 - 0.04, z0 + 2.15, "liftcab", tag)
        s.box(lx0 + 0.1, ly1 - 0.12, z0 + 0.9, lx1 - 0.1, ly1 - 0.09, z0 + 0.94, "chrome", tag)


def door_leaves(s):
    """Inside doors stand open at 90 degrees (inside the swing kept clear on the plans); outside
    doors are shown shut."""
    for tag, z0 in LEVEL.items():
        f = FLOOR[tag]
        ext = ext_walls(tag)
        for op in f["openings"]:
            if op[0] not in ("door", "pivot"):
                continue
            x0, y0, x1, y1 = op[1:5]
            wall = next((w for w in ext if min(x1, w[2]) - max(x0, w[0]) > 0.01
                         and min(y1, w[3]) - max(y0, w[1]) > 0.01), None)
            if wall:                                  # outside door: shut, cut with its wall
                side = outward(tag, wall)
                h, m = (2.48, "cladding") if op[0] == "pivot" else (heights(op)[1] - 0.02, "doorext")
                for g, top in ((f"{tag}.hi{side}", min(h, CUT - 0.01)), (f"{tag}.lo{side}", min(h, LOW - 0.01)),
                               (f"{tag}.full", h)):
                    if (x1 - x0) >= (y1 - y0):
                        ym = (y0 + y1) / 2
                        s.box(x0 + 0.01, ym - 0.03, z0, x1 - 0.01, ym + 0.03, z0 + top, m, g)
                    else:
                        xm = (x0 + x1) / 2
                        s.box(xm - 0.03, y0 + 0.01, z0, xm + 0.03, y1 - 0.01, z0 + top, m, g)
                        if op[0] == "pivot" and top > 1.9:
                            s.box(xm + 0.03, y0 + 0.12, z0 + 0.9, xm + 0.06, y0 + 0.15, z0 + 1.9, "frame", g)
                            s.box(xm - 0.06, y0 + 0.12, z0 + 0.9, xm - 0.03, y0 + 0.15, z0 + 1.9, "frame", g)
                continue
            _, x0, y0, x1, y1, at_end, sw = op
            h = heights(op)[1] - 0.02
            t = 0.04
            if (x1 - x0) >= (y1 - y0):
                width, face = x1 - x0, (y1 if sw > 0 else y0)
                hx = x1 if at_end else x0
                xa, xb = (hx - t, hx) if at_end else (hx, hx + t)
                ya_, yb_ = sorted((face, face + sw * (width - 0.02)))
                s.box(xa, ya_, z0, xb, yb_, z0 + h, "door", tag)
            else:
                width, face = y1 - y0, (x1 if sw > 0 else x0)
                hy = y1 if at_end else y0
                ya_, yb_ = (hy - t, hy) if at_end else (hy, hy + t)
                xa, xb = sorted((face, face + sw * (width - 0.02)))
                s.box(xa, ya_, z0, xb, yb_, z0 + h, "door", tag)


def terrace(s):
    tx0, ty0, tx1, ty1 = TERRACE
    for g, top in (("T.cut", CUT), ("T.full", EAVE - 3.0)):
        s.box(tx1 - T, ty1 - T, 3.0, tx1, ty1, 3.0 + top, "render", g)          # corner post
    # glass railing on the open sides, shared by both views
    for r in ((tx1 - 0.05, ty0 + T, tx1 - 0.02, ty1 - T), (tx0 + T, ty1 - 0.05, tx1 - T, ty1 - 0.02)):
        s.box(r[0], r[1], 3.0, r[2], r[3], 4.0, "glass", "T")
    s.box(tx1 - 0.06, ty0 + T, 3.96, tx1 - 0.01, ty1 - T, 4.02, "frame", "T")
    s.box(tx0 + T, ty1 - 0.06, 3.96, tx1 - T, ty1 - 0.01, 4.02, "frame", "T")


# --------------------------------------------------------------------------------------- furniture
def furniture(s):
    for tag, z0 in LEVEL.items():
        fu = FLOOR[tag].get("furniture", {})

        def add(k, **kw):
            item = dict(k=k, f=tag, z=z0)
            item.update(kw)
            s.items.append(item)

        for b in fu.get("bed", []):
            add("bed", r=list(b[:4]), d=OPP[b[4] if len(b) > 4 else "N"])
        for r in fu.get("counter", []):
            kind = COUNTER_KIND[tuple(r)]
            item = dict(r=list(r), d=OPP[back_side(tag, r)])
            if kind == "shoe":
                item["h"] = SHOE_HEIGHT.get(tuple(r), 1.0)
            if kind == "kitchen":                    # sink under the middle of the window behind
                for op in FLOOR[tag]["openings"]:
                    if op[0] == "window" and min(op[3], r[2]) - max(op[1], r[0]) > 0.5 \
                            and min(abs(op[2] - r[3]), abs(op[4] - r[1])) < 0.2:
                        item["sink"] = [(max(op[1], r[0]) + min(op[3], r[2])) / 2, (r[1] + r[3]) / 2]
            add(kind, **item)
        for r in fu.get("fridge", []):
            add("fridge", r=list(r), d=OPP[back_side(tag, r)])
        for r in fu.get("island", []):
            add("sauna" if tag == "B" else "island", r=list(r))
        for r in fu.get("table", []):
            add("billiards" if tag == "B" else "coffee", r=list(r))
        for r in fu.get("sofa", []):
            add("sofa", r=list(r), d=OPP[back_side(tag, r, tol=0.2)])
        for x0, y0, x1, y1, wall in fu.get("tv", []):
            add("tv", r=[x0, y0, x1, y1], d=OPP[wall])
        for i, r in enumerate(fu.get("tub", [])):
            add("jacuzzi" if i == 0 else "plunge", r=list(r))
        for r in fu.get("shower", []):
            add("shower", r=list(r), open=sorted({"N", "S", "E", "W"} - touching(tag, r)))
        for x, y, d in fu.get("wc", []):
            add("wc", p=[x, y], d=d)
        for x, y, d in fu.get("squat", []):
            add("squat", p=[x, y], d=d)
        for r in fu.get("basin", []):
            add("basin", r=list(r), d=OPP[back_side(tag, r)])
        for item in DECOR[tag]:
            it = {k: (list(v) if isinstance(v, tuple) else v) for k, v in item.items()}
            add(it.pop("k"), **it)


def labels(s):
    for tag, z0 in LEVEL.items():
        f = FLOOR[tag]
        for en, alt_name, r, at in f["rooms"]:
            x, y = at or ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
            s.labels.append({"en": en, "alt": alt_name, "p": [x, y, z0 + 0.05], "f": tag})
        en, alt_name, _, _, at = f["open_space"]
        s.labels.append({"en": en, "alt": alt_name, "p": [at[0], at[1], z0 + 0.05], "f": tag})
        s.labels.append({"en": "Stairs", "alt": "پله", "p": [5.4, 10.4, z0 + 0.05], "f": tag})
    s.labels.append({"en": "Covered terrace", "alt": "تراس مسقف", "p": [14.2, 11.9, 3.05], "f": "T"})
    s.labels.append({"en": "Not dug out (soil)", "alt": "بدون گودبرداری", "p": [6.3, 6.3, -2.55], "f": "B"})
    for en, alt_name, p in (("Front door", "در ورودی", (3.55, 8.05, 1.3)),
                           ("Carport", "سایبان پارکینگ", (3.8, 2.6, 2.8)),
                           ("South patio", "محوطه جنوبی", (13.4, 4.4, 0.1)),
                           ("Lower garden", "باغ پایین", (19.0, 7.5, -2.9))):
        s.labels.append({"en": en, "alt": alt_name, "p": list(p), "f": "S"})


# --------------------------------------------------------------------------------------- roof and site
def roof(s):
    s.roof = {"x0": X0 - O, "x1": X1 + O, "yS": Y0 - O, "yN": Y1 + O, "yM": YM,
              "zE": EAVE - O * PITCH, "zR": RIDGE, "t": ROOF_T,
              "windows": [[5.0, 6.0], [8.3, 9.3], [9.8, 10.8]], "wy": [10.42, 11.61]}


CARPORT = geom.CARPORT
PATIO = geom.PATIO_SOUTH


def finished_ground(x, y):
    """Ground after building. Each level change sits between two grid lines 1 cm apart inside a
    wall, so every step hides in that wall."""
    if inside((X0 + 0.065, Y0 + 0.065, X1 - 0.065, Y1 - 0.065), x, y, 0):
        return -0.35 if inside(UNDUG, x, y) else -3.35
    if not (0.0 <= y <= 14.23 and geom.west_x(y) <= x <= geom.east_x(y)):
        return round(geom.ground_level(x, y), 3)       # outside the plot: natural slope
    if x <= X0 + 0.065:
        return 0.0
    if CARPORT[0] <= x <= CARPORT[2] + 0.065 and y <= Y0 + 0.065:
        return 0.0
    if PATIO[0] + 0.065 <= x <= PATIO[2] - 0.065 and PATIO[1] + 0.065 <= y <= PATIO[3]:
        return 0.0
    if x >= X1 - 0.065 and y >= 1.0:
        return -3.0
    return round(geom.ground_level(x, y), 3)


def site(s):
    bx = [X0 + 0.06, X0 + 0.07, X1 - 0.07, X1 - 0.06, CARPORT[2] + 0.06, CARPORT[2] + 0.07,
          PATIO[0] + 0.06, PATIO[0] + 0.07]
    by = [Y0 + 0.06, Y0 + 0.07, Y1 - 0.07, Y1 - 0.06, PATIO[1] + 0.06, PATIO[1] + 0.07, 0.99, 1.0]
    xs = sorted({round(-14 + 0.5 * i, 3) for i in range(105)} | {round(v, 3) for v in bx})
    ys = sorted({round(-12 + 0.5 * j, 3) for j in range(76)} | {round(v, 3) for v in by})
    s.terrain = {"xs": xs, "ys": ys, "z": [[finished_ground(x, y) for x in xs] for y in ys]}
    s.plot = geom.PLOT
    g = "S"
    s.box(-9.0, -12.0, -0.06, -0.25, 26.0, 0.02, "road", g)
    # retaining walls where levelled ground meets the natural slope (stone, 4 cm coping lip)
    north_east_top = round(geom.ground_level(X1, 13.3), 2) + 0.1
    for r, za, zb in (((PATIO[0], PATIO[1], PATIO[2], PATIO[1] + 0.25), -2.6, 0.04),
                      ((PATIO[0], PATIO[1], PATIO[0] + 0.25, PATIO[3]), -1.9, 0.04),
                      ((PATIO[2] - 0.25, PATIO[1], PATIO[2], PATIO[3]), -3.0, 0.04),
                      ((CARPORT[2], 0.0, CARPORT[2] + 0.25, Y0), -1.2, 0.04),
                      ((X1 - 0.25, Y1, X1, 14.23), -3.0, north_east_top),
                      ((X0, Y1, X0 + 0.25, 14.23), -0.9, 0.04)):
        s.box(r[0], r[1], za, r[2], r[3], zb, "stonewall", g)
    # paving: south patio, path from the gate, carport floor
    s.box(PATIO[0] + 0.25, PATIO[1] + 0.25, -0.05, PATIO[2] - 0.25, PATIO[3], 0.02, "pave", g)
    s.box(geom.west_x(8.6), 7.45, -0.04, X0, 8.6, 0.025, "pave", g)
    s.box(CARPORT[0], CARPORT[1], -0.04, CARPORT[2], CARPORT[3], 0.015, "concrete", g)
    # steps beside the patio, from its level at the north end down to the lower garden
    st, n = geom.PATIO_STEPS, 9
    d = (st[3] - st[1]) / n
    for i in range(n):
        s.box(st[0], st[3] - (i + 1) * d, -3.0, st[2], st[3] - i * d, -i * 3.0 / n, "stonewall", g)
    # carport: four posts and a slatted roof
    c = CARPORT
    for px, py in ((c[0], c[1]), (c[2] - 0.12, c[1]), (c[0], c[3] - 0.12), (c[2] - 0.12, c[3] - 0.12)):
        s.box(px, py, 0.0, px + 0.12, py + 0.12, 2.5, "frame", g)
    s.box(c[0] - 0.15, c[1] - 0.15, 2.5, c[2] + 0.15, c[3] + 0.15, 2.62, "frame", g)
    s.cars = [[x, y, k] for x, y, k in CARS]
    s.trees = [list(t) for t in TREES]
    s.conifers = [list(t) for t in CONIFERS]
    s.patio = list(PATIO_SET)


def build():
    s = Scene()
    for tag in LEVEL:
        cut_walls(s, tag)
        wall_ao(s, tag)
    full_walls(s)
    slabs_and_finishes(s)
    undug_soil(s)
    stairs(s)
    lift(s)
    door_leaves(s)
    terrace(s)
    furniture(s)
    labels(s)
    roof(s)
    site(s)
    return {"center": [round((X0 + X1) / 2, 3), round((Y0 + Y1) / 2, 3)],
            "levels": LEVEL, "cut": CUT, "house": [X0, Y0, X1, Y1],
            "boxes": s.boxes, "prisms": s.prisms, "quads": s.quads, "ao": s.ao,
            "items": s.items, "labels": s.labels, "roof": s.roof, "terrain": s.terrain,
            "plot": s.plot, "cars": s.cars, "trees": s.trees, "conifers": s.conifers,
            "patio": s.patio}
