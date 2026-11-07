# Standards and conventions

The pipeline produces concept-stage design: RIBA Stage 2, or AIA Schematic Design. Structure,
services and full code compliance belong to a licensed engineer at the next stage. This page lists
the conventions the generators follow and the rules the design model encodes.

## Design stage

- **RIBA Plan of Work 2020, Stage 2 (Concept Design):** site strategy, spaces and sizes, levels,
  façades, an area schedule and open issues.
  [RIBA Plan of Work](https://www.architecture.com/knowledge-and-resources/resources-landing-page/riba-plan-of-work)
- **AIA Schematic Design:** the equivalent US phase, used as a cross-check on the drawing set.

## Regulations

The layout follows the national building regulations of the site's jurisdiction, which cover:

- **general requirements:** room sizes, daylight and ventilation, stairs and boundary distances,
- **seismic design:** a regular rectangular plan on one structural grid, with wet rooms, bedrooms,
  stairs and lift stacked floor over floor,
- **gas installations:** a plant room with its own external door and natural ventilation.

## Drafting and CAD

| Convention | Applied as |
|---|---|
| Layer names | AIA CAD Layer Guidelines / US National CAD Standard: `A-WALL`, `A-DOOR`, `A-GLAZ`, `A-FURN`, `A-FLOR-STRS`, `A-AREA-IDEN`, `A-ANNO-TEXT`, `A-SITE`, `A-ROOF`, `A-ELEV`, `A-SECT` and others ([nationalcadstandard.org](https://www.nationalcadstandard.org)) |
| Sheet numbering | A-000 cover and area schedule, A-100 site, A-101 to A-103 plans, A-201 and A-202 elevations, A-301 sections |
| Scales and paper | plans 1:50; site plan, elevations and sections 1:100; A3 landscape |
| Units and levels | metres; levels relative to a site datum (±0.00); finished-floor-level markers on every plan |
| File formats | DXF R2018 for each sheet; a true-size model in metres; PDF and PNG renders |
| Annotation | room names in two languages, with areas; right-to-left labels pre-shaped for CAD |
| Validation | every DXF written is re-read in recovery mode and audited with ezdxf; the build fails on any error or repair |
| Symbols | filled wall sections; door swings as arcs; sliding and pivot doors; windows with sill and head heights; WC, squat toilet, basin, shower, refrigerator |

## Dimensions and clearances

| Item | Rule | Basis |
|---|---|---|
| Doors | 0.8 m openings for rooms, 0.7 m for WCs | common minimum widths |
| Door swings | clear of furniture, fixtures, walls and other swings | enforced by the build gate |
| Corridors | at least 0.9 m clear | common residential minimum |
| Kitchen work aisle | at least 1.0 m between counter and island | common guidance is 1.0 to 1.2 m; asserted in the tests |
| Stairs | 2 × rise + going between 60 and 64 cm | Blondel's comfort rule; the design uses a 17 cm rise and a 28 cm going (62 cm) |
| Equipment rooms | room to use the equipment, for example one cue length around a billiards table | manufacturer and sports-body guidance |
| Daylight | glazing of about one-eighth of the floor area or more in habitable rooms | common rule of thumb |

## Area accounting

- **Built area:** the outside dimensions of the envelope, less undug ground in the basement and less
  open terraces on upper floors.
- **Limits:** each floor's built area must stay within the limit set by the brief. The tests assert
  this for every floor.
- **Area schedule:** room areas, plus stairs and lift, plus residual circulation, plus walls, equals
  the built area, to 0.01 m². This is measured on a 1 cm grid so nothing is counted twice.

## Software and licences

| Package | Version | Licence | Role |
|---|---|---|---|
| [ezdxf](https://github.com/mozman/ezdxf) | 1.4.5 | MIT | DXF authoring and rendering |
| [PyMuPDF](https://github.com/pymupdf/PyMuPDF) | 1.28.0 | AGPL-3.0 or commercial | PDF and PNG back end |
| [arabic-reshaper](https://github.com/mpcabd/python-arabic-reshaper) | 3.1.0 | MIT | joined right-to-left glyphs |
| [python-bidi](https://github.com/MeirKriheli/python-bidi) | 0.6.12 | LGPL-3.0 | bidirectional text order |
| [NumPy](https://numpy.org) | 2.4.6 | BSD-3-Clause | raster area accounting |
| [three.js](https://threejs.org) | r147, vendored | MIT | WebGL rendering |
| [pytest](https://pytest.org) | 9.1.1 | MIT | tests (development) |
| [Pillow](https://python-pillow.org) | 12.2.0 | MIT-CMU | figure composition (development) |
