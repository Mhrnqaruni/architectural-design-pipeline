"""Command-line interface.

    archdesign check                  run the design-rule checks
    archdesign drawings [A-102 ...]   generate the drawing set (DXF, PDF, PNG)
    archdesign model [--renders]      generate the 3D model page, optionally with renders
    archdesign all                    checks, drawing set, 3D model and renders
    archdesign serve [--port 8765]    serve the outputs locally

Without installing: python -m archdesign <command>.
"""
import argparse
import sys

from . import __version__


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out", default="output", help="output folder (default: %(default)s)")
    parser = argparse.ArgumentParser(prog="archdesign",
                                     description="Concept-stage architectural design as code.")
    parser.add_argument("--version", action="version", version=f"archdesign {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", parents=[common], help="run the design-rule checks")
    drawings = sub.add_parser("drawings", parents=[common], help="generate the drawing set")
    drawings.add_argument("sheets", nargs="*", help="sheet numbers such as A-102 (default: all)")
    model = sub.add_parser("model", parents=[common], help="generate the furnished 3D model page")
    model.add_argument("--renders", action="store_true", help="also render 1920 x 1200 pictures of every view")
    sub.add_parser("all", parents=[common], help="checks, drawing set, 3D model and renders")
    server = sub.add_parser("serve", parents=[common], help="serve the outputs on http://127.0.0.1:PORT")
    server.add_argument("--port", type=int, default=8765)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "serve":
        from .server import serve
        serve(args.out, args.port)
        return 0

    from . import checks
    if checks.run_all():
        print("Fix the plan problems above before generating anything.", file=sys.stderr)
        return 1
    if args.command in ("drawings", "all"):
        from . import drawing_set
        if drawing_set.build(args.out, set(getattr(args, "sheets", None) or []) or None):
            print("The DXF audit reported problems (listed above).", file=sys.stderr)
            return 1
    if args.command in ("model", "all"):
        from . import web_model
        page = web_model.build(args.out)
        if args.command == "all" or args.renders:
            web_model.render_stills(page, args.out)
    return 0
