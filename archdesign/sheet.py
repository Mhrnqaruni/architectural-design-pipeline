"""A3 landscape sheet: border, title block strip on the right, north arrow, scale bar."""
from ezdxf.enums import TextEntityAlignment

from .cad import shape_rtl

W, H = 420.0, 297.0
FRAME = (20.0, 10.0, 410.0, 287.0)       # left margin 20 mm for binding
STRIP_X = 345.0                          # title block strip from here to the right frame
DRAW_AREA = (25.0, 15.0, 340.0, 282.0)

PROJECT_EN = "Three-Storey House"
PROJECT_ALT = "خانه سه‌طبقه"
STAGE_EN = "CONCEPT DESIGN - NOT FOR CONSTRUCTION"
STAGE_ALT = "طرح اولیه - برای اجرا نیست"


def _t(msp, s, x, y, h, rtl=False, align="MIDDLE_LEFT", layer="A-ANNO-TTLB"):
    t = msp.add_text(shape_rtl(s) if rtl else s, height=h,
                     dxfattribs={"layer": layer, "style": "ALT" if rtl else "EN"})
    t.set_placement((x, y), align=TextEntityAlignment[align])


def _box(msp, x0, y0, x1, y1, layer="A-ANNO-TTLB"):
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True,
                       dxfattribs={"layer": layer})


def frame(msp, number, title_en, title_alt, scale_text, date="2026-11-07", rev="B"):
    # paper edge in white so renderers fit the page exactly
    msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True,
                       dxfattribs={"layer": "A-ANNO-NPLT", "true_color": 0xFFFFFF})
    _box(msp, *FRAME)
    x0, x1 = STRIP_X, FRAME[2]
    msp.add_line((x0, FRAME[1]), (x0, FRAME[3]), dxfattribs={"layer": "A-ANNO-TTLB"})
    cx = (x0 + x1) / 2
    # project
    _t(msp, PROJECT_EN, cx, 272, 4.2, align="MIDDLE_CENTER")
    _t(msp, PROJECT_ALT, cx, 263, 4.6, rtl=True, align="MIDDLE_CENTER")
    _t(msp, "Hillside lot", cx, 255, 2.0, align="MIDDLE_CENTER")
    msp.add_line((x0, 249), (x1, 249), dxfattribs={"layer": "A-ANNO-TTLB"})
    # stage banner
    _box(msp, x0 + 3, 236, x1 - 3, 246)
    _t(msp, STAGE_EN, cx, 243, 1.6, align="MIDDLE_CENTER")
    _t(msp, STAGE_ALT, cx, 238.8, 2.2, rtl=True, align="MIDDLE_CENTER")
    # notes
    notes = ["Dimensions in metres; levels relative to the road (+/-0.00).",
             "Concept stage: sizes approximate until design development.",
             "Structure, foundations, retaining walls, plumbing and",
             "electrical design by a licensed engineer (phase 1 & 2).",
             "Fixtures and furniture shown schematically."]
    _t(msp, "NOTES", x0 + 3, 228, 2.2)
    for i, n in enumerate(notes):
        _t(msp, n, x0 + 3, 222 - i * 4.2, 1.55)
    # fields
    rows = [("Drawing", title_en), ("", title_alt), ("Scale", scale_text), ("Date", date),
            ("Revision", rev), ("Sheet", number)]
    y = 92
    msp.add_line((x0, y + 6), (x1, y + 6), dxfattribs={"layer": "A-ANNO-TTLB"})
    for label, value in rows:
        if label:
            _t(msp, label, x0 + 3, y, 1.8)
        if label == "" and value:
            _t(msp, value, x1 - 3, y, 3.0, rtl=True, align="MIDDLE_RIGHT")
        elif label == "Sheet":
            _t(msp, value, x1 - 3, y - 6, 9.0, align="MIDDLE_RIGHT")
        elif value:
            size = 2.6 if label != "Drawing" else (3.0 if len(value) <= 20 else 2.3)
            _t(msp, value, x1 - 3, y, size, align="MIDDLE_RIGHT")
        y -= 9 if label != "Sheet" else 0
        msp.add_line((x0, y + 4.5), (x1, y + 4.5), dxfattribs={"layer": "A-ANNO-TTLB"})


def north_arrow(msp, x, y, r=9.0):
    msp.add_circle((x, y), r, dxfattribs={"layer": "A-ANNO-SYMB"})
    pts = [(x, y + r * 0.95), (x - r * 0.35, y - r * 0.6), (x, y - r * 0.25),
           (x + r * 0.35, y - r * 0.6)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "A-ANNO-SYMB"})
    h = msp.add_hatch(color=7, dxfattribs={"layer": "A-ANNO-SYMB"})
    h.paths.add_polyline_path(pts[:3], is_closed=True)
    _t(msp, "N", x, y + r + 4, 3.5, align="MIDDLE_CENTER", layer="A-ANNO-SYMB")


def scale_bar(msp, x, y, scale, metres=5):
    k = 1000.0 / scale
    for i in range(metres):
        x0 = x + i * k
        msp.add_lwpolyline([(x0, y), (x0 + k, y), (x0 + k, y + 2), (x0, y + 2)], close=True,
                           dxfattribs={"layer": "A-ANNO-SYMB"})
        if i % 2 == 0:
            h = msp.add_hatch(color=7, dxfattribs={"layer": "A-ANNO-SYMB"})
            h.paths.add_polyline_path([(x0, y), (x0 + k, y), (x0 + k, y + 2), (x0, y + 2)],
                                      is_closed=True)
        _t(msp, str(i), x0, y - 3, 1.8, align="MIDDLE_CENTER", layer="A-ANNO-SYMB")
    _t(msp, f"{metres} m", x + metres * k, y - 3, 1.8, align="MIDDLE_CENTER", layer="A-ANNO-SYMB")


def view_title(msp, x, y, title_en, title_alt, scale_text):
    _t(msp, title_en.upper(), x, y, 3.2, layer="A-ANNO-TEXT")
    msp.add_line((x, y - 2.8), (x + 110, y - 2.8), dxfattribs={"layer": "A-ANNO-TEXT"})
    _t(msp, title_alt, x + 110, y, 3.4, rtl=True, align="MIDDLE_RIGHT", layer="A-ANNO-TEXT")
    _t(msp, scale_text, x, y - 6, 2.0, layer="A-ANNO-TEXT")
