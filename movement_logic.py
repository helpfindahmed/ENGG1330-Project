import os
import textwrap
import sys
import time

# Stage 4: presentation only; no gameplay state is changed here.
def intro_terminal_size():
    try:
        return os.get_terminal_size(sys.stdout.fileno())
    except (OSError, ValueError):
        return (80, 24)  # Redirected output has no terminal to resize.


def intro_draw(lines, prompt, size):
    """Draw a bounded frame without newlines or the terminal's last column."""
    width, height = size
    ready = width >= 80 and height >= 24
    if ready:
        rows = [(3 + i, 3, line) for i, line in enumerate(lines)]
        rows.append((22, 3, prompt))
    else:
        # Even a one-row terminal must not scroll. Extremely narrow terminals
        # show the beginning of the message until there is room for all of it.
        message = textwrap.wrap("Resize to 80 x 24 to continue.",
                                width=max(1, width - 1))
        rows = [(i + 1, 1, line) for i, line in enumerate(message[:height])]
    sys.stdout.write("\033[2J\033[H")
    for row, column, line in rows:
        if row <= height: 
            sys.stdout.write(f"\033[{row};{column}H" +
                             line[:max(0, width - column)])
                             
    sys.stdout.flush()
    return ready


def _intro_key(interactive, ready, size):
    if interactive:
        if os.name == "nt":
            import msvcrt
            if msvcrt.kbhit():
                character = msvcrt.getwch()
                if character in ("\x00", "\xe0"):
                    msvcrt.getwch()
                    return ""
                return character
            time.sleep(0.02)
        else:
            import select
            if select.select([sys.stdin], [], [], 0.02)[0]:
                key = os.read(sys.stdin.fileno(), 1)
                return key.decode("utf-8", errors="ignore")
    elif ready:
        key = sys.stdin.read(1)
        if not key:
            raise EOFError
        return key
    else:
        time.sleep(0.02)
    return ""


def intro_frame(text):
    """Reveal one text frame, then wait for Enter or Backspace."""
    lines = []
    for paragraph in text.split("\n"):
        lines.extend(textwrap.wrap(paragraph, width=72) or [""])
    if len(lines) > 18:
        raise ValueError("Introduction frame exceeds its 18-line text area")
    prompt = "Enter to continue | Backspace to go back | Ctrl+C to quit"
    interactive = sys.stdin.isatty()
    previous_size = None
    previous_visible = -1
    visible = 0
    total = sum(len(line) for line in lines)
    while True:
        size = intro_terminal_size()
        ready = size[0] >= 80 and size[1] >= 24
        if size != previous_size or visible != previous_visible:
            shown = []
            remaining = visible
            for line in lines:
                shown.append(line[:remaining])
                remaining = max(0, remaining - len(line))
            intro_draw(shown, prompt, size)
            previous_size = size
            previous_visible = visible
        key = _intro_key(interactive, ready, size)
        if key in ("\x03", "\x04"):
            raise KeyboardInterrupt
        if not ready:
            continue
        if key in ("\x08", "\x7f"):
            return "back"
        if visible < total:
            visible += 1
            continue
        if key in ("\n", "\r"):
            return "next"



def intro_story():
    frames = [
        "You are a spacecraft systems engineer. Your work takes you between "
        "remote colonies, orbital stations and mining sites that describe "
        "their maintenance problems as 'probably nothing.'\n\n"
        "You fix what someone else breaks, collect your payment and leave. "
        "Nobody has asked you to save the universe. Your rates do not cover it :(",
        "Your next job is a regulator replacement at a distant mining colony. "
        "The route is plotted and the engines are steady.\n\n"
        "Then your cup slides across the console.\n\n"
        "[NAVIGATION] UNREQUESTED COURSE CORRECTION\n\n"
        "A second set of coordinates appears with no source identifier. "
        "You reject it. The ship turns again.",
        "[AUTOPILOT] CONFLICTING POSITION DATA\n"
        "[AUTOPILOT] TRAJECTORY CORRECTION FAILED\n\n"
        "You take manual control, but the controls go slack. A planet swells "
        "across the space where your route should be.\n\n"
        "[WARNING] GRAVITATIONAL CAPTURE\n\n"
        "Below the cloud cover, forest fills the horizon.",
        "[DESCENT] THRUST INSUFFICIENT\n\n"
        "                 .---->\n"
        "              .-'\n\n"
        "       /\\       /\\   /\\       /\\\n"
        "      /  \\ /\\ /  \\ /  \\ /\\ /  \\",
        "[CRITICAL] EMERGENCY LANDING FAILED\n\n"
        "                    \\ | /\n"
        "                 --- * ---\n"
        "                    / | \\\n"
        "       /\\       /\\   /\\   /\\",
        "You wake against the restraint straps. Both engines are offline.\n\n"
        "[DIAGNOSTICS] THRUST REGULATOR DISCONNECTED\n"
        "[DIAGNOSTICS] TAKEOFF UNAVAILABLE WITHOUT REGULATOR\n"
        "[RADAR] POSSIBLE COMPONENT BEACON DETECTED\n\n"
        "You take your equipment and follow the signal into the forest.",
        "The beacon fades at the bottom of a slope. You turn to check your "
        "way back, but the track crosses itself and stops.\n\n"
        "A dry knock carries through the trees. The ship's marker sits at the "
        "edge of the display, much farther away than you meant to go.",
        "[DATABASE] PLANETARY IDENTIFICATION COMPLETE\n"
        "[WARNING] EXTREME THREAT CLASSIFICATION\n\n"
        "[PLANETARY RECORD] SURVEY WORLD K-17\n"
        "[ACTIVITY] INCREASES TOWARD LOCAL NIGHTFALL\n\n"
        "There is no safe route in the record. You are inside one of the "
        "most dangerous habitats in the known universe.",
        "The remaining strips of sky are losing their colour. You hear the "
        "knock again, from a different direction.\n\n"
        "You turn back. Repairs can wait until you have a hull between you "
        "and the forest.\n\n"
        "Find the way back to your ship (>). Stay clear of anything moving.",
        "You might be wondering why you had to read all that instead of playing it.\n\n"
        "...\n\n"
        "Goodluck.",
    ]
    index = 0
    while index < len(frames):
        result = intro_frame(frames[index])
        if result == "back":
            index = max(0, index - 1)
        else:
            index += 1


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


def read_turn(prompt="Move [WASD | F + direction | E | T | H | X] > "):
    if not sys.stdin.isatty() or os.name != "posix":
        return input("Enter your move: ").strip().upper()

    import select
    import termios
    import tty

    fd = sys.stdin.fileno()
    original = termios.tcgetattr(fd)

    def read_key():
        key = os.read(fd, 1)
        if key != b"\x1b":
            return key.decode("ascii", errors="replace").upper()

        # Consume terminal escape sequences so an arrow's final letter
        # cannot become a movement command.
        if select.select([fd], [], [], 0.03)[0]:
            prefix = os.read(fd, 1)
            if prefix in (b"[", b"O"):
                while select.select([fd], [], [], 0.03)[0]:
                    part = os.read(fd, 1)
                    if not part or b"@" <= part <= b"~":
                        break
        return "\x1b"

    try:
        tty.setcbreak(fd, termios.TCSANOW)
        while True:
            print("\r\033[2K" + prompt, end="", flush=True)
            key = read_key()
            if key in ("", "\x04", "X"):
                print("", end="", flush=True)
                return "X"
            if key in ("\r", "\n", "\x1b"):
                print("", end="", flush=True)
                continue
            if key != "F":
                print(key, end="", flush=True)
                return key

            print("F", end="", flush=True)
            print("\r\033[2K" + "Aim [WASD, Esc to cancel] > ", end="", flush=True)
            direction = read_key()
            print("", end="", flush=True)
            if direction in ("", "\x04", "X"):
                return "X"
            if direction in ("W", "A", "S", "D"):
                return "F" + direction
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, original)


def panel_answer(lines, prompt="Setting > ", max_length=16):
    """Bound puzzle input to one screen, including invalid or pasted input."""
    saved = None
    answer = ""
    previous = None
    try:
        if sys.stdin.isatty() and os.name == "posix":
            import termios
            saved = termios.tcgetattr(sys.stdin.fileno())
            settings = termios.tcgetattr(sys.stdin.fileno())
            settings[3] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON)
            settings[6][termios.VMIN] = 1
            settings[6][termios.VTIME] = 0
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, settings)
        while True:
            size = intro_terminal_size()
            ready = size[0] >= 80 and size[1] >= 24
            if (size, answer) != previous:
                intro_draw(lines, prompt + answer, size)
                previous = (size, answer)
            key = _intro_key(sys.stdin.isatty(), ready, size)
            if key in ("\x03", "\x04"):
                raise KeyboardInterrupt
            if not ready or intro_terminal_size() != size:
                continue
            if key in ("\n", "\r"):
                return answer.strip()
            if key in ("\x08", "\x7f"):
                answer = answer[:-1]
            elif key and len(key) == 1 and " " <= key <= "~" and len(answer) < max_length:
                answer += key
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)
    finally:
        if saved is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, saved)


def debug_menu():
    print("DEBUG MENU")
    print("Press Enter for the full game.")
    print("Type 'forest' to start at the forest.")
    print("Type 'ship' to start at the ship.")
    while True:
        command = input("> ").strip().lower()
        if command in ("", "forest", "ship"):
            return command or "full"
        print("Unknown command. Use forest, ship, or press Enter.")


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
help_unlocked = False


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
    global help_unlocked
    help_unlocked = True
    os.system('cls' if os.name == 'nt' else 'clear')
    print("SURVIVAL MANUAL (PAGE 1/2)")
    print("-" * 40)
    print("MISSION LOG:")
    print("You are a space engineer. Your ship crashed in a")
    print("dark, uncharted forest. The radar shows ship parts")
    print("scattered nearby. You need to fix the ship to survive.")
    print("\nCONTROLS:")
    print("W A S D   - Move one tile per keypress (Costs battery)")
    print("F then WASD - Aim a flash attack to stun enemies")
    print("T         - Drop Trap (Step off to arm)")
    print("E         - Interact (Read terminal, buy from shop)")
    print("H         - Reopen this help menu")
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
    print("3. Repair the upper engine, then the lower engine.")
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


def terminal_ready():
    try:
        width, height = os.get_terminal_size(sys.stdout.fileno())
    except (OSError, ValueError):
        width, height = 80, 24
    if width < 80 or height < 24:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Resize terminal to 80x24 or above to continue.")
        return False
    return True


def print_dialogue(msg, width=78, max_lines=4):
    if not msg:
        return
    print()
    lines = []
    for paragraph in msg.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=width) or [""])
    for line in lines[:max_lines]:
        print(line)


def draw(msg=""):
    if not terminal_ready():
        return
    os.system('cls' if os.name == 'nt' else 'clear')
    display = [row[:] for row in s["grid"]]
    for i, (x, y) in enumerate(s["aliens"]):
        if (x, y) != (s["px"], s["py"]):
            symbol = "G" if i == 0 else "H"
            if alien_stunned[i] > 0:
                symbol = symbol.lower()  # stunned aliens == g.
            display[y][x] = symbol
    print("LEVEL 1 - FOREST | OBJECTIVE: RETURN TO SHIP (>)")
    panel = [
        f"Flash: {s['flash']}%",
        f"Coins: {s['coins']}",
        f"Charges: {s['bangs']}",
        f"Traps: {s['traps']}",
        "",
        "X quit",
    ]
    for index, row in enumerate(display):
        side = panel[index] if index < len(panel) else ""
        print(f"{''.join(row):<60} {side:<19}")
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

    sprint_distance = 12 if aggressive else 8

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
        steps = 2 if aggressive or distance_to_goal > sprint_distance else 1

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
debug_mode = debug_menu()
if debug_mode == "full":
    play_introduction()
elif debug_mode == "forest":
    print("Starting forest debug sequence...")
    time.sleep(0.5)

if debug_mode != "ship":
    draw("Escape.")

clear_first_level = debug_mode == "ship"
while debug_mode != "ship":
    target_x = s["px"]
    target_y = s["py"]
    valid_move = False
    action_taken = False
    trap_placed = False
    msg = ""
    move = read_turn()

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
            if (
                0 <= target_y < len(s["grid"])
                and 0 <= target_x < len(s["grid"][target_y])
                and s["grid"][target_y][target_x] == "?"
            ):
                msg = "The terminal blocks the path. Stand beside it and press E."
            else:
                msg = "Dense undergrowth blocks that path."
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
    "  ##.........######...........######.........####",
    " #...........######...........######.............###",
    "#...................................................##",
    "#.......####.............................####.........##",
    "#.......####........#######..............####..........#",
    "#...................#######.............................#",
    "#.......####.............................####............#",
    "[R].....####........@....................####..........>...#",
    "#.......####.............................####............#",
    "#...................#######.............................#",
    "#.......####........#######..............####..........#",
    "#.......####.............................####.........##",
    "#...................................................##",
    "  ##.........######...........######.........######",
    "    ####.....######...........######...######",
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


def at_engine_panel():
    return s["grid"][s["py"]][s["px"]] == "C" or near_tile("C")


def draw_level_2(msg=""):
    if not terminal_ready():
        return
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

    room_names = {
        "ship": "MAIN DECK",
        "engine_1": "UPPER ENGINE ROOM",
        "engine_2": "LOWER ENGINE ROOM",
        "reactor": "REACTOR ROOM",
    }
    upper = "ON" if engine_fixed["engine_1"] else "OFF"
    lower = "ON" if engine_fixed["engine_2"] else "OFF"
    if stage == "repair":
        objective = "Repair Lower" if engine_fixed["engine_1"] else "Repair Upper"
    elif stage == "escape":
        objective = "Check controls >"
    else:
        objective = "Activate reactor"
    print(f"LEVEL 2 | {room_names[room]} | UPPER ENGINE:{upper} LOWER ENGINE:{lower} "
          f"({sum(engine_fixed.values())}/2) | {objective}")
    panel = [
        f"Flash: {s['flash']}%",
        f"Traps: {s['traps']}",
        f"Engines: {sum(engine_fixed.values())}/2",
        "",
        "X quit",
    ]
    for index, row in enumerate(display):
        side = panel[index] if index < len(panel) else ""
        print(f"{''.join(row):<60} {side:<19}")
    print_dialogue(msg)


def change_room(new_room, x, y):
    global room

    room = new_room
    s["grid"] = maps[room]
    s["px"] = x
    s["py"] = y



def use_panel():
    global stage, enemies_active, level_2_clear

    if room in engine_fixed:
        if not at_engine_panel():
            return "Walk to C or a tile beside it, then press E."

        if engine_fixed[room]:
            return "This engine is already repaired."

        if room == "engine_2" and not engine_fixed["engine_1"]:
            return "Repair the upper engine first to get its starter position."

        feedback = ""
        while True:
            lines = list(panel_lines(room))
            if feedback:
                lines += ["", feedback]
            answer = panel_answer(lines)
            if answer.upper() == "X":
                return "Panel closed."
            if solves_panel(room, answer):
                break
            feedback = "Incorrect setting. Check the clues and try again."

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
                "Engine 2 starts with a deafening roar, then the ship shudders.\n"
                "A churning explosion tears through the engine room.\n"
                "Something climbs aboard the ship.\n"
                "The Ghost and Hunter are here!\n"
                "Go to the Reactor at [R]."
            )

        return (
            "Upper engine repaired. The ship lights are back on.\n"
            f"Starter position {IGNITION_SLOT} unlocks the lower engine."
        )


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
        move = read_turn()
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
                    if engine_fixed[room]:
                        msg = "Engine repaired. Walk to < to return to the main deck."
                    elif room == "engine_2" and not engine_fixed["engine_1"]:
                        msg = "Lower engine locked. Return via < and repair the upper engine."
                    else:
                        msg = "Find C. Stand on it or next to it, then press E to repair."

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


        elif move == "H" and help_unlocked:
            open_terminal()
            draw_level_2("Help menu closed.")
            continue
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
