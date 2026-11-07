"""DXF helpers: layers, text (with right-to-left shaping), and a Pen that maps metres onto paper."""
import math

import arabic_reshaper
import ezdxf
from bidi.algorithm import get_display
from ezdxf.enums import TextEntityAlignment

# Layer names follow the AIA / US National CAD Standard pattern. (name, colour, lineweight 1/100 mm)
LAYERS = [
    ("A-WALL", 7, 50), ("A-WALL-PATT", 8, 0), ("A-DOOR", 7, 25), ("A-GLAZ", 5, 18),
    ("A-FLOR-STRS", 7, 18), ("A-FLOR-LEVL", 7, 13), ("A-FURN", 8, 13), ("A-AREA-IDEN", 7, 18),
    ("A-ANNO-DIMS", 7, 13), ("A-ANNO-TEXT", 7, 18), ("A-ANNO-SYMB", 7, 25),
    ("A-ANNO-TTLB", 7, 35), ("A-ANNO-NPLT", 9, 13), ("A-SITE", 7, 25), ("A-SITE-PLNT", 8, 13),
    ("A-ELEV", 7, 35), ("A-ELEV-HIDD", 8, 13), ("A-SECT", 7, 50), ("A-ROOF", 7, 25),
]


def new_doc():
    doc = ezdxf.new("R2018", setup=True, units=4)  # drawing units: millimetres on paper
    for name, color, lw in LAYERS:
        doc.layers.add(name, color=color, lineweight=lw)
    doc.styles.add("EN", font="arial.ttf")
    doc.styles.add("ALT", font="tahoma.ttf")
    return doc


def shape_rtl(text):
    """Shape right-to-left script so CAD renderers show the letters joined and in reading order."""
    return get_display(arabic_reshaper.reshape(text))


class Pen:
    """Draws world geometry (metres) into a layout at a given scale, offset on the paper (mm)."""

    def __init__(self, layout, origin=(0.0, 0.0), scale=100, world_origin=(0.0, 0.0),
                 text_scale=1.0):
        self.msp, self.ox, self.oy = layout, origin[0], origin[1]
        self.k = 1000.0 / scale          # paper mm per metre (1.0 for a true-size model in m)
        self.wx, self.wy = world_origin
        self.scale = scale
        self.ts = text_scale             # shrinks paper-sized text for a true-size model

    def p(self, x, y):
        return (self.ox + (x - self.wx) * self.k, self.oy + (y - self.wy) * self.k)

    def line(self, a, b, layer):
        self.msp.add_line(self.p(*a), self.p(*b), dxfattribs={"layer": layer})

    def poly(self, pts, layer, close=False, **attrs):
        return self.msp.add_lwpolyline([self.p(*q) for q in pts], close=close,
                                       dxfattribs={"layer": layer, **attrs})

    def rect(self, r, layer, **attrs):
        x0, y0, x1, y1 = r
        return self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, close=True, **attrs)

    def fill(self, pts, layer, color=None):
        h = self.msp.add_hatch(color=color or 7, dxfattribs={"layer": layer})
        h.paths.add_polyline_path([self.p(*q) for q in pts], is_closed=True)
        return h

    def fill_rect(self, r, layer, color=None):
        x0, y0, x1, y1 = r
        return self.fill([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, color)

    def arc(self, c, r, a0, a1, layer):
        self.msp.add_arc(self.p(*c), r * self.k, a0, a1, dxfattribs={"layer": layer})

    def circle(self, c, r, layer):
        self.msp.add_circle(self.p(*c), r * self.k, dxfattribs={"layer": layer})

    def text(self, s, at, h=2.5, layer="A-ANNO-TEXT", rtl=False, align="MIDDLE_CENTER",
             rot=0.0):
        """h is paper height in mm, so labels keep the same size at any scale."""
        t = self.msp.add_text(shape_rtl(s) if rtl else s, height=h * self.ts, rotation=rot,
                              dxfattribs={"layer": layer, "style": "ALT" if rtl else "EN"})
        t.set_placement(self.p(*at), align=TextEntityAlignment[align])
        return t

    def dim(self, a, b, offset, layer="A-ANNO-DIMS", vertical=False):
        """Linear dimension between world points a and b; offset in metres from the points."""
        if vertical:
            base = (a[0] + offset, (a[1] + b[1]) / 2)
            angle = 90
        else:
            base = ((a[0] + b[0]) / 2, a[1] + offset)
            angle = 0
        d = self.msp.add_linear_dim(base=self.p(*base), p1=self.p(*a), p2=self.p(*b),
                                    angle=angle, dimstyle="PLAN",
                                    override={"dimlfac": 1.0 / self.k, "dimscale": self.ts},
                                    dxfattribs={"layer": layer})
        d.render()


def setup_dimstyle(doc):
    ds = doc.dimstyles.new("PLAN")
    ds.dxf.dimtxt = 2.0
    ds.dxf.dimasz = 1.4
    ds.dxf.dimblk = "ARCHTICK"
    ds.dxf.dimexe = 1.0
    ds.dxf.dimexo = 1.0
    ds.dxf.dimdec = 2
    ds.dxf.dimtad = 1
    ds.dxf.dimgap = 0.6
    ds.dxf.dimtxsty = "EN"
    ds.dxf.dimzin = 0
    ds.dxf.dimdsep = ord(".")


def split_rect(w, cuts):
    """Remove the parts of wall rectangle w covered by opening rectangles, along its long axis."""
    x0, y0, x1, y1 = w
    horizontal = (x1 - x0) >= (y1 - y0)
    lo, hi = (x0, x1) if horizontal else (y0, y1)
    spans = [(lo, hi)]
    for c in cuts:
        if c[0] >= x1 or c[2] <= x0 or c[1] >= y1 or c[3] <= y0:
            continue
        a, b = (c[0], c[2]) if horizontal else (c[1], c[3])
        new = []
        for s, e in spans:
            if b <= s or a >= e:
                new.append((s, e))
                continue
            if a > s:
                new.append((s, a))
            if b < e:
                new.append((b, e))
        spans = new
    if horizontal:
        return [(s, y0, e, y1) for s, e in spans if e - s > 1e-6]
    return [(x0, s, x1, e) for s, e in spans if e - s > 1e-6]


def arc_between(a_from, a_to):
    """Order two angles so the arc drawn counter-clockwise is the 90 degree sweep."""
    if (a_to - a_from) % 360 == 90:
        return a_from, a_to
    return a_to, a_from


def deg(v):
    return math.degrees(math.atan2(v[1], v[0])) % 360
