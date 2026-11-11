import os
import textwrap

raw_map = [
    "##########################################################",
    "#@.*........*....###......*..............*.......*...$...#",
    "#...#...#....*....#....#......######.........#.......*...#",
    "#.?.#...####...........#......#....#.........#.....*.....#",
    "#...*...#......#########......######.........#..*........#",
    "#####...#.*....#.*.......................*...#####.#####.#",
    "#...*..........#.........#####.......###.................#",
    "#...#####......########......#.......#.#.*...*...........#",
    "#...#.*.....*................#.......###...............>.#",
    "#..........#####......*......#...*............############",
    "#...$...*..#...#......*..................................#",
    "##########################################################",
]

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


def show_status():
    flashlight = "OFF (ship lights)" if s["flashlight_disabled"] else f"{s['flash']}%"
    print(f" Flashlight  : {flashlight}")
    print(f" Coins       : {s['coins']}")
    print(f" Big Bangs   : {s['bangs']}")
    print(f" Traps Left  : {s['traps']}")


def enter_shop():
    # Show stock limit dynamically
    print(f"enter 1 for +50 Battery (Bought {s['battery_buys']}/2) - 40cc")
    print("enter 2 for 1 Trap            - 20cc")
    print("enter 3 for 2 Big Bangs       - 30cc")
    try:
        opt = int(input())
    except ValueError:
        print("Invalid input")
        return

    if (opt == 1) and s["coins"] >= 40:
        if s["battery_buys"] < 2:
            s["flash"] += 50
            s["coins"] -= 40
            s["battery_buys"] += 1
        else:
            print("Out of stock! You already bought batteries twice.")
    elif (opt == 2) and s["coins"] >= 20:
        s["traps"] += 1
        s["coins"] -= 20
    elif (opt == 3) and s["coins"] >= 30:
        s["bangs"] += 2
        s["coins"] -= 30
    elif opt not in (1, 2, 3):
        print("invalid input")
    else:
        print("Not enough money")


def open_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("SURVIVAL MANUAL (PAGE 1/2)")
    print("-" * 40)
    print("MISSION LOG:")
    print("You are a space engineer. Your ship crashed in a")
    print("dark, uncharted forest. The radar shows ship parts")
    print("scattered nearby. You need to fix the ship to survive.")
    print("\nCONTROLS:")
    print("W A S D   - Move (Costs battery)")
    print("F + Dir   - Flash Attack (e.g. F W) - Stuns enemies")
    print("T         - Drop Trap (Step off to arm)")
    print("E         - Interact (Read terminal, buy from shop)")
    print("X         - Quit game")
    input("\nPress Enter for next page > ")

    os.system('cls' if os.name == 'nt' else 'clear')
    print("SURVIVAL MANUAL (PAGE 2/2)")
    print("-" * 40)
    print("THREATS:")
    print("GHOSTS (G) - Roam the forest. Avoid their paths.")
    print("HUNTER (H) - Actively tracks you. Can cut you off.")
    print("\nOBJECTIVES:")
    print("1. Collect debris coins (*) to buy supplies at the shop ($).")
    print("2. Find the exit (>) to reach your crashed ship.")
    print("3. Repair both Engine Rooms [E] inside the ship.")
    print("4. Access the Reactor [R] to trigger the final sequence.")
    input("\nPress Enter to close > ")


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
    print("G = Ghost | H = Hunter | g/h = stunned")
    print("WASD move | T trap | E shop | X exit")
    if msg:
        for line in textwrap.wrap(msg, width=78) or [""]:
            print(line)


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


def alien_turn(protected=False):
    """Return a warning if a creature is nearby, or a game-over string if caught."""
    global turn
    turn += 1
    warnings = []
    player = (s["px"], s["py"])
    # Give the player eight actions before the creatures begin moving.
    if turn <= 8:
        if turn == 8:
            return "You hear something moving in the darkness..."
        return ""

    # Sprint threshold increased so they don't rubberband to the player instantly
    sprint_distance = 8

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
        distance_to_goal = shortest_distance(here, goal)
        steps = 2 if distance_to_goal > sprint_distance else 1

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
draw("Escape.")

clear_first_level=False
while True:
    target_x = s["px"]
    target_y = s["py"]
    valid_move = False
    action_taken = False
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
                action_taken = True
                msg = "Trap placed. Step off to arm it."
        else:
            msg = "No traps left. you're cooked."

    elif move == "E":
        if near_tile("?"):
            open_terminal()
            msg = "Manual closed."
        elif near_tile("$"):
            enter_shop()
            msg = "Left the shop."
        else:
            msg = "Get closer to the shop ($) or terminal (?) first."
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
    else:
        draw("Invalid input")
        continue

    if valid_move:
        if not open_tile(target_x, target_y):
            msg = "That's a wall genius. Try the other way."
        elif s["grid"][target_y][target_x] == ">":
            clear_first_level = True
            draw("You made it out of the dark woods.")
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
    print("FW/FA/FS/FD flash | C panel | < return | G/H creatures | g/h stunned")

    if msg:
        for paragraph in msg.splitlines():
            lines = textwrap.wrap(paragraph, width=78)
            print(*(lines or [""]), sep="\n")


def change_room(new_room, x, y):
    global room

    room = new_room
    s["grid"] = maps[room]
    s["px"] = x
    s["py"] = y



def use_panel():
    global stage, enemies_active, level_2_clear, enemy_delay

    if room in ("engine_1", "engine_2"):
        if not near_tile("C"):
            return "Move closer to the control panel."

        if engine_fixed[room]:
            return "This engine is already repaired."

        engine_fixed[room] = True
        if room == "engine_1":
            s["flashlight_disabled"] = True

        if all(engine_fixed.values()):
            stage = "escape"
            enemies_active = True
            enemy_delay = 6

            return (
                "Engine 2 starts with a deafening roar, then the ship shudders.\n"
                "A churning explosion tears through the engine room.\n"
                "Something climbs aboard the ship.\n"
                "The Ghost and Hunter are here!\n"
                "Go to the Reactor at [R]."
            )

        if room == "engine_1":
            return "Engine 1 repaired. The ship lights are restored; your flashlight is no longer needed."

        return "Engine repaired. Find the other engine room."


    if room == "ship":
        if not near_tile(">"):
            return "There is nothing to use here."

        if stage == "repair":
            return "No power. Repair both engines first."

        stage = "reactor"

        return (
            "The engines are running, but the ship cannot move.\n"
            "The hull is damaged..\n"
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
    s["aliens"] = [[50, 6], [40, 8]]

    alien_names = ["GHOST", "HUNTER"]
    alien_stunned = [0, 0]
    turn = 0

    maps["ship"][9][20] = "."

    draw_level_2(
        "You make it back to your ship.\n"
        "The forest falls silent behind you as you reach the hull."
    )
    input("\nPress Enter to board your ship > ")
    draw_level_2(
        "Inside, the ship is dark and powerless.\n"
        "The engines are damaged, but the ship is still reparable.\n"
        "Repair both engines and get the ship moving again."
    )
    input("\nPress Enter to begin repairs > ")

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
                    if not s["flashlight_disabled"]:
                        s["flash"] -= 1
                action_taken = True


        elif move == "E":
            msg = use_panel()
            action_taken = True

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
