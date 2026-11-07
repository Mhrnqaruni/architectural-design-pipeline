"""A small allow-list server for the generated outputs, for local viewing or behind a tunnel.

    /                          the 3D model         (<out>/model/index.html)
    /renders/<name>.png        the 3D renders       (<out>/model/renders)
    /concept-drawings.pdf      the drawing set      (<out>/drawings)
    /png/<sheet>.png           the sheets as images (<out>/drawings/png)

Nothing else in the folder is reachable.
"""
import http.server
from functools import partial
from pathlib import Path

TYPES = {".html": "text/html; charset=utf-8", ".png": "image/png", ".pdf": "application/pdf"}


def resolve(out, path):
    """Map a request path to an allowed file, or None."""
    parts = [p for p in path.split("?")[0].split("#")[0].split("/") if p]
    if not parts or parts == ["index.html"]:
        return out / "model" / "index.html"
    if parts == ["concept-drawings.pdf"]:
        return out / "drawings" / "concept-drawings.pdf"
    if len(parts) == 2 and parts[1].endswith(".png") and ".." not in parts[1] and "\\" not in parts[1]:
        folder = {"renders": out / "model" / "renders", "png": out / "drawings" / "png"}.get(parts[0])
        return folder / parts[1] if folder else None
    return None


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, out, **kwargs):
        self.out = out
        super().__init__(*args, **kwargs)

    def do_GET(self, head=False):
        f = resolve(self.out, self.path)
        if f is None or not f.is_file():
            self.send_error(404)
            return
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", TYPES.get(f.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def do_HEAD(self):
        self.do_GET(head=True)


def serve(out_dir="output", port=8765):
    out = Path(out_dir).resolve()
    print(f"serving {out} on http://127.0.0.1:{port}  (Ctrl+C to stop)", flush=True)
    http.server.ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, out=out)).serve_forever()
