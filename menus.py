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
        "A ENGG1330 Project",
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

        choice = panel_answer(display_lines, "Select an option > ").upper()
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
    s["help_unlocked"] = True
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
        choice = panel_answer(lines, "Choose 1 or 2, then press Enter > ")
        if choice in ("1", "2"):
            return choice == "1"
        feedback = "Invalid choice. Enter 1 or 2."


