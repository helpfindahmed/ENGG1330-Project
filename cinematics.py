import os
import sys
import time
import textwrap

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



def intro_terminal_size():
    try:
        return os.get_terminal_size(sys.stdout.fileno())
    except (OSError, ValueError):
        return (80, 24)

def intro_draw(lines, prompt, size):
    width, height = size
    ready = width >= 80 and height >= 24
    if ready:
        rows = [(3 + i, 3, line) for i, line in enumerate(lines)]
        rows.append((22, 3, prompt))
    else:
        message = textwrap.wrap("Resize to 80 x 24 to continue.", width=max(1, width - 1))
        rows = [(i + 1, 1, line) for i, line in enumerate(message[:height])]
    sys.stdout.write("\033[2J\033[H")
    for row, column, line in rows:
        if row <= height:
            sys.stdout.write(f"\033[{row};{column}H" + line[:max(0, width - column)])
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

def intro_steps(text):
    """Paginate whole paragraphs within the 72-column, 18-row text area."""
    pages = []
    lines = []
    for paragraph in text.split("\n\n"):
        if not paragraph.strip():
            continue
        wrapped = []
        for part in paragraph.splitlines():
            wrapped.extend(textwrap.wrap(part, width=72) or [""])
        if lines and len(lines) + 1 + len(wrapped) > 18:
            pages.append(lines)
            lines = []
        # A paragraph longer than a screen must continue on another page.
        while len(wrapped) > 18:
            pages.append(wrapped[:18])
            wrapped = wrapped[18:]
        if lines:
            lines.append("")
        lines.extend(wrapped)
    if lines:
        pages.append(lines)
    return pages or [[]]

def intro_frame(text, start=0):
    steps = intro_steps(text)
    index = len(steps) - 1 if start < 0 else min(start, len(steps) - 1)
    prompt = "Enter to continue | Backspace to go back | Ctrl+C to quit"
    interactive = sys.stdin.isatty() or (
        os.name == "nt" and sys.stdout.isatty()
    )
    previous = None
    while True:
        size = intro_terminal_size()
        ready = size[0] >= 80 and size[1] >= 24
        if (size, index) != previous:
            intro_draw(steps[index], prompt, size)
            previous = (size, index)
        key = _intro_key(interactive, ready, size)
        if key in ("\x03", "\x04"):
            raise KeyboardInterrupt
        if not ready or intro_terminal_size() != size:
            continue
        if key in ("\x08", "\x7f"):
            if index == 0:
                return "back"
            index -= 1
        elif key in ("\n", "\r"):
            if index == len(steps) - 1:
                return "next"
            index += 1

def intro_timed_frame(lines, seconds):
    if len(lines) > 18 or any(len(line) > 72 for line in lines):
        raise ValueError("Introduction animation exceeds its text area")
    remaining = seconds * 2.2
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

def play_reactor_frames(frames):
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
        for text, delay in frames:
            intro_timed_frame(text.splitlines(), delay)
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)
    finally:
        if saved is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, saved)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def intro_story():
    """narrative pages with Enter and Backspace navigation."""
    frames = [
        (
            'You are a spacecraft systems engineer.\n'
            '\n'
            'Six years ago, “travel between planets” on your resume sounded like a perk.\n'
            '\n'
            'Your employer has since done a lot to correct that impression.\n'
            '\n'
            'Today, a mining plant has stopped working. The site manager '
            'swears nobody touched anything.\n'
            '\n'
            'He has attached a photograph of a coolant regulator '
            'installed backwards.\n'
            '\n'
            'You could explain this over a call, but they requested '
            'an engineer. So now you have to go to another planet '
            'and turn something around.\n'
            '\n'
            'Two hours’ pay. Travel not included.\n'
            '\n'
            'You accept the job. Rent remains annoyingly non-negotiable.'
        ),
        (
            'You board the ship and prepare for the journey.\n'
            '\n'
            '[SYSTEMS] ALL SYSTEMS NOMINAL\n'
            '\n'
            '[NAVIGATION] UNSCHEDULED COURSE CORRECTION\n'
            '\n'
            '????\n'
            '\n'
            'You switch to manual control. The controls respond a second too '
            'late.\n'
            '\n'
            'The navigation display jumps from one star chart to the next.\n'
            '\n'
            'The route eventually disappears, replaced by an unidentified planet '
            'filling the window.\n'
            '\n'
            '[WARNING] ATMOSPHERIC ENTRY IMMINENT\n'
            '\n'
            'You fire the engines to slow your descent.\n'
            'Below you, there is nothing but forest.'
        ),
        (
            'You wake in the damaged cockpit and check the diagnostics.\n'
            '\n'
            '[ENGINES] OFFLINE\n'
            '[THRUST REGULATOR] MISSING\n'
            '[RADAR] COMPONENT SIGNAL DETECTED\n'
            '\n'
            'The regulator was thrown clear during the crash.\n'
            'Without it, the ship cannot take off.\n'
            '\n'
            'Its signal is coming from the forest. You mark the ship’s '
            'position, take your equipment, and follow the navigation arrow.'
        ),
        (
            'You follow the signal between enormous trees, walking around '
            'roots and fallen branches.\n'
            '\n'
            'Each detour takes you farther from the ship.\n'
            '\n'
            'The signal disappears.\n'
            '\n'
            '[ROUTE GUIDANCE] RECALCULATING\n'
            '\n'
            'You climb a slope to recover the signal. When you turn back, you cannot '
            'find the path you came from.\n'
            '\n'
            'You check your recorded route.\n'
            '\n'
            '[RETURN TRACK] INCOMPLETE\n'
            '\n'
            'You try retracing your steps, but nothing looks familiar.'
        ),
        (
            'Your handheld finally identifies the planet.\n'
            '\n'
            '[THREAT CLASSIFICATION] EXTREME\n'
            '[EXPEDITION RECORDS] INCOMPLETE\n'
            '[SPECIES] EXCEPTIONALLY DANGEROUS\n'
            '[ACTIVITY] INCREASES AFTER NIGHTFALL\n'
            '[YOUR POSITION] WITHIN THEIR TERRITORY\n'
            '\n'
            'The system waited until it was certain before warning you.\n'
            '\n'
            'You would have preferred a less reliable warning earlier.'
        ),
        (
            'It is getting dark. You hear something moving behind the trees.\n'
            '\n'
            'You stop looking for the regulator.\n'
            '\n'
            'You are lost in the forest.\n'
            '\n'
            'You need to get back to the ship.\n'
            '\n'
            'The navigation system cannot tell you how.\n'
            '\n'
            'OBJECTIVE: REACH > ON THE RIGHT TO RETURN TO YOUR SHIP.'
        ),
        (
            'You might be wondering why we narrated all of that instead of '
            'letting you play through it.\n'
            '\n'
            '…\n'
            '\n'
            'Goodluck.'
        ),
    ]
    crash_frames = [
        ['[LANDING GEAR] DEPLOYMENT INCOMPLETE', '', '  +------------------------------------------------------+', '  |                                                      |', '  |                         /\\                           |', '  |           /\\           /  \\        /\\                |', '  |     /\\   /  \\    /\\    /    \\      /  \\       /\\       |', '  |____/  \\_/    \\__/  \\__/      \\____/    \\_____/  \\______|', '  |                                                      |', '  +------------------------------------------------------+', '', '[DESCENT] PULL UP'],
        ['[WARNING] TERRAIN COLLISION', '', '   +------------------------------------------------------+', '   |       /       \\            /        \\                |', '   |      /         \\          /          \\      /        |', '   |_____/           \\________/            \\____/         |', '   |           ||                    ||              ||   |', '   |     ------||-----         ------||------        ||   |', '   |           ||                    ||              ||   |', '   +------------------------------------------------------+', '', '[ENGINES] EMERGENCY SHUTDOWN'],
        ['[CRITICAL] IMPACT DETECTED', '', '  +------------------------------------------------------+', '  |          \\                    /                      |', '  |           \\       |          /                       |', '  |------------\\------*---------/-------------------------|', '  |             \\   / | \\     /                          |', '  |              \\ /  |  \\___/                           |', '  |               /   |      \\                           |', '  +------------------------------------------------------+', '', '[FLIGHT RECORDER] SIGNAL L—'],
    ]
    index = 0
    start = 0
    while index < len(frames):
        if index == 2:
            for lines, delay in zip(crash_frames, (0.2, 0.2, 0.15)):
                intro_timed_frame(lines, delay)
            intro_timed_frame([], 0.45)
        if index == 4:
            lead, notices, _ = frames[index].split("\n\n", 2)
            lines = textwrap.wrap(lead, width=72) + [""]
            intro_timed_frame(lines, 1.0)
            for notice in notices.splitlines():
                lines.append(notice)
                intro_timed_frame(lines, 0.4)
        result = intro_frame(frames[index], start=start)
        if result == "back":
            start = -1 if index > 0 else 0
            index = max(0, index - 1)
        else:
            index += 1
            start = 0

def explosion_animation():
    frames = [
        ("[REACTOR] NO CORRECTIVE ACTION\n\n"
         "You leave the controls untouched.\n"
         "The temperature continues to rise.\n\n"
         "TEMPERATURE  [######----]\nPRESSURE     [#####-----]", 0.8),
        ("[EMERGENCY] COOLANT BOILING\n"
         "[WARNING] PRESSURE LIMIT EXCEEDED\n\n"
         "TEMPERATURE  [#########-]\nPRESSURE     [##########]\n\n"
         "The deck shakes beneath your feet.", 1.2),
        ("[EMERGENCY] CORE FAILURE IMMINENT\n\n"
         "                   3\n\n"
         "[EVACUATION] NO SAFE ROUTE", 0.65),
        ("[EMERGENCY] CORE FAILURE IMMINENT\n\n"
         "                   2\n\n"
         "[PRESSURE] SENSOR FAILURE", 0.65),
        ("[EMERGENCY] CORE FAILURE IMMINENT\n\n"
         "                   1\n\n"
         "[CONTAINMENT] LOST", 0.65),
        (r"""[CRITICAL] CORE COLLAPSE

                   \ | /
                    \|/
             _______*_______
        ____/______###______\____
       /__________#####__________\
       \____________*____________/

The reactor casing splits. You have nowhere to go.""", 0.75),
        (r"""                 \    |    /
             .    \   |   /    .
                 **#######**
          .   ***###########***   .
       ------###################------
          .   ***###########***   .
                 **#######**
             .    /   |   \    .
                 /    |    \

              REACTOR BREACH""", 0.4),
        (r"""     /___       #         ___\
          \       *      /
   #          __/   \__          #
         .       ***        .
  <<<<<<<<<<     ***     >>>>>>>>>>
         .                  .

The ship tears apart.
You and the creatures aboard are caught in the blast.""", 0.9),
        (r"""  <<<<<<<<                     >>>>>>>>

    /\       /\       /\       /\
   /  \     /  \     /  \     /  \
  -----------\--------/-------------
       /       \    /       \

The shockwave flattens the trees around the wreck.
Much of the surrounding forest is destroyed.""", 1.0),
        ("       .                        .\n"
         "                 *\n\n"
         "   .                    .\n\n"
         "Fragments fall through the smoke.", 0.9),
        ("                         .\n\n\n\nSilence.", 0.8),
        ("THE END.", 0.8),
    ]
    play_reactor_frames(frames)


def reactor_repair_animation():
    frames = [
        ("[DIAGNOSTICS] COOLANT CONTROL UNRESPONSIVE\n"
         "[MANUAL OVERRIDE] ACCEPTED\n\n"
         "You isolate the failed controller and open the bypass.\n\n"
         "COOLANT FLOW  [##--------]  20%", 0.9),
        ("[REPAIR] BYPASS RESPONDING\n"
         "[CORE TEMPERATURE] FALLING\n\n"
         "COOLANT FLOW  [########--]  80%\n\n"
         "The readings begin to settle.", 0.9),
        ("[REPAIR] STABILIZATION IN PROGRESS\n\n"
         "           +----------------+\n"
         "           |     SEALED     |\n"
         "           |                |\n"
         "           +----------------+\n\n"
         "A heavy impact bends the door inward.\n"
         "[DOOR INTEGRITY] 72%", 0.9),
        ("[REPA_R] ST_BIL_ZATION IN PR_GRESS\n\n"
         "           +-------/--------+\n"
         "           |      /         |\n"
         "           |     /          |\n"
         "           +----------------+\n\n"
         "A sudden jolt shakes the entire structure.\n"
         "[IMPACT] DETECTED\n[DOOR INTEGRITY] 38%", 1.2),
        ("[REPAIR] STABILIZATION IN PROGRESS\n"
         "[DOOR INTEGRITY] 38%\n\n"
         "The display recovers. Another impact tears a hinge loose.", 0.9),
        ("[DOOR INTEGRITY] 0%\n[WARNING] CONTAINMENT BREACH\n\n"
         "     /---/                         __\n"
         "    / o o\\                       /oo\\\n"
         "   /  ___ \\                 ____/|  |\\____\n"
         "  / /     \\ \\                  /|__|\\\n"
         " /_/       \\_\\                / /  \\ \\\n\n"
         "The Ghost slips through the broken frame.\n"
         "The Hunter forces the rest of the door aside.\n"
         "You reach for the controls. Neither lets you finish.", 2.5),
        ("", 0.9),
        ("YOU DIED.", 1.0),
    ]
    play_reactor_frames(frames)


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
                           "  ||    ||   []    ||", "[DISPLAY] SYNC LOST"], 0.8)
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

