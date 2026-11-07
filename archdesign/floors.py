"""Room layouts. Partitions are 0.10 m rectangles; openings are rectangles that span the
wall they cut. Door: ("door", x0, y0, x1, y1, hinge_at_end, swing), swing +1 opens toward +y
(horizontal wall) or +x (vertical wall). Windows may carry (sill, head) heights.
Bands: south rooms y 5.53-9.43, north rooms y 9.53-12.07. West end holds stairs, lift and the
stacked wet rooms on every floor.
Fixtures: wc = (x, y, facing) with (x, y) on the wall behind the cistern; squat = squat-toilet
pan centre and long axis; bed = rect plus the side the headboard is on (default north).
Every door swing is kept clear of furniture, fixtures and other door swings.
"""
from .geom import STAIR

CORE_WALLS = [(6.5, 8.78, 6.6, 12.07), (6.6, 10.58, 7.9, 10.68), (7.9, 9.43, 8.0, 12.07)]
LIFT_DOOR = ("slide", 6.85, 10.58, 7.65, 10.68)
WET_WALLS = [(4.3, 7.3, 9.0, 7.4), (6.1, 5.53, 6.2, 7.3), (7.8, 5.53, 7.9, 7.3)]
# Ground floor: a 0.9 m corridor runs from the lobby to the living room along the north side of
# the master (nobody walks through bedroom 2). First floor: the way to the living room goes
# through the TV room, which is open to the lobby and the living room, so the master keeps its size.
SUITE_WALLS_G = [(7.9, 7.4, 8.0, 9.43), (9.0, 5.53, 9.1, 8.53), (9.1, 8.43, 11.95, 8.53),
                 (8.0, 9.43, 11.95, 9.53), (11.95, 5.53, 12.05, 8.53), (11.1, 9.53, 11.2, 12.07)]
SUITE_WALLS_T = [(7.9, 7.4, 8.0, 9.43), (9.0, 5.53, 9.1, 9.43), (8.0, 9.43, 11.95, 9.53),
                 (11.95, 5.53, 12.05, 9.53), (11.1, 9.53, 11.2, 12.07)]
SUITE_OPENINGS = [
    ("door", 5.35, 7.3, 6.05, 7.4, 1, -1),           # WC + shower, opens in against its side wall
    ("door", 7.8, 5.85, 7.9, 6.55, 0, -1),           # walk-in -> bathroom
    ("opening", 9.0, 5.8, 9.1, 6.9),                 # walk-in <-> bedroom
    ("opening", 7.9, 7.55, 8.0, 8.45),               # foyer -> lobby
    LIFT_DOOR,
    ("window", 4.7, 5.23, 5.6, 5.53, 1.5, 2.2), ("window", 6.5, 5.23, 7.4, 5.53, 1.5, 2.2),
    ("window", 9.4, 5.23, 11.6, 5.53, 0.5, 2.4),      # master bedroom, larger
    ("window", 8.75, 12.07, 10.75, 12.37, 1.6, 2.3),
    ("window", 4.0, 9.2, 4.3, 11.7, 0.3, 2.7),       # tall stair window on the road side
]
WET_ROOMS = [
    ("WC + shower", "سرویس و دوش", (4.3, 5.53, 6.1, 7.3), (4.78, 6.475)),
    ("Bathroom", "حمام", (6.2, 5.53, 7.8, 7.3), (6.9, 6.85)),
    ("Walk-in", "کلوزت", (7.9, 5.53, 9.0, 7.3), (8.45, 6.3)),
    ("Lobby", "لابی", (8.0, 7.4, 9.0, 9.43), (8.5, 8.0)),
]
WET_FIXTURES = {
    "shower": [(5.25, 5.58, 6.05, 6.38), (6.25, 5.58, 7.05, 6.38)],
    "wc": [(4.75, 5.53, "N"), (7.35, 7.3, "S")],
    "squat": [(4.7, 6.95, "E")],
    "basin": [(6.2, 6.75, 6.65, 7.25), (6.4, 7.4, 6.95, 7.85)],   # shower room; landing/foyer
}
MASTER_BED_G = (9.95, 6.18, 11.95, 7.78, "E")
MASTER_BED_T = (9.95, 6.85, 11.95, 8.45, "E")

GROUND = {
    "outline": "HOUSE",
    "walls": WET_WALLS + SUITE_WALLS_G + CORE_WALLS,
    "openings": SUITE_OPENINGS + [
        ("door", 9.15, 8.43, 9.95, 8.53, 0, -1),      # corridor -> master bedroom, opens to the wall
        ("door", 8.1, 9.43, 8.9, 9.53, 0, +1),        # lobby -> bedroom 2
        ("pivot", 4.0, 7.45, 4.3, 8.65, 0.2),         # tall pivot front door, 1.2 m
        ("slide", 12.3, 5.23, 14.6, 5.53),            # living -> south patio
        ("window", 12.0, 12.07, 14.4, 12.37, 1.2, 2.2),
        ("window", 14.9, 5.8, 15.2, 9.2, 0.1, 2.5), ("window", 14.9, 9.8, 15.2, 11.8, 1.0, 2.2),
    ],
    "rooms": WET_ROOMS + [
        ("Corridor", "راهرو", (9.0, 8.53, 11.95, 9.43), (10.55, 8.98)),
        ("Foyer", "ورودی", (4.3, 7.4, 7.9, 8.68), (6.2, 8.25)),
        ("Master bedroom", "اتاق‌خواب مستر", (9.1, 5.53, 11.95, 8.43), (10.45, 6.98)),
        ("Bedroom 2", "اتاق‌خواب ۲", (8.0, 9.53, 11.1, 12.07), (9.13, 10.9)),
    ],
    "open_space": ("Living + kitchen", "پذیرایی و آشپزخانه", (11.2, 5.53, 14.9, 12.07),
                   [(11.2, 5.53, 12.05, 9.53)], (13.35, 8.95)),
    "chain_x": [4.0, 7.9, 11.95, 15.2],
    "chain_y": [5.23, 9.48, 12.37],
    "level_at": (6.75, 9.8),
    "notes": [("TV area", "تی‌وی", (12.7, 8.4)), ("Kitchen", "آشپزخانه", (13.1, 11.75)),
              ("Island, 8 seats", "جزیره ۸ نفره", (13.5, 10.02))],
    "furniture": dict(WET_FIXTURES, **{
        "bed": [MASTER_BED_G, (9.6, 10.05, 11.0, 12.05)],
        "fridge": [(11.2, 11.48, 11.9, 12.07)],        # full-height fridge at the end of the run
        "counter": [(11.9, 11.48, 14.9, 12.07),        # kitchen
                    (8.05, 10.4, 8.65, 12.03),         # bedroom 2 wardrobe
                    (6.95, 7.45, 7.6, 7.8),            # shoe cabinet
                    (7.95, 6.75, 8.95, 7.3)],          # walk-in hanging
        "island": [(12.4, 9.6, 14.6, 10.45)],
        "sofa": [(13.95, 6.2, 14.75, 8.6)],            # faces west, to the TV
        "table": [(13.15, 6.9, 13.6, 7.9)],            # coffee table; 0.75 m walkway to the patio
        "tv": [(12.05, 6.75, 12.4, 8.05, "W")],        # TV unit on the inner wall
    }),
}

TOP = {
    "outline": "TOP",
    "ext_walls": [(4.0, 5.23, 15.2, 5.53), (14.9, 5.53, 15.2, 9.23), (12.9, 9.23, 15.2, 9.53),
                  (12.9, 9.53, 13.2, 12.37), (4.0, 12.07, 12.9, 12.37), (4.0, 5.53, 4.3, 12.07)],
    "walls": WET_WALLS + SUITE_WALLS_T + CORE_WALLS,
    "openings": SUITE_OPENINGS + [
        ("door", 9.0, 8.5, 9.1, 9.3, 1, +1),           # lobby -> master bedroom, opens to the wall
        ("opening", 8.1, 9.43, 8.9, 9.53),             # lobby -> TV room
        ("opening", 11.1, 9.6, 11.2, 10.5),            # TV room -> living room
        ("window", 4.0, 7.45, 4.3, 8.65),              # larger window to the road, above the door
        ("slide", 13.3, 9.23, 14.7, 9.53),             # living -> terrace
        ("slide", 12.9, 9.9, 13.2, 11.7),              # living (north part) -> terrace
        ("window", 12.8, 5.23, 14.6, 5.53, 1.0, 2.2),  # kitchen, to the south
        ("window", 14.9, 5.8, 15.2, 8.95, 0.1, 2.5),   # living, to the east view
    ],
    "rooms": WET_ROOMS + [
        ("Landing", "پاگرد", (4.3, 7.4, 7.9, 8.68), (5.45, 8.25)),
        ("Master bedroom", "اتاق‌خواب مستر", (9.1, 5.53, 11.95, 9.43), (10.55, 6.15)),
        ("TV room", "تی‌وی‌روم", (8.0, 9.53, 11.1, 12.07), (10.1, 10.8)),
    ],
    "open_space": ("Living + kitchen", "پذیرایی و آشپزخانه", (11.2, 5.53, 14.9, 12.07),
                   [(11.2, 5.53, 12.05, 9.53), (12.9, 9.23, 14.9, 12.07)], (13.5, 8.3)),
    "chain_x": [4.0, 7.9, 11.95, 15.2],
    "chain_y": [5.23, 9.48, 12.37],
    "level_at": (6.75, 9.8),
    "notes": [("Kitchen", "آشپزخانه", (13.45, 6.45)), ("Island, 4 seats", "جزیره ۴ نفره", (13.3, 7.5)),
              ("Laundry", "لباسشویی", (7.27, 7.7))],
    "furniture": dict(WET_FIXTURES, **{
        "bed": [MASTER_BED_T],
        "fridge": [(12.1, 5.58, 12.75, 6.18)],         # full-height fridge at the end of the run
        "counter": [(12.75, 5.58, 14.8, 6.18),         # kitchen
                    (6.95, 7.4, 7.6, 8.0),             # laundry closet (washer + dryer)
                    (4.35, 7.4, 5.25, 7.72),           # low shoe cabinet under the landing window
                    (7.95, 6.75, 8.95, 7.3)],          # walk-in hanging
        "island": [(12.6, 7.2, 14.0, 7.8)],
        "sofa": [(11.3, 10.65, 12.1, 12.0), (8.1, 10.45, 8.9, 12.0)],
    }),
}

BASEMENT = {
    "outline": "BASEMENT",
    "ext_walls": [(8.6, 5.23, 15.2, 5.53), (14.9, 5.53, 15.2, 12.07), (4.0, 12.07, 15.2, 12.37),
                  (4.0, 7.4, 4.3, 12.07), (4.0, 7.4, 8.9, 7.7), (8.6, 5.23, 8.9, 7.7)],
    "walls": CORE_WALLS + [(8.0, 9.43, 13.15, 9.53), (13.1, 9.53, 13.2, 12.07),
                           (13.15, 9.43, 14.9, 9.53), (13.2, 10.48, 14.9, 10.58),
                           (8.9, 8.43, 10.5, 8.53), (10.4, 5.53, 10.5, 8.43),
                           (8.8, 7.7, 8.9, 8.43)],
    "openings": [
        LIFT_DOOR,
        ("door", 9.7, 9.43, 10.45, 9.53, 1, +1),       # corridor -> spa
        ("door", 8.8, 7.75, 8.9, 8.38, 0, +1),         # hall -> storage
        ("slide", 13.45, 9.43, 14.15, 9.53),           # lounge -> WC, sliding door
        ("door", 14.9, 11.0, 15.2, 11.8, 0, +1),       # boiler room -> lower garden, opens out
        ("slide", 14.9, 5.85, 15.2, 9.15),             # lounge -> lower east garden
        ("window", 9.1, 5.23, 10.2, 5.53, 2.0, 2.6),   # storage, small high window
        ("window", 13.5, 12.07, 14.6, 12.37, 2.0, 2.6),  # boiler room, small high window
        ("window", 9.0, 12.07, 12.5, 12.37, 2.0, 2.6),   # spa, frosted high window
    ],
    "rooms": [
        ("Hall", "راهرو", (4.3, 7.7, 8.8, 8.78), (7.4, 8.25)),
        ("Spa", "سونا و جکوزی", (8.0, 9.53, 13.1, 12.07), (11.6, 9.95)),
        ("Boiler room", "موتورخانه", (13.2, 10.58, 14.9, 12.07), (14.05, 11.45)),
        ("Storage", "انباری", (8.9, 5.53, 10.4, 8.43), None),
        ("WC", "سرویس", (13.2, 9.53, 14.9, 10.48), (13.88, 10.05)),
    ],
    "open_space": ("Billiards lounge + bar", "بیلیارد و بار", (10.5, 5.53, 14.9, 9.43), [],
                   (12.7, 6.15)),
    "chain_x": [4.0, 8.75, 11.95, 15.2],
    "chain_y": [5.23, 7.55, 9.48, 12.37],
    "level_at": (5.6, 8.25),
    "notes": [("Billiards, 7 ft", "بیلیارد ۷ فوت", (12.7, 7.28)), ("Bar", "بار", (11.6, 9.13)),
              ("Jacuzzi", "جکوزی", (9.2, 11.4)), ("Sauna", "سونا", (12.2, 11.3)),
              ("Plunge pool", "حوضچه آب سرد", (10.8, 11.4)), ("Shower", "دوش", (8.45, 9.98)),
              ("Shower", "دوش", (12.65, 9.98)), ("Corridor", "راهرو", (9.25, 8.98))],
    "furniture": {
        "table": [(11.58, 6.645, 13.82, 7.915)],                       # 7 ft billiards
        "counter": [(10.6, 8.95, 12.6, 9.38),                          # bar
                    (13.9, 5.55, 14.85, 5.85)],                        # low shoe bench by the garden door
        "tub": [(8.2, 10.4, 10.2, 12.0), (10.35, 10.8, 11.25, 12.0)],  # jacuzzi, plunge pool
        "island": [(11.4, 10.55, 13.0, 12.05)],                        # sauna cabin
        "shower": [(8.05, 9.58, 8.85, 10.38), (12.25, 9.58, 13.05, 10.38)],
        "wc": [(14.9, 10.0, "W")],
        "basin": [(13.2, 9.65, 13.55, 10.15)],
    },
    "undug": (4.0, 5.23, 8.6, 7.4),
}
