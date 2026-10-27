"""First-floor map proposal, using the team's draft2 tile conventions.

Positions use zero-based (x, y): x is the column and y is the row.
Ghosts are stored separately from terrain so moving a ghost preserves tiles.
"""

FLOOR_ONE_MAP = [
    "####################",
    "#@.................#",
    "#..?...............#",
    "#..................#",
    "######_#######_#####",
    "#..................#",
    "#....####..........#",
    "#..............$...#",
    "#..=..............>#",
    "#..................#",
    "####################",
]

# Each spawn is (ghost kind, x, y), matching draft2's SPAWNS entries.
FLOOR_ONE_SPAWNS = [
    ("R", 12, 2),
    ("H", 10, 7),
]

TILE_LEGEND = {
    "#": "wall",
    ".": "floor",
    "@": "player start",
    "_": "pressure plate",
    "?": "data terminal",
    "=": "puzzle console",
    "$": "supply station",
    ">": "exit",
}
