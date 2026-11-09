import os

raw_map = [
    "#######################",
    "#@..........###.......#",
    "#.######..............#",
    "#.....$..#...######.###",
    "#.....................#",
    "#........###.....>....#",
    "#######################"
]

s = {"grid": [list(row) for row in raw_map],
     "px": -1,
     "py": -1,
     "flash": 0,
     "traps": 0,
     "coins": 70,
     "heat": 0,
     "beam_range": 4,
     "aliens": [[-1, -1], [-1, -1]],
     "tl": []
     }

s["flash"] = 100
s["traps"] = 3


alien_names = ["ALIEN", "HUNTER"]
alien_stunned = [0, 0]
alien_memory = [[-1, -1], [-1, -1]]
last_player = (1, 1)
hunter_target = None
turn = 0
message = ""


def show_status():
    print(f"Flashlight : [{'*' * (s['flash'] // 10):10}] {s['flash']}")
    print(f" CoinsLeft : [{'*' * (s['coins'] // 7):10}] {s['coins']}")
    print(f" HeatLevel : [{'*' * (s['heat'] // 10):10}] {s['heat']}")
    print(f" Trap_Left : [{'*' * s['traps']}] {s['traps']}")


def enter_shop():
    print("enter 1 for 20 Flashlight     - 40cc")
    print("enter 2 for a trap            - 20cc")
    print("enter 3 for lowering 20 heat  - 30cc")
    try:
        opt = int(input())
    except ValueError:
        print("Invalid input")
        return
    if (opt == 1) and s["coins"] >= 40:
        if s["flash"] <= 80:
            s["flash"] += 20
        else:
            s["flash"] = 100
        s["coins"] -= 40
    elif (opt == 2) and s["coins"] >= 20:
        s["traps"] += 1
        s["coins"] -= 20
    elif (opt == 3) and s["coins"] >= 30:
        if s["heat"] >= 20:
            s["heat"] -= 20
        else:
            s["heat"] = 0
        s["coins"] -= 30
    elif opt not in (1, 2, 3):
        print("invalid input")
    else:
        print("Not enough money")


def open_tile(x, y):
    return (0 <= y < len(s["grid"]) and
            0 <= x < len(s["grid"][y]) and
            s["grid"][y][x] != "#")


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(x, y):
    steps = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return [(a, b) for a, b in steps if open_tile(a, b)]


def shortest_distance(start, finish):
    """returns the number of steps to reach finish from start, or 999 if unreachable"""
    if start == finish:
        return 0
    queue = [(start, 0)]
    visited = {start}
    for place, steps in queue:
        for next_place in neighbors(*place):
            if next_place == finish:
                return steps + 1
            if next_place not in visited:
                visited.add(next_place)
                queue.append((next_place, steps + 1))
    return 999


def trap_at(x, y):
    for t in s["tl"]:
        if t["tx"] == x and t["ty"] == y and t["triggered"]:
            return t
    return None


def draw(msg=""):
    os.system('cls' if os.name == 'nt' else 'clear')
    display = [row[:] for row in s["grid"]]
    for i, (x, y) in enumerate(s["aliens"]):
        if (x, y) != (s["px"], s["py"]):
            symbol = "G" if i == 0 else "H"
            if alien_stunned[i] > 0:
                symbol = symbol.lower()  # stunned aliens == g.
            display[y][x] = symbol
    for row in display:
        print("".join(row))
    show_status()
    print("G = alien | H = hunter | g/h = trapped and stunned")
    print("WASD move | T trap | E shop | X exit")
    if msg:
        print(msg)


def route(start, goal, blocked=()):
    """keeps movement predictable hopefully"""
    queue = [start]
    previous = {start: None}
    for place in queue:
        if place == goal:
            break
        for tile in neighbors(*place):
            if tile not in previous and tile not in blocked:
                previous[tile] = place
                queue.append(tile)
    if goal not in previous:
        return []
    path = []
    place = goal
    while place is not None:
        path.append(place)
        place = previous[place]
    return path[::-1]


def hunter_goal(player):
    """returns the tile the Hunter should move toward to block the player"""
    global hunter_target
    hunter = tuple(s["aliens"][1])
    stalker = tuple(s["aliens"][0])
    exit_tile = (16, 5)

    # Replan every turn: use actual wall layout and the most recent player move.
    # Aliens can cross each other, so neither obstructs the escape route.
    escape_path = route(player, exit_tile)
    if not escape_path:
        return hunter

    # Evaluate tiles AHEAD of the player. A good barricade is one the
    # Hunter can reach before the player, preferably at a narrow junction.
    options = []
    for index, tile in enumerate(escape_path[1:], start=1):
        time_to_block = shortest_distance(hunter, tile)
        if time_to_block == 999:
            continue
        player_time = index
        # More valuable if Hunter can beat the player to the square.
        arrival_penalty = max(0, time_to_block - player_time + 1) * 12
        # Prefer nearer upcoming barricades, without chasing the player.
        future_penalty = abs(index - 4) * 2
        # Stay away from G so they're not walking together.
        partnership_penalty = max(0, 5 - shortest_distance(stalker, tile)) * 12
        # Narrow lanes are easier to block.
        corridor_bonus = (4 - len(neighbors(*tile))) * 3
        # Don't sit on the exit itself; create an obstacle BEFORE it.
        exit_penalty = 25 if tile == exit_tile else 0
        score = (arrival_penalty + future_penalty + time_to_block * 2
                 + partnership_penalty + exit_penalty - corridor_bonus)
        options.append((score, tile))

    # If already positioned on an approaching escape tile, HOLD the line.
    # Without this, H leaves the blocking spot and follows G around.
    if hunter in escape_path[1:7] and shortest_distance(hunter, stalker) >= 3:
        hunter_target = hunter
        return hunter
    if options:
        hunter_target = min(options)[1]
        return hunter_target
    return hunter


def alien_turn(protected=False):
    """returns a warning string if the aliens are nearby, or a game-over string if caught"""
    global turn
    turn += 1
    warnings = []
    player = (s["px"], s["py"])
    # sprints when far from the individual target, moves normally when nearby.
    sprint_distance = 5

    # hunter plans its separate move first, independent of G's chase goal.
    target = hunter_goal(player)
    for i in (0, 1):
        if alien_stunned[i] > 0:
            alien_stunned[i] -= 1
            continue

        here = tuple(s["aliens"][i])
        goal = player if i == 0 else target
        distance_to_goal = shortest_distance(here, goal)
        steps = 2 if distance_to_goal > sprint_distance else 1

        for step in range(steps):
            here = tuple(s["aliens"][i])
            # Aliens are incorporeal to each other: does NOT block the hunter
            path = route(here, goal)
            chosen = path[1] if len(path) > 1 else here
            if i == 1 and chosen == here and here == target and step == 0:
                warnings.append("The Hunter is holding your escape route!")

            # During the turn a trap is placed, aliens cannot attack.
            # They stop beside the player instead of entering their tile.
            if protected and chosen == player:
                break
            s["aliens"][i] = list(chosen)
            if chosen == player:
                return "An alien caught you. Game Over!"
            trap = trap_at(*chosen)
            if trap:
                s["tl"].remove(trap)
                alien_stunned[i] = 3
                warnings.append(alien_names[i] + " walked into your trap and is stunned!")
                break  # A trapped alien cannot finish its sprint.

    if shortest_distance(tuple(s["aliens"][0]), player) <= 2:
        warnings.append("The alien is right behind you!")
    if shortest_distance(tuple(s["aliens"][1]), player) <= 3:
        warnings.append("The Hunter is cutting off your path!")
    return " ".join(dict.fromkeys(warnings))


for y in range(len(s["grid"])):
    for x in range(len(s["grid"][y])):
        if s["grid"][y][x] == "@":
            s["py"] = y
            s["px"] = x


s["aliens"] = [[20, 1], [14, 4]]
draw("Escape.")

loop = True
while loop:
    target_x = s["px"]
    target_y = s["py"]
    valid_move = False
    trap_placed = False
    msg = ""
    move = input("Enter your move: ").strip().upper()

    if move == "W":
        target_y -= 1
        valid_move = True
    elif move == "A":
        target_x -= 1
        valid_move = True
    elif move == "S":
        target_y += 1
        valid_move = True
    elif move == "D":
        target_x += 1
        valid_move = True
    elif move == "T":
        if s["traps"] > 0:
            if any(t["tx"] == s["px"] and t["ty"] == s["py"] for t in s["tl"]):
                msg = "You already placed a trap here genius."
            else:
                s["traps"] -= 1
                s["flash"] -= 1
                s["tl"].append({"tx": s["px"], "ty": s["py"], "triggered": False})
                trap_placed = True
                msg = "Trap placed. Step off to arm it."
        else:
            msg = "No traps left. you're cooked."
    elif move == "E":
        if any(s["grid"][y][x] == "$" for x, y in neighbors(s["px"], s["py"])):
            enter_shop()
            msg = "shop closed brokie."
        else:
            msg = "Get closer to the shop first. Look for the $ sign."
        draw(msg)
        continue
    elif len(move) == 2 and move[0] == "F":
        direction = move[1]
        dx = 0
        dy = 0
        if direction == "W":
            dy -=1
        elif direction == "A":
            dx -= 1
        elif direction == "S":
            dy += 1
        elif direction == "D":
            dx += 1
        else:
            msg = "Invalid flash direction. Use F W, F A, F S or F D."
            draw(msg)
            continue

        if s["flash"] < 5:
            msg = "Not enough battery to fire flash!"
        else:
            s["flash"] -= 5
            s["heat"] += 20
            msg = "Flash fired!"
            for step in range(1, s["beam_range"] + 1):
                check_x = s["px"] + dx*step
                check_y = s["py"] + dy*step
                if not open_tile(check_x, check_y):
                    break
                for i, alien_pos in enumerate(s["aliens"]):
                    if alien_pos == [check_x, check_y]:
                        alien_stunned[i] = 3
                        msg += f" Stunned {alien_names[i]} for 3 turns!"
        valid_move = True
    elif move == "X":
        break
    else:
        draw("Invalid input")
        continue

    if valid_move:
        if not open_tile(target_x, target_y):
            msg = "That's a wall genius. Try the other way."
        elif s["grid"][target_y][target_x] == ">":
            draw("you made it out of the dark woods. want a medal?")
            break
        else:
            if any((target_x, target_y) == tuple(g) and alien_stunned[i] == 0
                   for i, g in enumerate(s["aliens"])):
                draw("you walked straight into an alien genius. Game over.")
                break
            if s["grid"][target_y][target_x] == "X":
                s["traps"] += 1
                s["tl"] = [t for t in s["tl"] if not (t["tx"] == target_x and t["ty"] == target_y)]
                msg = "Trap recovered!"
            s["grid"][target_y][target_x] = "@"
            left_trap = False
            for trap in s["tl"]:
                if trap["tx"] == s["px"] and trap["ty"] == s["py"]:
                    trap["triggered"] = True
                    left_trap = True
            if left_trap:
                s["grid"][s["py"]][s["px"]] = "X"
            elif (s["px"], s["py"]) == (6, 3):
                s["grid"][s["py"]][s["px"]] = "$"
            else:
                s["grid"][s["py"]][s["px"]] = "."
            s["px"] = target_x
            s["py"] = target_y
            s["flash"] -= 1
            s["heat"] = min(100, s["heat"] + 2)

    if s["flash"] <= 0:
        draw("Game Over! your flashlight died.")
        break
    # alien acts on all real player actions even a blocked movement.
    if valid_move or move == "T":
        danger = alien_turn(protected=trap_placed)
        if danger == "An alien caught you. Game Over!":
            draw(danger)
            break
        if danger:
            msg = (msg + " " + danger).strip()
    draw(msg)