"""Sheet list: each entry draws one A3 sheet into a DXF modelspace (paper millimetres)."""
from . import cover, elev, floors, geom, plans, section, sheet, site
from .cad import Pen

PLAN_SCALE = 50
HOUSE_CENTRE = ((geom.HOUSE[0] + geom.HOUSE[2]) / 2, (geom.HOUSE[1] + geom.HOUSE[3]) / 2)


def plan_sheet(msp, number, floor, outline, title_en, title_alt, level, stair_label,
               dims_outline=None):
    sheet.frame(msp, number, title_en, title_alt, f"1:{PLAN_SCALE} (A3)")
    pen = Pen(msp, origin=(185.0, 160.0), scale=PLAN_SCALE, world_origin=HOUSE_CENTRE)
    plans.draw_plan(pen, floor, outline, stair_label, dims_outline)
    plans.draw_level(pen, floor["level_at"], f"FFL {level}")
    sheet.view_title(msp, 40, 42, title_en, title_alt, f"Scale 1:{PLAN_SCALE}")
    sheet.scale_bar(msp, 40, 24, PLAN_SCALE)
    sheet.north_arrow(msp, 318, 258)
    return pen


def site_plan(msp):
    sheet.frame(msp, "A-100", "Site plan", "نقشه محوطه", "1:100 (A3)")
    pen = Pen(msp, origin=(182.0, 158.0), scale=100, world_origin=(12.32, 7.12))
    site.draw_site(pen)
    sheet.view_title(msp, 40, 42, "Site plan", "نقشه محوطه", "Scale 1:100")
    sheet.scale_bar(msp, 40, 24, 100, metres=10)
    sheet.north_arrow(msp, 318, 258)


def basement_plan(msp):
    pen = plan_sheet(msp, "A-101", floors.BASEMENT, geom.BASEMENT, "Basement plan",
                     "پلان زیرزمین", "-3.00", "UP")
    pen.text("Retaining walls and waterproofing on the buried sides (by engineer)",
             (12.4, geom.HOUSE[1] - 2.0), h=1.6)


def ground_plan(msp):
    plan_sheet(msp, "A-102", floors.GROUND, geom.HOUSE, "Ground floor plan", "پلان طبقه همکف",
               "±0.00", "UP / DN")


def top_plan(msp):
    pen = plan_sheet(msp, "A-103", floors.TOP, geom.TOP, "First floor plan", "پلان طبقه اول",
                     "+3.00", "DN", dims_outline=geom.HOUSE)
    plans.draw_terrace(pen)
    plans.draw_roof_edge(pen)


def elevation_sheet(msp, number, title_en, title_alt, views):
    """views: two (face, title_en, title_alt, u at view centre) stacked top and bottom."""
    sheet.frame(msp, number, title_en, title_alt, "1:100 (A3)")
    for (face, ten, tfa, uc), (py, ty) in zip(views, ((212.0, 151.0), (82.0, 22.0))):
        pen = Pen(msp, origin=(170.0, py), scale=100, world_origin=(uc, 2.0))
        elev.draw_elevation(pen, face)
        sheet.view_title(msp, 40, ty, ten, tfa, "Scale 1:100")


def elevations_ew(msp):
    elevation_sheet(msp, "A-201", "Elevations: east and west", "نماهای شرقی و غربی",
                    [("east", "East elevation (view)", "نمای شرقی (منظره)", 8.6),
                     ("west", "West elevation (road)", "نمای غربی (ورودی)", 12.2)])


def elevations_ns(msp):
    elevation_sheet(msp, "A-202", "Elevations: north and south", "نماهای شمالی و جنوبی",
                    [("north", "North elevation", "نمای شمالی", 18.6),
                     ("south", "South elevation", "نمای جنوبی", 11.0)])


def sections(msp):
    sheet.frame(msp, "A-301", "Sections A-A and B-B", "برش‌های الف و ب", "1:100 (A3)")
    pen = Pen(msp, origin=(165.0, 218.0), scale=100, world_origin=(11.8, 2.0))
    section.levels(pen, section.section_aa(pen))
    sheet.view_title(msp, 40, 150, "Section A-A", "برش الف - الف",
                     "West to east, looking north. Scale 1:100")
    pen = Pen(msp, origin=(165.0, 90.0), scale=100, world_origin=(7.6, 2.0))
    section.levels(pen, section.section_bb(pen))
    sheet.view_title(msp, 40, 22, "Section B-B", "برش ب - ب",
                     "South to north, looking west. Scale 1:100")


SHEET_LIST = [
    ("A-000", "Cover, drawing list, areas", "جلد، فهرست و جدول متراژ"),
    ("A-100", "Site plan 1:100", "نقشه محوطه"),
    ("A-101", "Basement plan 1:50", "پلان زیرزمین"),
    ("A-102", "Ground floor plan 1:50", "پلان طبقه همکف"),
    ("A-103", "First floor plan 1:50", "پلان طبقه اول"),
    ("A-201", "Elevations east, west 1:100", "نماهای شرقی و غربی"),
    ("A-202", "Elevations north, south 1:100", "نماهای شمالی و جنوبی"),
    ("A-301", "Sections A-A, B-B 1:100", "برش‌ها"),
]


def cover_sheet(msp):
    sheet.frame(msp, "A-000", "Cover and areas", "جلد و جدول متراژ", "-")
    cover.draw_cover(msp, SHEET_LIST)


SHEETS = [
    ("A-000", "cover", cover_sheet),
    ("A-100", "site-plan", site_plan),
    ("A-101", "basement-plan", basement_plan),
    ("A-102", "ground-floor-plan", ground_plan),
    ("A-103", "first-floor-plan", top_plan),
    ("A-201", "elevations-east-west", elevations_ew),
    ("A-202", "elevations-north-south", elevations_ns),
    ("A-301", "sections", sections),
]
