"""The furnished 3D model: one offline HTML page (three.js r147 inlined) and headless renders.

Loose furniture that is not on the plans (rugs, plants, stools) is checked against every door
swing before the page is written.
"""
import json
import math
import shutil
import subprocess
from pathlib import Path

from . import export3d, floors
from .checks import in_quarter, swings

HERE = Path(__file__).parent
VENDOR = HERE / "vendor" / "three-r147"
VIEWS = [("house", "1_house-from-garden"), ("house-west", "2_house-from-road"),
         ("first", "3_first-floor"), ("first-nw", "4_first-floor-from-north-west"),
         ("ground", "5_ground-floor"), ("ground-nw", "6_ground-floor-from-north-west"),
         ("basement", "7_basement"), ("basement-nw", "8_basement-from-north-west")]


def _js(path):
    return path.read_text(encoding="utf-8").replace("</script", "<\\/script")


def furniture_footprints(item):
    """Plan rectangles a loose 3D item occupies."""
    kind = item["k"]
    if kind == "stools":
        x0, y0, x1, y1 = item["r"]
        step = (x1 - x0) / item["n"]
        out = []
        for i in range(item["n"]):
            x = x0 + (i + 0.5) * step
            if "S" in item["sides"]:
                out.append((x - 0.18, y0 - 0.28, x + 0.18, y0 + 0.08))
            if "N" in item["sides"]:
                out.append((x - 0.18, y1 - 0.08, x + 0.18, y1 + 0.28))
        return out
    if "r" in item:
        return [tuple(item["r"])]
    x, y = item["p"]
    half = {"chair": 0.23, "barstool": 0.18}.get(kind, item.get("s", 0.2) * (1.8 if kind == "plant" else 1.0))
    return [(x - half, y - half, x + half, y + half)]


def check_furniture(log=print):
    """Every loose item must stay out of every door swing; rugs lie flat and may pass under."""
    problems = 0
    for tag, floor in (("B", floors.BASEMENT), ("G", floors.GROUND), ("T", floors.TOP)):
        discs = [(op, q) for op in floor["openings"] for q in swings(op)]
        for item in export3d.DECOR[tag]:
            if item["k"] == "rug":
                continue
            for fp in furniture_footprints(item):
                for op, q in discs:
                    (cx, cy), r = q[0], q[1]
                    pts = [(cx + r * i / 16 * math.cos(math.radians(t)), cy + r * i / 16 * math.sin(math.radians(t)))
                           for i in range(1, 17) for t in range(0, 360, 4)]
                    if any(in_quarter(p, q) and fp[0] < p[0] < fp[2] and fp[1] < p[1] < fp[3] for p in pts):
                        log(f"  {tag}: {item['k']} {fp} is inside the swing of {op[:5]}")
                        problems += 1
    log("3D furniture clear of door swings" if not problems else f"3D furniture: {problems} problems")
    return problems


def build(out_dir="output", log=print):
    """Write <out_dir>/model/index.html: three.js, the controls, the scene data and the app in one file."""
    if check_furniture(log):
        raise SystemExit("Move the furniture listed above out of the door swings.")
    scene = export3d.build()
    data = json.dumps(scene, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "viewer3d.html").read_text(encoding="utf-8")
    for key, text in (("/*THREE*/", _js(VENDOR / "three.min.js")),
                      ("/*ORBIT*/", _js(VENDOR / "OrbitControls.js")),
                      ("/*CSS2D*/", _js(VENDOR / "CSS2DRenderer.js")),
                      ("/*SCENE*/", data),
                      ("/*APP*/", _js(HERE / "viewer3d.js"))):
        page = page.replace(key, text, 1)
    out = Path(out_dir) / "model" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    log(f"3D model: {out} ({out.stat().st_size / 1024:.0f} KB, {len(scene['boxes'])} parts, "
        f"{len(scene['items'])} furniture items)")
    return out


def find_browser():
    """A Chromium-based browser for headless renders: Edge or Chrome on Windows and macOS,
    Chrome or Chromium on Linux."""
    candidates = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("Renders need Edge, Chrome or Chromium; none was found.")


def render_stills(page, out_dir="output", size=(1920, 1200), log=print):
    """One picture per view with a headless browser (SwiftShader WebGL, so no GPU is needed)."""
    out = (Path(out_dir) / "model" / "renders").resolve()     # the browser needs absolute paths
    out.mkdir(parents=True, exist_ok=True)
    browser, url = find_browser(), Path(page).resolve().as_uri()
    for view, name in VIEWS:
        target = out / f"{name}.png"
        cmd = [browser, "--headless=new", "--hide-scrollbars", "--enable-unsafe-swiftshader",
               "--use-angle=swiftshader", f"--window-size={size[0]},{size[1]}",
               "--virtual-time-budget=20000", f"--screenshot={target}", f"{url}#{view}-still"]
        subprocess.run(cmd, check=False, capture_output=True, timeout=240)
        log(f"  render {name}" if target.exists() else f"  FAILED {name}")
    return out
