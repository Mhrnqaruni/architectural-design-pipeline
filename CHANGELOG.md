# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-08

### Added

- Parametric design model (`geom.py`, `floors.py`): site, levels, envelope, walls, typed openings,
  rooms, fixtures and furniture as plain Python data.
- Drawing set: eight A3 sheets written as DXF R2018 on AIA / US National CAD Standard layers and
  rendered to PDF and PNG, plus a combined PDF and a true-size model in metres.
- Furnished 3D model: a three.js viewer inlined into one offline HTML page, with cutaway floors,
  parametric furniture, procedural materials and headless renders.
- Verification gate: circulation reachability, door-swing clearance, area limits, area-schedule
  closure, 3D furniture clearance, and an audit of every DXF written.
- `archdesign` command-line interface with `check`, `drawings`, `model`, `all` and `serve`.
- Test suite, CI on Python 3.11 and 3.12, and deployment of the 3D model to GitHub Pages.

[1.0.0]: https://github.com/Mhrnqaruni/architectural-design-pipeline/releases/tag/v1.0.0
