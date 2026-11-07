"""Cover sheet: title, drawing list and an area table computed from the floor data."""
from ezdxf.enums import TextEntityAlignment

from . import areas, floors, geom
from .cad import shape_rtl
from .plans import area


def _t(msp, s, x, y, h, rtl=False, align="MIDDLE_LEFT", layer="A-ANNO-TEXT"):
    t = msp.add_text(shape_rtl(s) if rtl else s, height=h,
                     dxfattribs={"layer": layer, "style": "ALT" if rtl else "EN"})
    t.set_placement((x, y), align=TextEntityAlignment[align])


def _hline(msp, x0, x1, y, layer="A-ANNO-TEXT"):
    msp.add_line((x0, y), (x1, y), dxfattribs={"layer": layer})


def floor_rooms(floor):
    rows = [(en, alt_name, area(r)) for en, alt_name, r, _ in floor["rooms"]]
    en, alt_name, r, minus, _ = floor["open_space"]
    rows.append((en, alt_name, area(r) - sum(area(m) for m in minus)))
    return rows


def draw_cover(msp, sheet_list):
    _t(msp, "THREE-STOREY HOUSE", 40, 262, 9.0)
    _t(msp, "خانه سه‌طبقه", 330, 262, 9.5, rtl=True, align="MIDDLE_RIGHT")
    _t(msp, "Concept design drawings", 40, 249, 4.0)
    _t(msp, "نقشه‌های طرح اولیه", 330, 249, 4.4, rtl=True, align="MIDDLE_RIGHT")
    _hline(msp, 40, 330, 242)
    facts = [("Location", "Hillside lot (concept study)"),
             ("Land", "about 308 m², slopes 3 m down from the road (west) to the east"),
             ("House", f"{geom.HOUSE[2] - geom.HOUSE[0]:.2f} × {geom.HOUSE[3] - geom.HOUSE[1]:.2f} m; "
                       "3 floors: basement -3.00, ground ±0.00, first floor +3.00"),
             ("Built area", " + ".join(f"{areas.built_area(k):.2f}" for k in "BGT")
              + f" = {sum(areas.built_area(k) for k in 'BGT'):.2f} m², plus a "
              + f"{areas.terrace_area():.2f} m² covered terrace"),
             ("Levels", "±0.00 = road and front yard; ridge +7.40"),
             ("Revision", "B: redesign after the owner's first review")]
    for i, (k, v) in enumerate(facts):
        _t(msp, k, 40, 234 - i * 6, 2.4)
        _t(msp, v, 72, 234 - i * 6, 2.4)

    # drawing list
    _t(msp, "DRAWING LIST", 40, 198, 3.2)
    _hline(msp, 40, 175, 194)
    for i, (num, en, alt_title) in enumerate(sheet_list):
        y = 188 - i * 7
        _t(msp, num, 40, y, 2.5)
        _t(msp, en, 58, y, 2.5)
        _t(msp, alt_title, 175, y, 2.7, rtl=True, align="MIDDLE_RIGHT")
        _hline(msp, 40, 175, y - 3.5, layer="A-ANNO-NPLT")

    # area table
    _t(msp, "AREA TABLE (m²; rooms inside walls, rows add up to the built area)", 190, 198, 3.0)
    _hline(msp, 190, 330, 194)
    y = 189
    for tag, name, name_alt, limit in (("B", "Basement", "زیرزمین", "max 70"),
                                      ("G", "Ground floor", "همکف", "max 80"),
                                      ("T", "First floor", "طبقه اول", "max 80 with terrace")):
        rows = areas.breakdown(tag)
        _t(msp, f"{name}: built {areas.built_area(tag):.2f} m² ({limit})", 190, y, 2.4)
        _t(msp, name_alt, 330, y, 2.6, rtl=True, align="MIDDLE_RIGHT")
        y -= 4.0
        for en, alt_name, a in rows:
            _t(msp, en, 194, y, 1.9)
            _t(msp, f"{a:.2f}", 282, y, 1.9, align="MIDDLE_RIGHT")
            _t(msp, alt_name, 330, y, 2.0, rtl=True, align="MIDDLE_RIGHT")
            y -= 3.6
        y -= 1.4
    terrace = sum((r[2] - r[0] - 0.3) * (r[3] - r[1] - 0.3) for r in geom.TERRACE)
    _t(msp, f"Covered terrace: {areas.terrace_area():.2f} m² outside size (first floor + terrace "
            f"= {areas.built_area('T') + areas.terrace_area():.2f}, max 80)", 190, y, 2.2)
    _t(msp, f"{terrace:.2f}", 282, y - 3.6, 1.9, align="MIDDLE_RIGHT")
    _t(msp, "usable inside the railing", 194, y - 3.6, 1.9)
    _t(msp, "تراس مسقف", 330, y - 3.6, 2.0, rtl=True, align="MIDDLE_RIGHT")
