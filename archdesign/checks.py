"""Plan checks that run before every build; the command-line interface stops if any fails.

1. Reach: walking from inside the front door (or the stair landing on the other floors) through
   doors, sliding doors and openings only, every room must be reachable. The boiler room is the
   one exception: it opens only to the garden, on purpose (gas safety).
2. Door swings: no swing may hit furniture, a fixture, a wall or another swing, and no furniture
   may overlap other furniture or stand in a wall.
"""
import math
from collections import deque

from . import floors, geom, plans
from .cad import split_rect

FLOORS = [("Basement", floors.BASEMENT, (6.0, 8.2)), ("Ground floor", floors.GROUND, (5.0, 8.0)),
          ("First floor", floors.TOP, (5.0, 8.0))]
OUTSIDE_ONLY = {"Boiler room"}
STEP = 0.05


def walls_of(fl):
    return (fl.get("ext_walls") or plans.outer_walls(geom.HOUSE)) + fl["walls"]


def check_reach(name, fl, start):
    x0, y0, x1, y1 = geom.HOUSE
    walls = walls_of(fl)
    passable = [op[1:5] for op in fl["openings"] if op[0] in ("door", "pivot", "opening", "slide")]
    undug = fl.get("undug")
    nx, ny = int(round((x1 - x0) / STEP)), int(round((y1 - y0) / STEP))

    def blocked(i, j):
        x, y = x0 + (i + 0.5) * STEP, y0 + (j + 0.5) * STEP
        if undug and undug[0] <= x <= undug[2] and undug[1] <= y <= undug[3]:
            return True
        if not any(w[0] <= x <= w[2] and w[1] <= y <= w[3] for w in walls):
            return False
        return not any(o[0] <= x <= o[2] and o[1] <= y <= o[3] for o in passable)

    grid = [[blocked(i, j) for j in range(ny)] for i in range(nx)]
    seen = [[False] * ny for _ in range(nx)]
    si, sj = int((start[0] - x0) / STEP), int((start[1] - y0) / STEP)
    seen[si][sj] = True
    q = deque([(si, sj)])
    while q:
        i, j = q.popleft()
        for a, b in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
            if 0 <= a < nx and 0 <= b < ny and not seen[a][b] and not grid[a][b]:
                seen[a][b] = True
                q.append((a, b))
    targets = [(en, at or ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)) for en, _, r, at in fl["rooms"]]
    targets.append((fl["open_space"][0], fl["open_space"][4]))
    missing = [en for en, (x, y) in targets if en not in OUTSIDE_ONLY
               and not seen[int((x - x0) / STEP)][int((y - y0) / STEP)]]
    for en in missing:
        print(f"  {name}: {en} cannot be reached from the entrance")
    return len(missing)


def swings(op):
    """Quarter discs (centre, radius, start angle, end angle) swept by a door."""
    if op[0] == "door":
        _, x0, y0, x1, y1, at_end, s = op
        if (x1 - x0) >= (y1 - y0):
            w, face = x1 - x0, (y1 if s > 0 else y0)
            return [((x1 if at_end else x0, face), w, 90 if s > 0 else 270, 180 if at_end else 0)]
        w, face = y1 - y0, (x1 if s > 0 else x0)
        return [((face, y1 if at_end else y0), w, 0 if s > 0 else 180, 270 if at_end else 90)]
    if op[0] == "pivot":
        _, x0, y0, x1, y1, off = op
        p = ((x0 + x1) / 2, y0 + off)
        return [(p, (y1 - y0) - off, 0, 90), (p, off, 180, 270)]
    return []


def in_quarter(pt, q):
    (cx, cy), r, a, b = q
    dx, dy = pt[0] - cx, pt[1] - cy
    if math.hypot(dx, dy) > r:
        return False
    ang = math.degrees(math.atan2(dy, dx)) % 360
    lo, hi = sorted((a % 360, b % 360))
    return (ang >= hi or ang <= lo) if hi - lo == 270 else lo <= ang <= hi


def fixtures(f):
    out = []
    for k in ("bed", "counter", "island", "table", "sofa", "tub", "shower", "basin", "tv", "fridge"):
        out += [(k, tuple(r[:4])) for r in f.get(k, [])]
    for kind, half, (b0, b1) in (("wc", 0.225, (0.0, 0.68)), ("squat", 0.21, (-0.3, 0.3))):
        for x, y, d in f.get(kind, []):
            fx, fy = plans.DIRS[d]
            pts = [(x + a * fy + b * fx, y - a * fx + b * fy) for a in (-half, half) for b in (b0, b1)]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            out.append((kind, (min(xs), min(ys), max(xs), max(ys))))
    return out


def check_swings(name, fl):
    cuts = [op[1:5] for op in fl["openings"]]
    pieces = [p for w in walls_of(fl) for p in split_rect(w, cuts)]
    fx = fixtures(fl.get("furniture", {}))
    qs = [(op, q) for op in fl["openings"] for q in swings(op)]

    def inside(pt, r, m=0.01):
        return r[0] + m < pt[0] < r[2] - m and r[1] + m < pt[1] < r[3] - m

    n = 0
    for op, q in qs:
        (cx, cy), r = q[0], q[1]
        pts = [p for p in ((cx + r * i / 24 * math.cos(math.radians(t)), cy + r * i / 24 * math.sin(math.radians(t)))
                           for i in range(1, 25) for t in range(0, 360, 3)) if in_quarter(p, q)]
        hits = [k for k, rr in fx if any(inside(p, rr) for p in pts)]
        hits += ["a wall" for wp in pieces if any(inside(p, wp) for p in pts)]
        hits += ["another door" for op2, q2 in qs if op2 is not op and any(in_quarter(p, q2) for p in pts)]
        for h in hits:
            print(f"  {name}: door {op[1:5]} swings into {h}")
        n += len(hits)
    for i, (k, a) in enumerate(fx):
        for k2, b in fx[i + 1:]:
            if min(a[2], b[2]) - max(a[0], b[0]) > 0.01 and min(a[3], b[3]) - max(a[1], b[1]) > 0.01:
                print(f"  {name}: {k} {a} overlaps {k2} {b}")
                n += 1
        for wp in pieces:
            if min(a[2], wp[2]) - max(a[0], wp[0]) > 0.01 and min(a[3], wp[3]) - max(a[1], wp[1]) > 0.01:
                print(f"  {name}: {k} {a} stands in a wall")
                n += 1
    return n


def run_all():
    problems = sum(check_reach(name, fl, start) + check_swings(name, fl) for name, fl, start in FLOORS)
    print("plan checks: every room reachable, no door clashes" if not problems
          else f"plan checks: {problems} problems")
    return problems
