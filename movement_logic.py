import os
import textwrap
import sys
import time

from engine_puzzles import IGNITION_SLOT, PANEL_HINTS, panel_lines, solves_panel
from turn_input import read_turn

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


def intro_frame(text, reveal=True):
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
    if not reveal:
        visible = total
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



def intro_timed_frame(lines, seconds):
    """Show an animation frame without reflowing ASCII or scrolling."""
    if len(lines) > 18 or any(len(line) > 72 for line in lines):
        raise ValueError("Introduction animation exceeds its text area")
    remaining = seconds
    previous_size = None
    while remaining > 0:
        size = intro_terminal_size()
        ready = size[0] >= 80 and size[1] >= 24
        if size != previous_size:
            intro_draw(lines, "", size)
            previous_size = size
        started = time.monotonic()
        if sys.stdin.isatty():
            key = _intro_key(True, ready, size)
            if key in ("\x03", "\x04"):
                raise KeyboardInterrupt
        else:
            time.sleep(0.02)
        if ready and intro_terminal_size() == size:
            remaining -= time.monotonic() - started


def intro_story():
    """Run the approved narrative, preserving Enter and Backspace navigation."""
    frames = [
        'You are a spacecraft systems engineer. You work for a maintenance contractor that services remote mining colonies, orbital stations, and anyone else willing to pay the call-out charge.\n\nThey send you between planets to repair failing equipment, usually several months after someone decided maintenance was too expensive. \nYou fix it, sign the paperwork, and leave before anything else breaks. \nYou don’t get paid enough for this, but you do get paid. That has kept you here for six years.\n\nToday’s assignment is a mining settlement on another planet. Its ore-processing plant keeps overheating. The replacement coolant regulator is already installed. From the photographs, you can see that someone fitted it backwards.\n\nYou pack a socket adapter and accept the job. Your supervisor has allowed two hours for the repair. Travel, apparently, is something you do in your spare time.',
        'Your ship leaves the transfer station on its assigned course. You secure your tools and check the approach instructions.\n\nHalfway through the journey, the steering thrusters fire.\n\n[NAVIGATION] COURSE CORRECTION APPLIED\n[FLIGHT PLAN] NO SCHEDULED MANOEUVRE\n\nYou bring up the route. Your destination is still listed, but the ship is steering toward a second set of coordinates.\n\nYou cancel the correction and reload the flight plan.\n\n[AUTOPILOT] POSITION SOURCES DISAPPROVED',
        'You disconnect the autopilot and take manual control.\n\nThe thrusters respond, but the position display still keeps jumping. You cannot tell which correction made things worse.\n\nA planet fills the forward window. There is no name beside it.\n\n[WARNING] ATMOSPHERIC ENTRY IMMINENT\n[ENGINES] DESCENT RATE EXCEEDS AVAILABLE THRUST\n\nYou turn the ship upside-down and spread the remaining thrust across the descent. The vibration makes the controls difficult to hold.\n\nBelow the clouds, an enormous forest reaches to the horizon. \nYou aim for a break in the canopy and deploy the landing gear.',
        'You wake with your weight hanging against the restraint straps.\n\nThe emergency lights are on. You release the harness, lower yourself to the tilted floor, and work through the damage report.\n\nBoth engines have shut down. The thrust regulator’s mounting has torn away, leaving an empty socket in the service bay.\n\n[DIAGNOSTICS] THRUST REGULATOR MISSING\n[TAKEOFF] UNAVAILABLE\n[RADAR] MATCHING MAINTENANCE BEACON DETECTED\n\nThe signal lies beyond the damaged trees ahead of the wreck. The regulator may have been thrown clear during the crash.\n\nYou could restore power without it but you cannot control enough thrust to lift the ship.',
        'OBJECTIVE: FIND THE THRUST REGULATOR IN THE FOREST\nAND BRING IT BACK TO REPAIR THE SHIP.\n\nYou mark the ship on your handheld, take your equipment, and follow the bearing.\n\nThe first stretch is easy. Broken branches show where the ship came through. Beyond them, smooth trunks rise into broad fans of leaves. Warm droplets fall from the canopy long after you pass beneath it.\n\nYou follow the navigation arrow on your handheld.',
        'Thick roots block the direct path. You walk around them and follow a shallow channel between the trees.\n\nThe ground is soft enough to leave footprints. You check behind you occasionally, making sure you can follow them back.\n\nFarther along, the regulator’s signal starts cutting out.\n\n[RADAR] CONTACT INTERMITTENT\n[ROUTE GUIDANCE] RECALCULATING\n\nYou climb out of the channel to recover the signal. When it returns, the navigation arrow points along the slope. You follow it.',
        'You cross the slope, work around a fallen trunk, and descend through another gap in the roots.\n\nThe channel below is dry. You walk along it looking for your footprints before accepting that it is a different channel.\n\nYou request a route back to the ship.\n\n[POSITION FIX] ACCURACY LOW\n[RETURN TRACK] INCOMPLETE\n\nThe recorded trail jumps across terrain you remember going around. You retrace your last few steps, but the fallen trunk is hidden behind several others.\n\nA branch knocks against something farther down the channel. You stop to listen. It does not happen again.\nYour ship’s marker is now well beyond the edge of the local map.',
        'For a moment, the ship link returns. A stored message arrives before you can request another position fix.\n\n[SHIP DATABASE] PLANETARY IDENTIFICATION COMPLETE\n[WORLD] K-17\n[THREAT CLASSIFICATION] EXTREME\n[EXPEDITION RECORDS] INCOMPLETE\n[FAUNA] EXCEPTIONALLY DANGEROUS SPECIES DOCUMENTED\n[ACTIVITY] INCREASES AFTER LOCAL NIGHTFALL\n[YOUR POSITION] WITHIN RECORDED HABITAT\n[RECOMMENDATION] RETURN TO SHELTER',
        'You open the attached survey. Most of its entries contain coordinates and missing reports. There is no marked safe route.\n\nThe database had flagged a possible match earlier. It only released the warning once it confirmed the planet.\n\nYou would have preferred a less reliable warning earlier.',
        'Above the canopy, the patches of sky are turning grey.\n\nThe regulator’s signal appears once more, then drops out. You put away the search bearing.\n\nThe ship is damaged, but its hatch still closes. Whatever repairs it needs, you need to reach it before nightfall.\n\nYou turn toward its last recorded position. A wall of roots blocks the direct route, and the handheld offers no useful way around it.\n\nYou will have to find your own path.\n\nYour immediate objective is to survive the forest and reach your crashed spacecraft. Find your way back to the ship (>).',
    ]
    crash_frames = [
        ['[LANDING GEAR] DEPLOYMENT INCOMPLETE', '', '  +------------------------------------------------------+', '  |                                                      |', '  |                         /\\                           |', '  |           /\\           /  \\        /\\                |', '  |     /\\   /  \\    /\\    /    \\      /  \\       /\\       |', '  |____/  \\_/    \\__/  \\__/      \\____/    \\_____/  \\______|', '  |                                                      |', '  +------------------------------------------------------+', '', '[DESCENT] PULL UP'],
        ['[WARNING] TERRAIN COLLISION', '', '   +------------------------------------------------------+', '   |       /       \\            /        \\                |', '   |      /         \\          /          \\      /        |', '   |_____/           \\________/            \\____/         |', '   |           ||                    ||              ||   |', '   |     ------||-----         ------||------        ||   |', '   |           ||                    ||              ||   |', '   +------------------------------------------------------+', '', '[ENGINES] EMERGENCY SHUTDOWN'],
        ['[CRITICAL] IMPACT DETECTED', '', '  +------------------------------------------------------+', '  |          \\                    /                      |', '  |           \\       |          /                       |', '  |------------\\------*---------/-------------------------|', '  |             \\   / | \\     /                          |', '  |              \\ /  |  \\___/                           |', '  |               /   |      \\                           |', '  +------------------------------------------------------+', '', '[FLIGHT RECORDER] SIGNAL L—'],
    ]
    index = 0
    while index < len(frames):
        if index == 3:
            for lines, delay in zip(crash_frames, (0.2, 0.2, 0.15)):
                intro_timed_frame(lines, delay)
            intro_timed_frame([], 0.45)
        if index == 7:
            lead, notices = frames[index].split("\n\n", 1)
            lines = textwrap.wrap(lead, width=72) + [""]
            intro_timed_frame(lines, 1.0)
            for notice in notices.splitlines():
                lines.append(notice)
                intro_timed_frame(lines, 0.8)
            result = intro_frame(frames[index], reveal=False)
        else:
            result = intro_frame(frames[index])
        if result == "back":
            index = max(0, index - 1)
        else:
            index += 1

    joke = textwrap.wrap(
        "You might be wondering why we narrated all of that instead "
        "of letting you play through it.", width=72)
    intro_timed_frame(joke, 2.0)
    intro_timed_frame(joke + ["", "…"], 1.0)
    intro_timed_frame(joke + ["", "…", "", "Goodluck."], 1.0)


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


def secret_ending():
    """A brief visual interruption, then a clean end with restart guidance."""
    saved = None
    try:
        if sys.stdin.isatty() and os.name == "posix":
            import termios
            saved = termios.tcgetattr(sys.stdin.fileno())
            settings = termios.tcgetattr(sys.stdin.fileno())
            settings[3] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON)
            settings[6][termios.VMIN] = 1
            settings[6][termios.VTIME] = 0
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, settings)
        sys.stdout.write("\033[?25l")
        intro_timed_frame(['   /\\    /\\       /\\', '  /##\\  /  \\  ## /  \\',
                           "  ||    ||   []    ||", "[DISPLAY] SYNC LOST"], 0.15)
        intro_timed_frame(["#  []  ##   --   []", "   ##       #  #", "[DI$PLAY] -- --"], 0.12)
        intro_timed_frame([], 0.7)
        intro_timed_frame(["YOU DIED."], 1.2)
        intro_timed_frame(["Just kidding."], 1.0)
        intro_timed_frame(["Secret ending development in progress."], 1.0)
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)
    finally:
        if saved is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, saved)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    panel_answer(["Secret ending development in progress.", "",
                  "To restart, run this Python file again."],
                 "Press Enter to exit > ", 0)


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
    "#...*..........#.........#####.......###.............#...#",
    "#...#####......########......#.......#.#.*...*.......#...#",
    "#...#.*.....*................#.......###...............>.#",
    "#..........#####......*......#...*............############",
    "#<..$...*..#...#......*..................................#",
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
    print()
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
        print(f"{''.join(row).replace('.', ' '):<60} {side:<19}")
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
        distance_to_player = shortest_distance(here, player)
        sprint_limit = 4 if i == 0 else 8
        steps = 2 if distance_to_player > sprint_limit else 1

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
    draw("Move beside ? and press E for help. Press H to reopen it afterward.")

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
        elif s["grid"][target_y][target_x] in (">", "<"):
            ship_exit = s["grid"][target_y][target_x] == ">"
            question = ("Make a run towards the ship?" if ship_exit
                        else "Go deeper into the forest?")
            if not confirm_forest_exit(question):
                draw("You stay in the forest.")
                continue
            if ship_exit:
                clear_first_level = True
                draw("You made it out of the dark woods.")
            else:
                secret_ending()
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
    print(f"L2 | {room_names[room]} | U:{upper} L:{lower} "
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
        print(f"{''.join(row).replace('.', ' '):<60} {side}".rstrip())
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

        hints = PANEL_HINTS[room]
        while True:
            lines = list(panel_lines(room))
            if engine_attempts[room]:
                hint_number = min(engine_attempts[room], len(hints))
                lines.extend((
                    "",
                    "Incorrect setting. Check the clues and try again.",
                    f"Hint {hint_number}/{len(hints)}: {hints[hint_number - 1]}",
                ))
            answer = panel_answer(lines)
            if answer.upper() == "X":
                return "Panel closed."
            if solves_panel(room, answer):
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
    engine_attempts = dict.fromkeys(engine_fixed, 0)

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
    input("Press Enter to board your ship > ")
    draw_level_2(
        "Inside, the ship is dark and powerless.\n"
        "The engines are damaged, but the ship is still reparable.\n"
        "Repair both engines and get the ship moving again."
    )
    input("Press Enter to begin repairs > ")

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
