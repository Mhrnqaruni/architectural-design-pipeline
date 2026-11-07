"""Site plan: boundary, slope contours, house and roof, carport, gates, patio, garden."""
import math

from . import geom
from .plans import draw_level


def _side_label(pen, a, b, text, out=0.55):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n, dx / n                     # outward normal for a clockwise boundary
    ang = math.degrees(math.atan2(dy, dx))
    if ang > 90 or ang < -90:
        ang += 180
    pen.text(text, (mx + nx * out, my + ny * out), h=2.4, rot=ang, layer="A-SITE")


def contours(pen):
    for i in range(1, 6):
        lvl = -0.5 * i
        t = -lvl / 3.0
        a = (1.11 + t * 18.65, 0.0)
        b = (0.0 + t * 24.64, 14.23)
        pen.poly([a, b], "A-SITE-PLNT", linetype="DASHED", ltscale=3)
        pen.text(f"{lvl:.2f}", (b[0] - (b[0] - a[0]) * 0.03 + 0.25, 13.8), h=1.5, rot=72,
                 layer="A-SITE-PLNT")


def car(pen, x, y):
    """A car parked east-west, front to the east."""
    pen.rect((x, y, x + 4.7, y + 1.9), "A-FURN")
    pen.rect((x + 1.3, y + 0.2, x + 3.4, y + 1.7), "A-FURN")


def gate(pen, y0, y1, text):
    a, b = (geom.west_x(y0), y0), (geom.west_x(y1), y1)
    pen.poly([a, b], "A-SITE", linetype="DASHED", ltscale=3, lineweight=50)
    for p in (a, b):
        pen.line((p[0] - 0.25, p[1]), (p[0] + 0.25, p[1]), "A-SITE")
    pen.text(text, (geom.west_x((y0 + y1) / 2) - 0.45, (y0 + y1) / 2), h=1.8, rot=90)


def draw_site(pen):
    pts = geom.PLOT
    pen.poly(pts, "A-SITE", close=True, lineweight=70)
    for (a, b), key in zip(zip(pts, pts[1:] + pts[:1]), ("N", "E", "S", "W")):
        _side_label(pen, a, b, f"{geom.PLOT_SIDES[key]:.2f}")
    contours(pen)

    # lower east garden, levelled at -3.00
    pen.poly(geom.LOWER_GARDEN, "A-SITE", close=True, linetype="DASHED", ltscale=4)
    pen.text("Lower garden -3.00 (levelled)", (19.3, 8.8), h=2.0, rot=72)
    pen.text("باغ پایین", (20.4, 8.4), h=2.0, rtl=True, rot=72)

    # house footprint, roof and ridge
    x0, y0, x1, y1 = geom.HOUSE
    o = geom.ROOF_OVERHANG
    pen.fill_rect(geom.HOUSE, "A-WALL-PATT", color=254)
    pen.rect(geom.HOUSE, "A-WALL")
    pen.rect((x0 - o, y0 - o, x1 + o, y1 + o), "A-ROOF", linetype="DASHED", ltscale=6)
    ym = (y0 + y1) / 2
    pen.line((x0 - o, ym), (x1 + o, ym), "A-ROOF")
    pen.text("HOUSE", ((x0 + x1) / 2, ym + 0.95), h=3.0)
    pen.text("خانه", ((x0 + x1) / 2, ym + 0.4), h=3.0, rtl=True)
    pen.text("Ridge +7.40", (x1 - 1.4, ym + 0.25), h=1.7, layer="A-ROOF")
    pen.text("3 floors: -3.00 / ±0.00 / +3.00", ((x0 + x1) / 2, ym - 0.5), h=1.8)
    pen.text("Front door", (x0 + 1.1, 8.03), h=1.5)

    # carport with two cars parked east-west, and the gates on the road
    pen.rect(geom.CARPORT, "A-ROOF", linetype="DASHED", ltscale=6)
    car(pen, 1.5, 0.45)
    car(pen, 1.5, 2.95)
    pen.text("Carport, 2 cars", (2.2, 5.75), h=2.0)
    pen.text("سایبان پارکینگ", (2.2, 6.25), h=2.0, rtl=True)
    gate(pen, *geom.GATE_CAR, "Car gate (sliding)")
    gate(pen, *geom.GATE_WALK, "Gate")
    pen.rect((geom.west_x(8.6), 7.45, x0, 8.6), "A-SITE")
    pen.text("ROAD (WEST)", (-1.6, 7.1), h=2.6, rot=90)
    pen.text("Front yard ±0.00", (2.2, 11.2), h=1.8)

    # raised south patio with its retaining wall, and steps down to the lower garden
    sx0, sy0, sx1, sy1 = geom.PATIO_SOUTH
    pen.rect(geom.PATIO_SOUTH, "A-SITE")
    pen.poly([(sx0, sy0), (sx1, sy0), (sx1, sy1)], "A-WALL", lineweight=50)
    pen.text("South patio ±0.00", ((sx0 + sx1) / 2, 3.3), h=2.0)
    pen.text("محوطه صاف جنوبی", ((sx0 + sx1) / 2, 2.8), h=2.0, rtl=True)
    pen.text("retaining wall", ((sx0 + sx1) / 2, sy0 + 0.25), h=1.5)
    st = geom.PATIO_STEPS
    pen.rect(st, "A-SITE")
    for i in range(1, 8):
        yy = st[1] + i * (st[3] - st[1]) / 8
        pen.line((st[0], yy), (st[2], yy), "A-SITE")
    pen.text("Steps down to -3.00", (st[2] + 0.2, (st[1] + st[3]) / 2), h=1.5, align="MIDDLE_LEFT")
    pen.text("Side path, natural slope", (11.8, 13.35), h=1.6)

    # levels
    draw_level(pen, (0.9, 12.6), "±0.00 road")
    draw_level(pen, (21.3, 4.6), "-3.00")
    draw_level(pen, (x0 + 0.7, 6.0), "FFL ±0.00")
    for x, y in ((x0, y1), (x1, y1), (x1, y0), (x0, y0)):
        pen.text(f"NGL {geom.ground_level(x, y):+.2f}", (x, y + (0.35 if y == y1 else -0.35)),
                 h=1.5, layer="A-FLOR-LEVL")

    # distances to the boundaries and the size of the lower garden
    pen.dim((8.6, y1), (8.6, 14.23), 0.0, vertical=True)
    pen.dim((geom.west_x(9.6), 9.6), (x0, 9.6), 0.0)
    pen.dim((x1, 9.6), (geom.east_x(9.6), 9.6), 0.0)
