"""Clues and solution checks for the ship's linked engine puzzles."""

RELAY_ORDER = "CIP"
IGNITION_SLOT = RELAY_ORDER.index("I") + 1
FUEL_TOTAL = 9


def panel_lines(room):
    """Return the clues shown on an engine's repair screen."""
    if room == "engine_1":
        return (
            "ENGINE 1 | ROUTE THE POWER",
            "",
            "Put C (coolant), I (ignition) and P (pump) in order.",
            "Coolant comes before the pump.",
            "The pump comes immediately after ignition.",
            "",
            "Enter the three letters in order. X closes the panel.",
        )
    return (
        "ENGINE 2 | BALANCE THE FUEL",
        "",
        "Set fuel valves A, B and C to whole numbers from 1 to 5.",
        "B needs one more unit than A.",
        f"C must match Engine 1's ignition slot ({IGNITION_SLOT}).",
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
