"""The A3 drawing set: one DXF, PDF and PNG per sheet, a combined PDF and a true-size DXF model."""
from pathlib import Path

import ezdxf
import fitz
from ezdxf import recover
from ezdxf.addons.drawing import Frontend, RenderContext, config, layout, pymupdf

from . import cad, floors, geom, plans, sheets, site

PAGE_MM = (420, 297)            # A3 landscape
PNG_DPI = 150


def audit_dxf(path):
    """Re-read a written DXF in recovery mode and audit it. Returns what the auditor reported:
    errors it could not fix and problems it had to fix. A clean file returns an empty list."""
    doc, auditor = recover.readfile(path)
    second = doc.audit()
    return [f"{Path(path).name}: {entry.message}"
            for entry in auditor.errors + auditor.fixes + second.errors + second.fixes]


def render_sheet(doc, stem, out):
    """Write one sheet as DXF, and render it to PDF and PNG with the ezdxf drawing add-on."""
    backend = pymupdf.PyMuPdfBackend()
    cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE,
                               lineweight_policy=config.LineweightPolicy.ABSOLUTE)
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(doc.modelspace())
    page = layout.Page(*PAGE_MM, layout.Units.mm, margins=layout.Margins.all(0))
    (out / "pdf" / f"{stem}.pdf").write_bytes(backend.get_pdf_bytes(page))
    (out / "png" / f"{stem}.png").write_bytes(backend.get_pixmap_bytes(page, fmt="png", dpi=PNG_DPI))
    doc.saveas(out / "dxf" / f"{stem}.dxf")


def build_model_dxf(path):
    """True-size DXF in metres for the engineer's CAD: the site plan and the three floor plans."""
    doc = ezdxf.new("R2018", setup=True, units=6)
    for name, color, lineweight in cad.LAYERS:
        doc.layers.add(name, color=color, lineweight=lineweight)
    doc.styles.add("EN", font="arial.ttf")
    doc.styles.add("ALT", font="tahoma.ttf")
    cad.setup_dimstyle(doc)
    doc.header["$LTSCALE"] = 0.05
    msp = doc.modelspace()
    site.draw_site(cad.Pen(msp, scale=1000, text_scale=0.1))
    for dx, floor, outline, stair_label, title in (
            (0.0, floors.BASEMENT, geom.BASEMENT, "UP", "BASEMENT -3.00"),
            (22.0, floors.GROUND, geom.HOUSE, "UP / DN", "GROUND FLOOR ±0.00"),
            (44.0, floors.TOP, geom.TOP, "DN", "FIRST FLOOR +3.00")):
        pen = cad.Pen(msp, origin=(dx, 18.0), scale=1000, text_scale=0.05)
        plans.draw_plan(pen, floor, outline, stair_label, geom.HOUSE if floor is floors.TOP else None)
        if floor is floors.TOP:
            plans.draw_terrace(pen)
        pen.text(title, (12.0, 3.0), h=8.0)
    doc.saveas(path)


def build(out_dir="output", only=None, log=print):
    """Generate the drawing set into <out_dir>/drawings. `only` limits it to some sheet numbers.
    Every DXF written is audited; returns the list of audit problems (empty when all are clean)."""
    out = Path(out_dir) / "drawings"
    for sub in ("pdf", "png", "dxf"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    built, problems = [], []
    for number, slug, draw in sheets.SHEETS:
        if only and number not in only:
            continue
        doc = cad.new_doc()
        cad.setup_dimstyle(doc)
        draw(doc.modelspace())
        stem = f"{number}_{slug}"
        render_sheet(doc, stem, out)
        problems += audit_dxf(out / "dxf" / f"{stem}.dxf")
        built.append(stem)
        log(f"  sheet {stem}")
    if not only:
        book = fitz.open()
        for stem in built:
            with fitz.open(out / "pdf" / f"{stem}.pdf") as part:
                book.insert_pdf(part)
        book.save(out / "concept-drawings.pdf")
        build_model_dxf(out / "model_1to1_metres.dxf")
        problems += audit_dxf(out / "model_1to1_metres.dxf")
        log(f"drawing set: {len(built)} sheets, combined PDF and true-size DXF in {out}")
    for problem in problems:
        log(f"  DXF audit: {problem}")
    log(f"DXF audit: {len(problems)} problems" if problems else "DXF audit: every file is clean")
    return problems
