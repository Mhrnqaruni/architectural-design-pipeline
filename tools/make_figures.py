"""Compose the README figures from the generated outputs.

    python -m archdesign all          # first, generate the outputs
    python tools/make_figures.py      # then write docs/figures/
"""
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
FIG = ROOT / "docs" / "figures"
RENDERS = OUT / "model" / "renders"
SHEETS = OUT / "drawings" / "png"
INK, MUTED, BG = (31, 35, 40), (101, 109, 118), (255, 255, 255)


def font(size, bold=False):
    names = ("segoeuib.ttf", "DejaVuSans-Bold.ttf") if bold else ("segoeui.ttf", "DejaVuSans.ttf")
    for name in names:
        for folder in (Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu")):
            if (folder / name).exists():
                return ImageFont.truetype(str(folder / name), size)
    return ImageFont.load_default()


def trim(img, bg, margin=20):
    """Crop to the drawn content: everything that differs from the background colour."""
    diff = ImageChops.difference(img.convert("RGB"), Image.new("RGB", img.size, bg)).convert("L")
    x0, y0, x1, y1 = diff.point(lambda v: 255 if v > 10 else 0).getbbox()
    return img.crop((max(0, x0 - margin), max(0, y0 - margin), min(img.width, x1 + margin),
                     min(img.height, y1 + margin)))


def fit_h(img, h):
    return img.resize((round(img.width * h / img.height), h), Image.LANCZOS)


def fit_w(img, w):
    return img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)


def row(panels, labels, h, gap=48, pad=32, caption=46, bg=BG):
    """Panels side by side at one height, each with a small label underneath."""
    panels = [fit_h(p, h) for p in panels]
    w = pad * 2 + sum(p.width for p in panels) + gap * (len(panels) - 1)
    canvas = Image.new("RGB", (w, pad + h + (caption if labels else 0) + pad // 2), bg)
    d, f = ImageDraw.Draw(canvas), font(24)
    x = pad
    for p, label in zip(panels, labels or [None] * len(panels)):
        canvas.paste(p, (x, pad))
        if label:
            d.text((x, pad + h + 12), label, fill=MUTED, font=f)
        x += p.width + gap
    return canvas


def save(img, name, **kw):
    FIG.mkdir(parents=True, exist_ok=True)
    path = FIG / name
    img.save(path, **kw)
    print(f"{path.relative_to(ROOT)}: {img.width} x {img.height}, {path.stat().st_size // 1024} KB")


def main():
    floor_bg = (242, 242, 240)
    plan = trim(Image.open(SHEETS / "A-102_ground-floor-plan.png").convert("RGB").crop((130, 140, 2020, 1480)), BG)
    ground = trim(Image.open(RENDERS / "5_ground-floor.png").convert("RGB"), floor_bg)
    save(row([plan, ground], ["Floor plan, 1:50  (DXF / PDF)", "3D model of the same floor  (three.js)"], 760),
         "plan-to-model.png", optimize=True)

    floors = [trim(Image.open(RENDERS / n).convert("RGB"), floor_bg)
              for n in ("7_basement.png", "5_ground-floor.png", "3_first-floor.png")]
    save(row(floors, ["Basement", "Ground floor", "First floor"], 560), "floors.png", optimize=True)

    exterior = [Image.open(RENDERS / n).convert("RGB").crop((160, 60, 1760, 1140))
                for n in ("1_house-from-garden.png", "2_house-from-road.png")]
    save(row(exterior, None, 640), "exterior.jpg", quality=88, optimize=True)

    names = [("A-100_site-plan", "A-100  Site plan"), ("A-101_basement-plan", "A-101  Basement plan"),
             ("A-102_ground-floor-plan", "A-102  Ground floor plan"),
             ("A-103_first-floor-plan", "A-103  First floor plan"),
             ("A-201_elevations-east-west", "A-201  Elevations"), ("A-301_sections", "A-301  Sections")]
    thumbs = [fit_w(Image.open(SHEETS / f"{n}.png").convert("RGB"), 700) for n, _ in names]
    tw, th, gap, pad, cap = thumbs[0].width, thumbs[0].height, 36, 32, 44
    sheet = Image.new("RGB", (pad * 2 + tw * 3 + gap * 2, pad * 2 + (th + cap) * 2 + gap), BG)
    d, f = ImageDraw.Draw(sheet), font(24)
    for i, (img, (_, label)) in enumerate(zip(thumbs, names)):
        x, y = pad + (i % 3) * (tw + gap), pad + (i // 3) * (th + cap + gap)
        sheet.paste(img, (x, y))
        d.rectangle([x, y, x + tw - 1, y + th - 1], outline=(208, 215, 222), width=2)
        d.text((x, y + th + 10), label, fill=MUTED, font=f)
    save(sheet, "drawing-set.png", optimize=True)


if __name__ == "__main__":
    main()
