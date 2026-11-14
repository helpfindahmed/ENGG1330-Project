from map_data import raw_map

shop_positions = {
    (x, y)
    for y, row in enumerate(raw_map)
    for x, tile in enumerate(row)
    if tile == "$"
}

s = {"grid": [list(row) for row in raw_map],
     "px": -1,
     "py": -1,
     "flash": 100,
     "battery_buys": 0,
     "bangs": 3,
     "traps": 3,
     "coins": 0,
     "beam_range": 4,
     "aliens": [[50, 2], [40, 8]],
     "tl": [],
     "flashlight_disabled": False,
     "help_unlocked" : False,
     "turn" : 0}

alien_names = ["GHOST", "HUNTER"]
alien_stunned = [0, 0]

def open_tile(x, y):
    return (0 <= y < len(s["grid"]) and 0 <= x < len(s["grid"][y])
            and s["grid"][y][x] not in ("#", "?", "$", " "))

def neighbors(x, y):
    steps = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(a, b) for a, b in steps if open_tile(a, b)]

def shortest_distance(start, finish):
    if start == finish: return 0
    queue = [(start, 0)]
    visited = {start}
    for place, steps in queue:
        for next_place in neighbors(*place):
            if next_place == finish: return steps + 1
            if next_place not in visited:
                visited.add(next_place)
                queue.append((next_place, steps + 1))
    return 999

def trap_at(x, y):
    for t in s["tl"]:
        if t["tx"] == x and t["ty"] == y and t["triggered"]:
            return t
    return None

def near_tile(symbol):
    positions = [
        (s["px"] + 1, s["py"]),
        (s["px"] - 1, s["py"]),
        (s["px"], s["py"] + 1),
        (s["px"], s["py"] - 1),
    ]
    for x, y in positions:
        if 0 <= y < len(s["grid"]) and 0 <= x < len(s["grid"][y]):
            if s["grid"][y][x] == symbol:
                return True
    return False
