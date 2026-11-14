import os
from turn_input import PASTED_MOVE
from cinematics import secret_ending
from ui import print_map, print_dialogue, terminal_ready, panel_answer, read_map_turn
from menus import enter_shop, open_terminal, show_forest_briefing, confirm_forest_exit
from alien_logic import alien_turn
from state import s, alien_names, alien_stunned, shop_positions, open_tile, near_tile

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

def run_forest_level():
    for y in range(len(s["grid"])):
        for x in range(len(s["grid"][y])):
            if s["grid"][y][x] == "@":
                s["py"] = y
                s["px"] = x

    s["aliens"] = [[30, 8], [28, 2]]
    show_forest_briefing()
    draw("Move with WASD. Stand next to ? and press E for more help.")

    while True:
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
                dy -= 1
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
                    check_x = s["px"] + dx * step
                    check_y = s["py"] + dy * step
                    if not open_tile(check_x, check_y):
                        break
                    for i, alien_pos in enumerate(s["aliens"]):
                        if alien_pos == [check_x, check_y]:
                            alien_stunned[i] = 5
                            msg += f" Stunned {alien_names[i]} for 5 turns!"

        elif move == "X":
            return False
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
                    draw("You escaped the forest and reached your ship.")
                    return True
                else:
                    secret_ending()
                    panel_answer(["Secret ending development in progress.", "",
                                  "To restart, run this Python file again."],
                                 "Press Enter to exit > ", 0)
                    return False
            else:
                if any((target_x, target_y) == tuple(g) and alien_stunned[i] == 0
                       for i, g in enumerate(s["aliens"])):
                    draw("You walked straight into a creature. Game over.")
                    return False

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
            return False
        if action_taken:
            danger = alien_turn(protected=trap_placed)
            if danger == "A creature caught you. Game Over!":
                draw(danger)
                return False
            if danger:
                msg = (msg + " " + danger).strip()
        draw(msg)