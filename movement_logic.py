import os
import sys
from collections import deque

raw_map = [
    "#######################",
    "#@......*...###.......#",
    "#.######........*.....#",
    "#.....$..#...######.###",
    "#..*...............*..#",
    "#........###.....>....#",
    "#######################"
]
MAPS = {
    "forest1": [
        "############################################################",
        "#@......#..............#.....................#...........#",
        "#.......#..............#.....................#...........#",
        "#.......#..............#...........#####.....#...........#",
        "#.......#......#########.....................#...........#",
        "#..............#..................###########...........#",
        "###########....#..................#.....................#",
        "#......................############.....................#",
        "#......................#...............................#",
        "#......................#.................############..#",
        "#......................................................>#",
        "############################################################",
    ]
}
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
clear_first_level=False
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
                        alien_stunned[0] = 3

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
            clear_first_level = True
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

ship_map = [
    "        ###############[E]#############",
    "    ####...............................######",
    "  ##.........................................####",
    " #...............................................###",
    "#...................................................##",
    "#.......#########...........#########.................##",
    "#.......#.......#...........#.......#..................#",
    "#.......#...........................#...................#",
    "#.......#########...........#########....................#",
    "[R].................@..................................>...#",
    "#........................................................#",
    "#.......#########...........#########...................#",
    "#.......#...................#..........................#",
    "#.......#.......#...........#.......#.................##",
    "#.......#########...........#########...............##",
    "  ##.........................................######",
    "    ####...............................######",
    "        ###############[E]#############",
]

ship_map = [row.ljust(60) for row in ship_map]

engine_1_map = [
    "##############################",
    "#............................#",
    "#....######......######......#",
    "#....######......######......#",
    "#............................#",
    "#.............C..............#",
    "#............................#",
    "#....######......######......#",
    "#....######......######......#",
    "#............................#",
    "#............................#",
    "##############<###############",
]

engine_2_map = [
    "##############<###############",
    "#............................#",
    "#............................#",
    "#....######......######......#",
    "#....######......######......#",
    "#............................#",
    "#.............C..............#",
    "#............................#",
    "#....######......######......#",
    "#....######......######......#",
    "#............................#",
    "##############################",
]

reactor_map = [
    "##############################",
    "#............................#",
    "#......################......#",
    "#......################......#",
    "#............................#",
    "#.............C..............#",
    "#............................#",
    "#......################......#",
    "#......################......#",
    "#...........................<#",
    "#............................#",
    "##############################",
]


def open_tile(x, y):
    return (
        0 <= y < len(s["grid"])
        and 0 <= x < len(s["grid"][y])
        and s["grid"][y][x] not in ("#", " ")
    )


def draw_level_2(msg=""):
    os.system("cls" if os.name == "nt" else "clear")

    display = [row[:] for row in s["grid"]]

    if room == "ship":
        for trap in s["tl"]:
            display[trap["ty"]][trap["tx"]] = "X"

        if enemies_active:
            for i, (x, y) in enumerate(s["aliens"]):
                symbol = "G" if i == 0 else "H"

                if alien_stunned[i] > 0:
                    symbol = symbol.lower()

                display[y][x] = symbol

    display[s["py"]][s["px"]] = "@"

    print("LEVEL 2 -", room.upper())

    for row in display:
        print("".join(row))

    print()
    print("Flashlight:", s["flash"])
    print("Traps:", s["traps"])
    print("Engines repaired:", sum(engine_fixed.values()), "/ 2")

    if stage == "repair":
        print("Goal: repair both engines.")
    elif stage == "escape":
        print("Goal: check the controls at >.")
    elif stage == "reactor":
        print("Goal: reach the reactor room.")

    print("WASD move | E interact | T trap")
    print("FW / FA / FS / FD flashlight | X quit")
    print("C control panel | < return to ship")
    print("G Ghost | H Hunter | g/h stunned")

    if msg:
        print()
        print(msg)


def change_room(new_room, x, y):
    global room

    room = new_room
    s["grid"] = maps[room]
    s["px"] = x
    s["py"] = y


def near_tile(symbol):
    positions = [
        (s["px"], s["py"]),
        (s["px"] + 1, s["py"]),
        (s["px"] - 1, s["py"]),
        (s["px"], s["py"] + 1),
        (s["px"], s["py"] - 1),
    ]

    for x, y in positions:
        if open_tile(x, y):
            if s["grid"][y][x] == symbol:
                return True

    return False


def hunter_goal(player):
    if stage == "escape":
        destination = bow_position
    else:
        destination = (2, 9)

    path = route(player, destination)

    if len(path) > 4:
        return path[4]

    if path:
        return path[-1]

    return player


def use_panel():
    global stage, enemies_active, level_2_clear, enemy_delay

    if room in ("engine_1", "engine_2"):
        if not near_tile("C"):
            return "Move closer to the control panel."

        if engine_fixed[room]:
            return "This engine is already repaired."

        engine_fixed[room] = True

        if all(engine_fixed.values()):
            stage = "escape"
            enemies_active = True
            enemy_delay = 6

            return (
                "Both engines start with a deafening roar.\n"
                "Something climbs onto the ship.\n"
                "The Ghost and Hunter are here!\n"
                "Go to the controls at >."
            )

        return "Engine repaired. Find the other engine room."
        

    if room == "ship":
        if not near_tile(">"):
            return "There is nothing to use here."

        if stage == "repair":
            return "No power. Repair both engines first."

        stage = "reactor"

        return (
            "The engines are running, but the ship cannot move.\n"
            "The hull is damaged. The lifeboats are gone.\n"
            "There is no way out.\n"
            "You must destroy the ship with the creatures aboard.\n"
            "Go to the reactor room."
        )

    if room == "reactor":
        if not near_tile("C"):
            return "Move closer to the control panel."

        if not all(engine_fixed.values()):
            return "Repair both engines first."

        level_2_clear = True

        return (
            "You activate the ship's self-destruct system.\n"
            "The Ghost and Hunter smash through the door.\n"
            "A flash of light swallows everything.\n"
            "The ship, the creatures, and you are gone.\n"
            "THE END."
        )
def explosion_animation():
    import time

    frames = [
        r"""
                    !
                    !
             _______|_______
        ____/_______________\____
       /_________________________\
  ~~~~~\_________________________/~~~~~
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

          REACTOR OVERLOAD
        """,

        r"""
                  \ | /
                   \|/
             ______*_______
        ____/_____*#*______\____
       /_________*###*__________\
  ~~~~~\___________*____________/~~~~~~
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

           CORE UNSTABLE
        """,

        r"""
              \    |    /
               \   |   /
           ----- ***** -----
              **#######**
        ____***#########***____
       /___**#############**___\
  ~~~~~\_____***#######***_____/~~~~~~~
  ~~~~~~~~~~~~~*******~~~~~~~~~~~~~~~~

                BOOM!
        """,

        r"""
        .       \  |  /        .
             .   \ | /    .
          *   ***#####***   *
       .   **#############**   .
     -----#################-----
       .   **#############**   .
          *   ***#####***   *
             .   / | \    .
        .       /  |  \        .

                BOOM!
        """,

        r"""
       #           .             /
              *         #
   \                  .                 *
          .      *           /
      #                *
             /                  #
  ~~~~~~~~ . ~~~~~ * ~~~~~~ . ~~~~~~~~~~
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

          THE SHIP BREAKS APART
        """,

        r"""
             .                 .
                       .
       .           .               .

                 .
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                SILENCE.
        """,

        r"""


  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


       The ship is gone.
       The Ghost and Hunter are gone.
       You never leave the reactor room.

               THE END
        """,
    ]

    time.sleep(1)

    for i, frame in enumerate(frames):
        os.system("cls" if os.name == "nt" else "clear")
        print(frame, flush=True)

        if i < 2:
            time.sleep(0.8)
        elif i < 5:
            time.sleep(0.35)
        else:
            time.sleep(1.2)


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

    enemies_active = False
    enemy_delay = 0
    level_2_clear = False
    return_position = (20, 9)

    s["grid"] = maps["ship"]
    s["px"] = 20
    s["py"] = 9

    s["tl"] = []
    s["aliens"] = [[48, 4], [46, 14]]

    alien_names = ["GHOST", "HUNTER"]
    alien_stunned = [0, 0]
    hunter_target = None
    turn = 0

    s["flash"] = max(s["flash"], 60)
    s["traps"] = max(s["traps"], 6)

    maps["ship"][9][20] = "."

    for y, row in enumerate(maps["ship"]):
        for x, tile in enumerate(row):
            if tile == ">":
                bow_position = (x, y)

    draw_level_2(
        "You find an abandoned ship.\n"
        "Repair both engines and try to escape."
    )

    while not level_2_clear:
        move = input("Enter your move: ").strip().upper()
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
                msg = "You cannot go there."

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
                    msg = "Engine room. Find C and press E."

                elif room == "ship" and tile == "R":
                    return_position = (s["px"], s["py"])
                    change_room("reactor", 27, 9)

                    changed_map = True
                    msg = "Reactor room. Find the control panel."

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

                action_taken = True

        elif move == "E":
            msg = use_panel()
            action_taken = room == "ship"

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

            elif s["flash"] < 5:
                msg = "Not enough flashlight battery."

            else:
                directions = {
                    "W": (0, -1),
                    "A": (-1, 0),
                    "S": (0, 1),
                    "D": (1, 0),
                }

                dx, dy = directions[move[1]]

                s["flash"] -= 5
                action_taken = True
                msg = "Flash fired."

                for step in range(1, s["beam_range"] + 1):
                    check_x = s["px"] + dx * step
                    check_y = s["py"] + dy * step

                    if not open_tile(check_x, check_y):
                        break

                    if enemies_active:
                        for i, enemy in enumerate(s["aliens"]):
                            if enemy == [check_x, check_y]:
                                alien_stunned[i] = 3
                                msg += (
                                    " "
                                    + alien_names[i]
                                    + " stunned!"
                                )

        else:
            msg = "Invalid input."

        if level_2_clear:
            draw_level_2("You activate the reactor. There is no turning back.")
            explosion_animation()
            break

        if (
            action_taken
            and room == "ship"
            and enemies_active
            and not changed_map
        ):
            if enemy_delay > 0:
                enemy_delay -= 1

            else:
                danger = alien_turn(protected=trap_placed)

                if danger == "An alien caught you. Game Over!":
                    draw_level_2(
                        "A creature caught you. Game Over!"
                    )
                    break

                if danger:
                    msg = (msg + "\n" + danger).strip()

        draw_level_2(msg)
