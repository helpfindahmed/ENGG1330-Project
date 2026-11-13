import os
import sys
import textwrap
import time

from endings import explosion_animation, reactor_decision, secret_ending
from engine_puzzles import IGNITION_SLOT, PANEL_HINTS, panel_lines, solves_panel
from game_maps import engine_1_map, engine_2_map, raw_map, reactor_map, ship_map
from intro import play_introduction
from terminal_ui import intro_draw, intro_terminal_size, panel_answer
from turn_input import PASTED_MOVE, read_turn


def title_screen():
    """Start the full game or leave from the player-facing title screen."""
    lines = [
        "+--------------------------------------+",
        "|          PROJECT CONTAINMENT         |",
        "+--------------------------------------+",
        "",
        "Survive the forest. Get back to your ship.",
        "",
        "[Enter] Start game",
        "[X] Quit",
    ]
    feedback = []
    while True:
        choice = panel_answer(lines + feedback, "> ", 16).lower()
        if choice in ("", "x"):
            return "full" if not choice else "quit"
        feedback = ["", "Press Enter to start or X to quit."]


def confirm_forest_exit(question):
    """A confirmation never spends resources or advances the combat clock."""
    feedback = ""
    while True:
        lines = [question, "", "[1] Yes", "[2] No"]
        if feedback:
            lines += ["", feedback]
        choice = panel_answer(lines, "Choose 1 or 2, then press Enter > ")
        if choice in ("1", "2"):
            return choice == "1"
        feedback = "Invalid choice. Enter 1 or 2."


def debug_menu():
    lines = [
        "DEBUG MENU",
        "Press Enter for the full game.",
        "Type 'forest' to start at the forest.",
        "Type 'ship' to start at the ship.",
    ]
    feedback = []
    while True:
        command = panel_answer(lines + feedback, "> ", 16).lower()
        if command in ("", "forest", "ship"):
            return command or "full"
        feedback = ["", "Unknown command. Use forest, ship, or press Enter."]


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
     }

alien_names = ["GHOST", "HUNTER"]
alien_stunned = [0, 0]
turn = 0
help_unlocked = False


def enter_shop():
    feedback = ""
    while True:
        lines = [
            "SUPPLY SHOP",
            "",
            f"[1] +50 battery (40 coins) | Bought {s['battery_buys']}/2",
            "[2] 1 trap (20 coins)",
            "[3] 2 Big Bangs (30 coins)",
            "",
            f"Coins: {s['coins']}",
            "Enter 1, 2, or 3 to buy, or X to leave.",
        ]
        if feedback:
            lines.extend(("", feedback))
        choice = panel_answer(lines, "Shop choice > ").upper()
        if choice == "X":
            return "You leave the shop."
        if choice in ("1", "2", "3"):
            break
        feedback = "Invalid choice. Enter 1, 2, 3, or X."

    item, amount, price = {
        "1": ("flash", 50, 40),
        "2": ("traps", 1, 20),
        "3": ("bangs", 2, 30),
    }[choice]
    if s["coins"] < price:
        return f"You need {price} coins for that purchase."
    if item == "flash":
        if s["battery_buys"] >= 2:
            return "Battery sold out. You have already bought two."
        s["battery_buys"] += 1
    s["coins"] -= price
    s[item] += amount
    return {
        "1": "Purchased +50 flashlight battery.",
        "2": "Purchased 1 trap.",
        "3": "Purchased 2 Big Bangs.",
    }[choice]


def open_terminal():
    global help_unlocked
    help_unlocked = True
    panel_answer([
        "SURVIVAL MANUAL (PAGE 1/2)",
        "",
        "WASD       Move one tile per keypress (costs battery)",
        "F + WASD   Aim a flash attack to stun enemies",
        "T          Drop a trap. Step off it to arm it.",
        "E          Use the help terminal, shop, or control panel",
        "H          Reopen this manual",
        "X          Quit game",
    ], "Press Enter for next page > ", 0)
    panel_answer([
        "SURVIVAL MANUAL (PAGE 2/2)",
        "",
        "GHOSTS (G) - Roam the forest. Avoid their paths.",
        "HUNTER (H) - Actively tracks you. Can cut you off.",
        "",
        "1. Collect coins (*) to buy supplies at the shop ($).",
        "2. Reach > on the right to return to your ship.",
        "3. Repair the upper engine [1], then the lower engine [2].",
        "4. Reach the reactor room [R] on the left side of the deck.",
    ], "Press Enter to close > ", 0)


def open_tile(x, y):
    return (
        0 <= y < len(s["grid"])
        and 0 <= x < len(s["grid"][y])
        and s["grid"][y][x] not in ("#", "?", "$", " ")
    )


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


def terminal_ready():
    size = intro_terminal_size()
    if size[0] >= 80 and size[1] >= 24:
        return True
    intro_draw([], "", size)
    return False


def read_map_turn(redraw):
    while True:
        if terminal_ready():
            move = read_turn()
            if move == "X" or terminal_ready():
                return move
        panel_answer(["Terminal resized. Press Enter to resume."], "Continue > ", 0)
        redraw()


def print_dialogue(msg, width=78, max_lines=4):
    if not msg:
        return
    lines = []
    for paragraph in msg.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=width) or [""])
    for line in lines[:max_lines]:
        print(line)


MAP_COLORS = {
    "@": "96", "☺": "96",
    "1": "93", "2": "93", "R": "93", "C": "93", "?": "93",
    ">": "92", "<": "92",
    "$": "95", "*": "95",
}


def plain_map():
    return (not sys.stdout.isatty() or os.environ.get("TERM") == "dumb"
            or "NO_COLOR" in os.environ)


def player_icon():
    encoding = (sys.stdout.encoding or "").lower().replace("-", "")
    # Use the one-cell text face in UTF-8 terminals, including Windows ConPTY.
    return "☺" if not plain_map() and encoding == "utf8" else "@"


def print_map(display, panel, show_floor):
    color = os.name == "posix" and bool(os.environ.get("TERM")) and not plain_map()
    icon = player_icon()
    for index, row in enumerate(display):
        tiles = "".join(row).replace("@", icon)
        if not show_floor:
            tiles = tiles.replace(".", " ")
        side = panel[index].replace("@", icon) if index < len(panel) else ""
        tiles = f"{tiles:<60}"
        if color:
            tiles = "".join(
                f"\033[{MAP_COLORS[tile]}m{tile}\033[0m" if tile in MAP_COLORS else tile
                for tile in tiles
            )
        print(f"{tiles} {side}".rstrip())


def show_forest_briefing():
    panel_answer([
        "LEVEL 1 - SURVIVE THE FOREST",
        "",
        f"You are {player_icon()}, near the top-left corner.",
        "Reach > on the right side of the map to return to the ship.",
        "",
        "Press W up, A left, S down, or D right to move one tile.",
        "Each step drains your battery. Walls (#) block movement.",
        "",
        "Stand next to ? and press E for help. H reopens it later.",
        "Walk over * to collect coins. Press E next to $ to buy supplies.",
        "",
        "Press T to drop a trap. Move off it to arm it.",
        "Press F, then a direction key, to fire a flash.",
        "Press X to quit.",
    ], "Press Enter to enter the forest > ", 0)


def draw(msg=""):
    if not terminal_ready():
        return
    os.system('cls' if os.name == 'nt' else 'clear')
    display = [row[:] for row in s["grid"]]
    for i, (x, y) in enumerate(s["aliens"]):
        if (x, y) != (s["px"], s["py"]):
            symbol = "G" if i == 0 else "H"
            if alien_stunned[i] > 0:
                symbol = symbol.lower()
            display[y][x] = symbol
    print("LEVEL 1 - FOREST")
    print("Goal: Reach > on the right to return to your ship.")
    panel = [
        f"Flash: {s['flash']}%",
        f"Coins: {s['coins']}",
        f"Charges: {s['bangs']}",
        f"Traps: {s['traps']}",
        "",
        "@ You  # Wall",
        "> Ship exit",
        "? Help  $ Shop",
        "* Coins",
        "WASD Move",
        "E Use  X Quit",
        "T Trap  F Flash",
    ]
    print_map(display, panel, show_floor=False)
    print_dialogue(msg)


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


def ghost_goal(player):
    """Return a reachable tile ahead of the player to obstruct the escape route."""
    ghost = tuple(s["aliens"][0])
    stalker = tuple(s["aliens"][1])
    exit_tile = next(
        (
            (x, y)
            for y, row in enumerate(s["grid"])
            for x, tile in enumerate(row)
            if tile == ">"
        ),
        player,
    )

    # Replan every turn: use actual wall layout and the most recent player move.
    # Aliens can cross each other, so neither obstructs the escape route.
    escape_path = route(player, exit_tile)
    if not escape_path:
        return ghost

    # Evaluate tiles AHEAD of the player. A good barricade is one the
    # Ghost can reach before the player, preferably at a narrow junction.
    options = []
    for index, tile in enumerate(escape_path[1:], start=1):
        time_to_block = shortest_distance(ghost, tile)
        if time_to_block == 999:
            continue
        player_time = index
        # More valuable if Ghost can beat the player to the square.
        arrival_penalty = max(0, time_to_block - player_time + 1) * 12
        # Prefer nearer upcoming barricades, without chasing the player.
        future_penalty = abs(index - 4) * 2
        # Stay away from H so they are not walking together.
        partnership_penalty = max(0, 5 - shortest_distance(stalker, tile)) * 12
        # Narrow lanes are easier to block.
        corridor_bonus = (4 - len(neighbors(*tile))) * 3
        # Don't sit on the exit itself; create an obstacle BEFORE it.
        exit_penalty = 25 if tile == exit_tile else 0
        score = (arrival_penalty + future_penalty + time_to_block * 2
                 + partnership_penalty + exit_penalty - corridor_bonus)
        options.append((score, tile))

    # If already positioned on an approaching escape tile, hold the line.
    if ghost in escape_path[1:7] and shortest_distance(ghost, stalker) >= 3:
        return ghost
    if options:
        return min(options)[1]
    return ghost


def hunter_goal(player):
    """Return the Hunter's current reachable route target: the player."""
    return player


def alien_turn(protected=False, aggressive=False):
    """Return a warning if a creature is nearby, or a game-over string if caught."""
    global turn
    turn += 1
    warnings = []
    player = (s["px"], s["py"])
    # The forest gives the player time to learn the controls. Once aboard the
    # ship, the creatures attack immediately.
    if not aggressive and turn <= 8:
        if turn == 8:
            return "You hear something moving in the darkness..."
        return ""

    target = hunter_goal(player)
    ghost_target = (
        player
        if shortest_distance(tuple(s["aliens"][0]), player) <= 1
        else ghost_goal(player)
    )
    for i in (0, 1):
        if alien_stunned[i] > 0:
            alien_stunned[i] -= 1
            continue

        here = tuple(s["aliens"][i])
        goal = ghost_target if i == 0 else target
        distance_to_player = shortest_distance(here, player)
        sprint_limit = 4 if i == 0 else 8
        steps = 2 if distance_to_player > sprint_limit else 1

        for step in range(steps):
            here = tuple(s["aliens"][i])
            # Aliens are incorporeal to each other: does NOT block the hunter
            path = route(here, goal)
            chosen = path[1] if len(path) > 1 else here
            if i == 1 and chosen == here and here == target and step == 0:
                warnings.append("The Hunter is holding your escape route!")

            # During the turn a trap is placed, creatures cannot attack.
            # They stop beside the player instead of entering their tile.
            if protected and chosen == player:
                break
            s["aliens"][i] = list(chosen)
            if chosen == player:
                return "A creature caught you. Game Over!"
            trap = trap_at(*chosen)
            if trap:
                s["tl"].remove(trap)
                alien_stunned[i] = 3
                warnings.append(alien_names[i] + " walked into your trap and is stunned!")
                break  # A trapped creature cannot finish its sprint.

    if shortest_distance(tuple(s["aliens"][0]), player) <= 2:
        warnings.append("The Ghost is right behind you!")
    if shortest_distance(tuple(s["aliens"][1]), player) <= 3:
        warnings.append("The Hunter is cutting off your path!")
    return " ".join(dict.fromkeys(warnings))


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

for y in range(len(s["grid"])):
    for x in range(len(s["grid"][y])):
        if s["grid"][y][x] == "@":
            s["py"] = y
            s["px"] = x


s["aliens"] = [[30, 8], [28, 2]]
debug_mode = debug_menu() if "--debug" in sys.argv[1:] else title_screen()
if debug_mode == "quit":
    raise SystemExit(0)
if debug_mode == "full":
    play_introduction()
elif debug_mode == "forest":
    print("Starting forest debug sequence...")
    time.sleep(0.5)

if debug_mode != "ship":
    show_forest_briefing()
    draw("Move with WASD. Stand next to ? and press E for more help.")

clear_first_level = debug_mode == "ship"
while debug_mode != "ship":
    target_x = s["px"]
    target_y = s["py"]
    valid_move = False
    action_taken = False
    trap_placed = False
    msg = ""
    move = read_map_turn(draw)

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
                action_taken = True
                msg = "Trap placed. Step off to arm it."
        else:
            msg = "No traps left. you're cooked."

    elif move == "H" and help_unlocked:
        open_terminal()
        draw("Help menu closed.")
        continue
    elif move == "E":
        if near_tile("?"):
            open_terminal()
            msg = "Manual closed."
            action_taken = True
        elif near_tile("$"):
            msg = enter_shop()
            action_taken = True
        else:
            msg = "Get closer to the shop ($) or terminal (?) first."
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
            msg = "Use W, A, S, or D to aim the flash."
            draw(msg)
            continue

        if s["bangs"] < 1:
            msg = "Out of Big Bangs!"
        else:
            s["bangs"] -= 1
            action_taken = True
            msg = "Big Bang fired!"
            for step in range(1, s["beam_range"] + 1):
                check_x = s["px"] + dx*step
                check_y = s["py"] + dy*step
                if not open_tile(check_x, check_y):
                    break
                for i, alien_pos in enumerate(s["aliens"]):
                    if alien_pos == [check_x, check_y]:
                        alien_stunned[i] = 5
                        msg += f" Stunned {alien_names[i]} for 5 turns!"

    elif move == "X":
        break
    elif move == PASTED_MOVE:
        draw("Press one key at a time to move. Pasted text was ignored.")
        continue
    else:
        draw("Unknown command. Use WASD to move, E to interact, or X to quit.")
        continue

    if valid_move:
        if not open_tile(target_x, target_y):
            if (
                0 <= target_y < len(s["grid"])
                and 0 <= target_x < len(s["grid"][target_y])
                and s["grid"][target_y][target_x] == "?"
            ):
                msg = "The terminal blocks the path. Stand beside it and press E."
            else:
                msg = "Dense undergrowth blocks that path."
        elif s["grid"][target_y][target_x] in (">", "<"):
            ship_exit = s["grid"][target_y][target_x] == ">"
            question = ("Make a run towards the ship?" if ship_exit
                        else "Go deeper into the forest?")
            if not confirm_forest_exit(question):
                draw("You stay in the forest.")
                continue
            if ship_exit:
                clear_first_level = True
                draw("You escaped the forest and reached your ship.")
            else:
                secret_ending()
            break
        else:
            if any((target_x, target_y) == tuple(g) and alien_stunned[i] == 0
                   for i, g in enumerate(s["aliens"])):
                draw("You walked straight into a creature. Game over.")
                break

            if s["grid"][target_y][target_x] == "X":
                s["traps"] += 1
                s["tl"] = [t for t in s["tl"] if not (t["tx"] == target_x and t["ty"] == target_y)]
                msg = "Trap recovered!"

            if s["grid"][target_y][target_x] == "*":
                s["coins"] += 10
                msg = "Coins gained!"

            s["grid"][target_y][target_x] = "@"
            left_trap = False
            for trap in s["tl"]:
                if trap["tx"] == s["px"] and trap["ty"] == s["py"]:
                    trap["triggered"] = True
                    left_trap = True
            if left_trap:
                s["grid"][s["py"]][s["px"]] = "X"
            elif (s["px"], s["py"]) in shop_positions:
                s["grid"][s["py"]][s["px"]] = "$"
            else:
                s["grid"][s["py"]][s["px"]] = "."
            s["px"] = target_x
            s["py"] = target_y
            s["flash"] -= 1
            action_taken = True
            if not msg and near_tile("$"):
                msg = "A mysterious store stands in the middle of the forest."

    if s["flash"] <= 0:
        draw("Game Over! your flashlight died.")
        break
    if action_taken:
        danger = alien_turn(protected=trap_placed)
        if danger == "A creature caught you. Game Over!":
            draw(danger)
            break
        if danger:
            msg = (msg + " " + danger).strip()
    draw(msg)

def at_control_panel():
    return s["grid"][s["py"]][s["px"]] == "C" or near_tile("C")


def ship_objective():
    if room == "ship":
        if not engine_fixed["engine_1"]:
            return "Enter the upper engine room [1] at the top of the deck."
        if not engine_fixed["engine_2"]:
            return "Enter the lower engine room [2] at the bottom of the deck."
        return "Reach the reactor room [R] on the left side of the deck."
    if room == "reactor" and stage == "repair":
        return "Return via < and repair both engines first."
    if room in engine_fixed:
        if engine_fixed[room]:
            return "Engine repaired. Walk to < to return to the main deck."
        if room == "engine_2" and not engine_fixed["engine_1"]:
            return "Return via < and repair the upper engine [1] first."
    return "Stand next to C or on it, then press E."


def draw_level_2(msg=""):
    if not terminal_ready():
        return
    os.system("cls" if os.name == "nt" else "clear")

    display = [row[:] for row in s["grid"]]

    if room == "ship":
        # Label the doors on screen without changing their collision tiles.
        upper_door = s["grid"][0].index("E")
        lower_door = s["grid"][-1].index("E")
        display[0][upper_door] = "1"
        display[-1][lower_door] = "2"
        for trap in s["tl"]:
            display[trap["ty"]][trap["tx"]] = "X"

        if enemies_active:
            for i, (x, y) in enumerate(s["aliens"]):
                symbol = "G" if i == 0 else "H"

                if alien_stunned[i] > 0:
                    symbol = symbol.lower()

                display[y][x] = symbol

    display[s["py"]][s["px"]] = "@"

    room_names = {
        "ship": "MAIN DECK",
        "engine_1": "UPPER ENGINE ROOM",
        "engine_2": "LOWER ENGINE ROOM",
        "reactor": "REACTOR ROOM",
    }
    upper = "ON" if engine_fixed["engine_1"] else "OFF"
    lower = "ON" if engine_fixed["engine_2"] else "OFF"
    repaired = sum(engine_fixed.values())
    print(f"L2 - {room_names[room]} | Engines: {repaired}/2 | "
          f"Upper: {upper} | Lower: {lower}")
    print(f"Goal: {ship_objective()}")
    panel = [
        f"Flash: {s['flash']}%",
        f"Traps: {s['traps']}",
        "",
        "@ You  # Wall",
        ". Walkable floor",
    ]
    if room == "ship":
        panel.extend(("[1] Upper engine", "[2] Lower engine", "[R] Reactor", "> Helm"))
    else:
        panel.extend(("C Control panel", "< Back to deck"))
    panel.append("E Use  X Quit")
    print_map(display, panel, show_floor=True)

    # Reserve two lines above the map and one for the input prompt.
    print_dialogue(msg, max_lines=min(4, 21 - len(display)))


def change_room(new_room, x, y):
    global room

    room = new_room
    s["grid"] = maps[room]
    s["px"] = x
    s["py"] = y


def use_panel():
    global stage, enemies_active, level_2_clear

    if room in engine_fixed:
        if not at_control_panel():
            return "Walk to C or a tile beside it, then press E."

        if engine_fixed[room]:
            return "This engine is already repaired."

        if room == "engine_2" and not engine_fixed["engine_1"]:
            return "Repair the upper engine first to get its starter position."

        hints = PANEL_HINTS[room]
        invalid_format = False
        while True:
            lines = list(panel_lines(room))
            if engine_attempts[room]:
                hint_number = min(engine_attempts[room], len(hints))
                lines.extend((
                    "",
                    "Incorrect setting. Check the clues and try again.",
                    f"Hint {hint_number}/{len(hints)}: {hints[hint_number - 1]}",
                ))
            if invalid_format:
                lines.extend(("", "Enter three digits, or X to close the panel."))
            answer = panel_answer(lines)
            if answer.upper() == "X":
                return "Panel closed."
            digits = "".join(answer.split())
            invalid_format = len(digits) != 3 or not digits.isascii() or not digits.isdecimal()
            if invalid_format:
                continue
            if solves_panel(room, digits):
                break
            engine_attempts[room] += 1

        if room == "engine_1":
            success = (f"Correct! Upper engine repaired. Starter position: "
                       f"{IGNITION_SLOT}.")
        else:
            success = "Correct! Lower engine repaired. Both engines are on."
        panel_answer([success], "Press Enter to return to the map > ", 0)

        engine_fixed[room] = True
        if room == "engine_1":
            s["flashlight_disabled"] = True

        if all(engine_fixed.values()):
            stage = "escape"
            enemies_active = True

            return (
                "Both engines are repaired, but the ship shudders.\n"
                "The Ghost and Hunter are here!\n"
                "Return via < and reach the reactor [R] on the deck."
            )

        return (
            "Upper engine repaired. The ship lights are back on.\n"
            "Return via < and enter the lower engine room [2]."
        )


    if room == "ship":
        if not near_tile(">"):
            return "Nothing to use here. Walk through a marked door."

        if stage == "repair":
            return "No power. Repair both engines first."

        stage = "reactor"

        return (
            "The hull is damaged. The ship cannot take off.\n"
            "Go to the reactor room [R] with the creatures still aboard."
        )

    if room == "reactor":
        if not at_control_panel():
            return "Walk to C or a tile beside it, then press E."

        if not all(engine_fixed.values()):
            return "Repair both engines first."

        reactor_decision()
        level_2_clear = True
        return "The reactor passes the point of recovery."
if clear_first_level:
    maps = {
        "ship": [list(row) for row in ship_map],
        "engine_1": [list(row) for row in engine_1_map],
        "engine_2": [list(row) for row in engine_2_map],
        "reactor": [list(row) for row in reactor_map],
    }

    room = "ship"
    stage = "repair"

    engine_fixed = {
        "engine_1": False,
        "engine_2": False,
    }
    engine_attempts = dict.fromkeys(engine_fixed, 0)

    enemies_active = False
    level_2_clear = False
    ship_entry = next(
        (
            (x, y)
            for y, row in enumerate(engine_1_map)
            for x, tile in enumerate(row)
            if tile == "<"
        ),
        None,
    )
    if ship_entry is None:
        raise ValueError("Engine map is missing its first < entry tile.")
    return_position = ship_entry

    s["grid"] = maps["ship"]
    s["px"], s["py"] = ship_entry

    s["tl"] = []
    s["aliens"] = [[50, 6], [40, 8]]
    maps["ship"][9][20] = "."

    alien_names = ["GHOST", "HUNTER"]
    alien_stunned = [0, 0]
    turn = 0

    panel_answer([
        "LEVEL 2 - CRASHED SHIP",
        "",
        "You made it back to your ship.",
        "Your battery keeps draining until the upper engine is repaired.",
        "",
        "Walk through [1] at the top of the deck. Find C and press E beside it.",
        "After the repair, use < to return and enter [2] at the bottom.",
    ], "Press Enter to board your ship > ", 0)
    draw_level_2("You're aboard. The ship is dark and powerless.")

    while not level_2_clear:
        move = read_map_turn(draw_level_2)
        move = move.replace(" ", "")

        msg = ""
        action_taken = False
        trap_placed = False
        changed_map = False

        if move == "X":
            break

        elif move in ("W", "A", "S", "D"):
            target_x = s["px"]
            target_y = s["py"]

            if move == "W":
                target_y -= 1
            elif move == "S":
                target_y += 1
            elif move == "A":
                target_x -= 1
            elif move == "D":
                target_x += 1

            if not open_tile(target_x, target_y):
                if room == "ship":
                    msg = "A sealed bulkhead blocks that route."
                elif room.startswith("engine_"):
                    msg = "The engine-room wall blocks that route."
                else:
                    msg = "The reactor-room wall blocks that route."

            else:
                tile = s["grid"][target_y][target_x]
                caught = False

                if room == "ship" and enemies_active:
                    for i, enemy in enumerate(s["aliens"]):
                        if (
                            enemy == [target_x, target_y]
                            and alien_stunned[i] == 0
                        ):
                            caught = True

                if caught:
                    draw_level_2(
                        "You walked straight into a creature. Game Over."
                    )
                    break

                if room == "ship":
                    for trap in s["tl"]:
                        if (
                            trap["tx"] == s["px"]
                            and trap["ty"] == s["py"]
                        ):
                            trap["triggered"] = True

                if room == "ship" and tile == "E":
                    return_position = (s["px"], s["py"])

                    if target_y == 0:
                        change_room("engine_1", 14, 10)
                    else:
                        change_room("engine_2", 14, 1)

                    changed_map = True
                    msg = "You entered the upper engine room." if target_y == 0 else (
                        "You entered the lower engine room."
                    )

                elif room == "ship" and tile == "R":
                    return_position = (s["px"], s["py"])
                    change_room("reactor", 27, 9)

                    changed_map = True
                    msg = "You entered the reactor room."

                elif room != "ship" and tile == "<":
                    change_room(
                        "ship",
                        return_position[0],
                        return_position[1],
                    )

                    changed_map = True
                    msg = "You return to the deck."

                else:
                    s["px"] = target_x
                    s["py"] = target_y
                    if not s["flashlight_disabled"]:
                        s["flash"] -= 1
                action_taken = True


        elif move == "H" and help_unlocked:
            open_terminal()
            draw_level_2("Help menu closed.")
            continue
        elif move == "E":
            msg = use_panel()
            action_taken = room == "ship" and enemies_active and near_tile(">")

        elif move == "T":
            if room != "ship":
                msg = "You can only place traps on the deck."

            elif s["traps"] <= 0:
                msg = "No traps left."

            elif any(
                trap["tx"] == s["px"]
                and trap["ty"] == s["py"]
                for trap in s["tl"]
            ):
                msg = "There is already a trap here."

            else:
                s["traps"] -= 1

                s["tl"].append({
                    "tx": s["px"],
                    "ty": s["py"],
                    "triggered": False,
                })

                trap_placed = True
                action_taken = True
                msg = "Trap placed. Step off to arm it."


        elif move in ("FW", "FA", "FS", "FD"):
            if room != "ship":
                msg = "There are no enemies in this room."
            elif s["bangs"] < 1:
                msg = "Out of Big Bangs!"
            else:
                directions = {
                    "W": (0, -1),
                    "A": (-1, 0),
                    "S": (0, 1),
                    "D": (1, 0),
                }
                dx, dy = directions[move[1]]
                s["bangs"] -= 1
                action_taken = True
                msg = "Big Bang fired!"
                for step in range(1, s["beam_range"] + 1):
                    check_x = s["px"] + dx * step
                    check_y = s["py"] + dy * step
                    if not open_tile(check_x, check_y):
                        break
                    if enemies_active:
                        for i, enemy in enumerate(s["aliens"]):
                            if enemy == [check_x, check_y]:
                                alien_stunned[i] = 5
                                msg += f" {alien_names[i]} stunned for 5 turns!"

        elif move == PASTED_MOVE:
            msg = "Press one key at a time to move. Pasted text was ignored."
        elif move == "F?":
            msg = "Use W, A, S, or D to aim the flash."
        else:
            msg = "Unknown command. Use WASD to move, E to interact, or X to quit."

        if level_2_clear:
            explosion_animation()
            break

        if (
            action_taken
            and room == "ship"
            and enemies_active
            and not changed_map
        ):
            danger = alien_turn(protected=trap_placed, aggressive=True)

            if danger == "A creature caught you. Game Over!":
                draw_level_2(
                    "A creature caught you. Game Over!"
                )
                break

            if danger:
                msg = (msg + "\n" + danger).strip()

        if s["flash"] <= 0 and not s["flashlight_disabled"]:
            draw_level_2("Your flashlight died. The creatures take you in the dark. GAME OVER.")
            break

        draw_level_2(msg)
