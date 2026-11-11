"""Clues and solution checks for the ship's linked engine puzzles."""

RELAY_ORDER = "231"
IGNITION_SLOT = RELAY_ORDER.index("3") + 1
FUEL_TOTAL = 9


def panel_lines(room):
    """Return the clues shown on an engine's repair screen."""
    if room == "engine_1":
        return (
            "UPPER ENGINE | CONNECT THE PARTS",
            "",
            "Connect all three parts in the correct order.",
            "1. Fuel pump",
            "2. Cooling system",
            "3. Starter",
            "",
            "The cooling system goes before the fuel pump.",
            "The fuel pump goes immediately after the starter.",
            "",
            "Enter the three part numbers in order, using each once.",
            "Press Enter to submit. X closes the panel.",
        )
    return (
        "LOWER ENGINE | BALANCE THE FUEL",
        "",
        "Set fuel valves A, B and C to whole numbers from 1 to 5.",
        "B needs one more unit than A.",
        f"C must match the upper engine's starter position ({IGNITION_SLOT}).",
        f"The three valves must total {FUEL_TOTAL} units.",
        "",
        "Enter the three numbers in A B C order. X closes the panel.",
    )


def solves_panel(room, answer):
    """Check a relay order or a set of fuel valve settings."""
    compact = "".join(answer.upper().split())
    if room == "engine_1":
        return compact == RELAY_ORDER
    if len(compact) != 3 or any(digit not in "12345" for digit in compact):
        return False

    valve_a, valve_b, valve_c = map(int, compact)
    return (
        valve_b == valve_a + 1
        and valve_c == IGNITION_SLOT
        and valve_a + valve_b + valve_c == FUEL_TOTAL
    )
