# Contributing

Issues and pull requests are welcome. For a larger change, please open an issue first to agree on
the approach.

## Development setup

```bash
git clone https://github.com/Mhrnqaruni/architectural-design-pipeline.git
cd architectural-design-pipeline
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
archdesign all
```

## Guidelines

- **Change the model, not the outputs.** Design changes go into `geom.py` and `floors.py`. Generated
  files are not tracked; they are rebuilt by `archdesign` and attached to releases.
- **Every new defect class gets a check.** Add the rule to `checks.py` (or the relevant generator),
  and add a regression test in `tests/` that reproduces the defect.
- **Keep the viewer build-free.** `viewer3d.js` is plain JavaScript and three.js is vendored, so the
  3D model stays a single offline HTML file.
- **Pin dependencies.** Add new packages with an exact version in `pyproject.toml`, and list their
  licence in [docs/standards.md](docs/standards.md#software-and-licences).
- **Run the full pipeline before a pull request.** `pytest` and `archdesign all` must both pass.
  The verification gate stops the build on any rule violation or DXF audit problem.

## Reporting a problem

Please include the command you ran, the full output, your operating system and your Python version.
For a drawing or model problem, name the sheet number or the 3D view.
