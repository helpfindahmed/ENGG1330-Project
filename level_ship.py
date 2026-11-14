import os
import alien_logic
from engine_puzzles import IGNITION_SLOT, PANEL_HINTS, panel_lines, solves_panel
from turn_input import PASTED_MOVE
from cinematics import explosion_animation, reactor_repair_animation
from map_data import ship_map, engine_1_map, engine_2_map, reactor_map
from ui import print_map, print_dialogue, terminal_ready, panel_answer, read_map_turn
from menus import open_terminal
from alien_logic import alien_turn
from state import s, alien_names, alien_stunned, open_tile, near_tile

maps = {}
room = "ship"
stage = "repair"
engine_fixed = {"engine_1": False, "engine_2": False}
engine_attempts = {"engine_1": 0, "engine_2": 0}
enemies_active = False
level_2_clear = False

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
    print_dialogue(msg, max_lines=min(4, 21 - len(display)))

def change_room(new_room, x, y):
    global room
    room = new_room
    s["grid"] = maps[room]
    s["px"] = x
    s["py"] = y

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

def run_ship_level():
    global maps, room, stage, engine_fixed, engine_attempts, enemies_active, level_2_clear
    maps = {
        "ship": [list(row) for row in ship_map],
        "engine_1": [list(row) for row in engine_1_map],
        "engine_2": [list(row) for row in engine_2_map],
        "reactor": [list(row) for row in reactor_map],
    }

    room = "ship"
    stage = "repair"
    engine_fixed = {"engine_1": False, "engine_2": False}
    engine_attempts = dict.fromkeys(engine_fixed, 0)
    enemies_active = False
    level_2_clear = False
    return_position = (55, 9)

    s["grid"] = maps["ship"]
    s["px"] = 55
    s["py"] = 9
    s["tl"] = []
    s["aliens"] = [[50, 6], [40, 8]]

    alien_stunned[0] = 0
    alien_stunned[1] = 0
    alien_logic.turn = 0

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
                        if enemy == [target_x, target_y] and alien_stunned[i] == 0:
                            caught = True

                if caught:
                    draw_level_2("You walked straight into a creature. Game Over.")
                    break

                if room == "ship":
                    for trap in s["tl"]:
                        if trap["tx"] == s["px"] and trap["ty"] == s["py"]:
                            trap["triggered"] = True

                if room == "ship" and tile == "E":
                    return_position = (s["px"], s["py"])
                    if target_y == 0:
                        change_room("engine_1", 14, 10)
                    else:
                        change_room("engine_2", 14, 1)
                    changed_map = True
                    msg = ("You entered the upper engine room." if target_y == 0
                           else "You entered the lower engine room.")

                elif room == "ship" and tile == "R":
                    return_position = (s["px"], s["py"])
                    change_room("reactor", 27, 9)
                    changed_map = True
                    msg = "You entered the reactor room."

                elif room != "ship" and tile == "<":
                    change_room("ship", return_position[0], return_position[1])
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
            elif any(trap["tx"] == s["px"] and trap["ty"] == s["py"] for trap in s["tl"]):
                msg = "There is already a trap here."
            else:
                s["traps"] -= 1
                s["tl"].append({"tx": s["px"], "ty": s["py"], "triggered": False})
                trap_placed = True
                action_taken = True
                msg = "Trap placed. Step off to arm it."

        elif move in ("FW", "FA", "FS", "FD"):
            if room != "ship":
                msg = "There are no enemies in this room."
            elif s["bangs"] < 1:
                msg = "Out of Big Bangs!"
            else:
                directions = {"W": (0, -1), "A": (-1, 0), "S": (0, 1), "D": (1, 0)}
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

        if action_taken and room == "ship" and enemies_active and not changed_map:
            danger = alien_turn(protected=trap_placed, aggressive=True)
            if danger == "A creature caught you. Game Over!":
                draw_level_2("A creature caught you. Game Over!")
                break
            if danger:
                msg = (msg + "\n" + danger).strip()

        if s["flash"] <= 0 and not s["flashlight_disabled"]:
            draw_level_2("Your flashlight died. The creatures take you in the dark. GAME OVER.")
            break

        draw_level_2(msg)