# Pull the main game state dictionary so the shop can deduct coins and add items
from state import s

# Pull the rendering tools the menus need to display text
from ui import panel_answer, player_icon


def main_menu():
    # Feeding it as a direct list avoids all Python indentation spacing issues
    lines = [
        r"  ____  _        _    ____ _  _____  _   _ _____ ",
        r" | __ )| |      / \  / ___| |/ / _ \| | | |_   _|",
        r" |  _ \| |     / _ \| |   | ' / | | | | | | | |  ",
        r" | |_) | |___ / ___ \ |___| . \ |_| | |_| | | |  ",
        r" |____/|_____/_/   \_\____|_|\_\___/ \___/  |_|  ",
        "",
        "An ENGG1330 Project",
        "",
        "[1] New Game",
        "[2] Survival Manual",
        "[3] Debug Mode",
        "[X] Quit"
    ]

    feedback = ""
    while True:
        display_lines = lines[:]
        if feedback:
            display_lines.extend(["", feedback])

        choice = panel_answer(display_lines, "Press 1, 2, 3, or X > ", single_key=True).upper()
        if choice in ("1", "2", "3", "X"):
            return choice
        feedback = "Invalid choice. Enter 1, 2, 3, or X."

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
            "Press 1, 2, or 3 to buy, or X to leave.",
        ]
        if feedback:
            lines.extend(("", feedback))
        choice = panel_answer(lines, "Press 1, 2, 3, or X > ", single_key=True).upper()
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
    s["help_unlocked"] = True
    panel_answer([
        "SURVIVAL MANUAL (PAGE 1/2)",
        "Move and choose menu options with a single key.",
        "Use Enter to turn pages or submit a typed answer.",
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
        "FOREST MAP",
        f"{player_icon()} You  # Wall  Blank space = walkable floor",
        "? Help terminal: stand beside it and press E. H reopens this manual.",
        "$ Shop: stand beside it and press E. Each * gives 10 coins.",
        "> Ship exit  < Secret exit  X Armed trap",
        "G Ghost cuts you off. H Hunter chases you. g/h are stunned.",
        "",
        "1. Collect 40 coins and buy +50 battery at a shop before boarding.",
        "2. Enter > on the right. Your remaining battery carries aboard.",
        "3. Repair the upper engine [1], then the lower engine [2].",
        "4. Reach the reactor room [R] on the left side of the deck.",
    ], "Press Enter to close > ", 0)

def show_forest_briefing():
    panel_answer([
        "LEVEL 1 - SURVIVE THE FOREST",
        "",
        f"You are {player_icon()}, near the top-left corner.",
        "Buy battery before boarding your ship at > on the right.",
        "",
        "Collect four * tiles (10 coins each). Stand beside $ and press E.",
        "There is a shop in the lower-left. Press 1 to buy +50 battery.",
        "Your battery carries aboard and drains until the first repair.",
        "",
        "WASD moves one tile. # is a wall; blank spaces are floor.",
        "? is the yellow help terminal: stand beside it and press E.",
        "H reopens the manual. < is an optional exit.",
        "The creatures stay still for the first 15 turns."
        "",
        "Press T to drop a trap. Move off it to arm it.",
        "Press F, then a direction key, to fire a flash.",
        "Press X to quit.",
    ], "Press Enter to enter the forest > ", 0)

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

def confirm_forest_exit(question):
    """A confirmation never spends resources or advances the combat clock."""
    feedback = ""
    while True:
        lines = [question, "", "[1] Yes", "[2] No"]
        if feedback:
            lines += ["", feedback]
        choice = panel_answer(lines, "Press 1 or 2 > ", single_key=True)
        if choice in ("1", "2"):
            return choice == "1"
        feedback = "Invalid choice. Enter 1 or 2."


