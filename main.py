import os
import textwrap
import sys
import time

from engine_puzzles import IGNITION_SLOT, PANEL_HINTS, panel_lines, solves_panel
from turn_input import PASTED_MOVE, read_turn
from cinematics import intro_story, explosion_animation, reactor_repair_animation, intro_terminal_size, intro_draw, _intro_key, intro_timed_frame, secret_ending
from map_data import ship_map, raw_map, engine_1_map, engine_2_map, reactor_map
from ui import print_map, print_dialogue, terminal_ready, player_icon, panel_answer
from alien_logic import route, ghost_goal, hunter_goal, alien_turn
from menus import enter_shop, open_terminal, show_forest_briefing, debug_menu, main_menu
from state import s, alien_names, alien_stunned, shop_positions, open_tile, neighbors, shortest_distance, trap_at


def play_introduction():
    """Temporarily suppress input echo; always restore it before gameplay."""
    saved_input = None
    try:
        if sys.stdin.isatty() and os.name != "nt":
            import termios
            saved_input = termios.tcgetattr(sys.stdin.fileno())
            settings = termios.tcgetattr(sys.stdin.fileno())
            settings[3] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON)
            settings[6][termios.VMIN] = 1
            settings[6][termios.VTIME] = 0
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, settings)
        sys.stdout.write("\033[?25l")
        intro_story()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)
    finally:
        if saved_input is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, saved_input)
        sys.stdout.write("\033[?25h\033[H")
        sys.stdout.flush()


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

def read_map_turn(redraw):
    while True:
        if terminal_ready():
            move = read_turn()
            if move == "X" or terminal_ready():
                return move
        panel_answer(["Terminal resized. Press Enter to resume."], "Continue > ", 0)
        redraw()

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
while True:
    start_choice = main_menu()
    if start_choice == "X":
        sys.exit()
    elif start_choice == "2":
        open_terminal()
        continue
    elif start_choice == "3":
        debug_mode = debug_menu()
        break
    else:
        # Choice 1: New Game
        debug_mode = "full"
        break

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

    elif move == "H" and s["help_unlocked"]:
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
                panel_answer(["Secret ending development in progress.", "",
                              "To restart, run this Python file again."],
                             "Press Enter to exit > ", 0)
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

def reactor_decision():
    """Checkpoint: retries stay here without consuming a combat turn."""
    attempts = 0
    feedback = ""
    while True:
        lines = ["[WARNING] REACTOR UNSTABLE", "",
                 "Coolant control has failed. Core temperature is rising.",
                 "", "[1] Attempt to repair the reactor", "[2] Do nothing"]
        if feedback:
            lines += ["", feedback]
        choice = panel_answer(lines, "Choose 1 or 2, then press Enter > ")
        if choice == "2":
            return
        if choice != "1":
            feedback = "Invalid choice. Enter 1 or 2."
            continue
        attempts += 1
        reactor_repair_animation()
        lines = ["YOU DIED.", ""]
        if attempts >= 2:
            lines += ["You don't learn, do you?", ""]
        lines += ["CHECKPOINT: REACTOR CONTROL PANEL",
                  "Both engines remain repaired."]
        panel_answer(lines, "Press Enter to return to the decision > ", 0)
        feedback = ""

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
    return_position = (55, 9)

    s["grid"] = maps["ship"]
    s["px"] = 55
    s["py"] = 9

    s["tl"] = []
    s["aliens"] = [[50, 6], [40, 8]]

    alien_names = ["GHOST", "HUNTER"]
    alien_stunned[0] = 0
    alien_stunned[1] = 0
    s["turn"] = 0

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


        elif move == "H" and s["help_unlocked"]:
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
            panel_answer(["THE END.", "", "You died in the reactor explosion.",
                          "The Ghost and Hunter were destroyed aboard the ship.",
                          "Much of the surrounding forest is gone.", "",
                          "To restart, run this Python file again."],
                         "Press Enter to exit > ", 0)
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
