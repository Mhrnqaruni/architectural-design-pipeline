"""Geometry in metres. x runs east, y runs north. Levels are relative to the road (±0.00).

Rectangles are (x0, y0, x1, y1). Every drawing, the 3D model and the checks read these numbers.
"""

# --- Land (from the survey sketch) ----------------------------------------------------------
PLOT = [(0.0, 14.23), (24.64, 14.23), (19.76, 0.0), (1.11, 0.0)]  # NW, NE, SE, SW
PLOT_SIDES = {"N": 24.64, "E": 15.04, "S": 18.65, "W": 14.27}
LEVEL_WEST, LEVEL_EAST = 0.00, -3.00


def west_x(y):
    return 1.11 - 0.0780 * y


def east_x(y):
    return 19.76 + 0.3429 * y


def ground_level(x, y):
    """Natural ground level: straight slope from the west boundary (0.00) to the east (-3.00)."""
    t = min(max((x - west_x(y)) / (east_x(y) - west_x(y)), 0.0), 1.0)
    return LEVEL_WEST + t * (LEVEL_EAST - LEVEL_WEST)


# --- Levels -----------------------------------------------------------------------------------
LEVELS = {"basement": -3.00, "ground": 0.00, "top": 3.00, "eaves": 5.30, "ridge": 7.40}
SLAB = 0.30

# --- Envelope ---------------------------------------------------------------------------------
EXT_WALL = 0.30
HOUSE = (4.0, 5.23, 15.2, 12.37)        # outside faces of the house
ROAD_SETBACK = 3.5                      # target distance from the road boundary (it is angled)
NORTH_SETBACK_MIN = 1.5                 # keep at least this far from the north boundary
UNDUG = (4.0, 5.23, 7.0, 8.68)          # not excavated under the entrance (high corner)
BASEMENT = HOUSE                        # outline; the undug corner is cut out by its walls
TERRACE = [(12.9, 9.23, 15.2, 12.37)]   # first-floor terrace, north-east corner, under the roof
TOP = HOUSE                             # outline; the terrace corner is cut out by its walls
ROOF_OVERHANG = 0.5
GRID_X = [4.0, 7.9, 11.95, 15.2]        # structural lines, same on every floor
GRID_Y = [5.23, 9.48, 12.37]

# --- Shared core (same place on every floor) ---------------------------------------------------
STAIR = (4.3, 8.78, 6.5, 12.07)         # U-stair, flights run north, landing at the north end
STAIR_LANDING = 1.10
LIFT = (6.6, 10.68, 7.9, 12.07)         # 4-person home lift, shaft inside dimensions

# --- Outdoor ----------------------------------------------------------------------------------
CARPORT = (1.0, 0.1, 6.6, 5.13)         # 2 cars side by side, parked east-west
PATIO_SOUTH = (11.6, 0.8, 15.2, 5.23)   # ±0.00, raised on soil from the dig
LOWER_GARDEN = [(15.2, 1.0), (20.1, 1.0), (24.64, 14.23), (15.2, 14.23)]  # levelled at -3.00
PATIO_STEPS = (15.2, 1.0, 16.6, 2.6)    # steps from the south patio down to the lower garden
GATE_CAR = (0.4, 4.9)                   # y range on the west boundary
GATE_WALK = (7.45, 8.6)
SECTION_AA_Y = 7.0                      # west-east section line
SECTION_BB_X = 13.5                     # south-north section line
