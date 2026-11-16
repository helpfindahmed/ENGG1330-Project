import os
import sys
import time
import textwrap

def play_introduction():
    intro_story()


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

def show_intro_pages(pages):
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
        _navigate_story_pages(pages)
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)
    finally:
        if saved_input is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, saved_input)
        sys.stdout.write("\033[?25h\033[H")
        sys.stdout.flush()



def _navigate_story_pages(pages):
    prompt = "Enter to continue | Backspace to go back | Ctrl+C to quit"
    index = 0
    interactive = sys.stdin.isatty() or (
        os.name == "nt" and sys.stdout.isatty()
    )
    previous = None
    while True:
        size = intro_terminal_size()
        ready = size[0] >= 80 and size[1] >= 24
        if (size, index) != previous:
            intro_draw(pages[index], prompt, size)
            previous = (size, index)
        key = _intro_key(interactive, ready, size)
        if key in ("\x03", "\x04"):
            raise KeyboardInterrupt
        if not ready or intro_terminal_size() != size:
            continue
        if key in ("\x08", "\x7f"):
            index = max(0, index - 1)
        elif key in ("\n", "\r"):
            if index == len(pages) - 1:
                return
            index += 1

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
        r'''[LANDING GEAR] JAMMED

                            : :           ENGINE PLUME
                         ___|=|___
                        /   | |   \
                       /____|O|____\
                            | |
                            \ /
                             V            SHIP IN DESCENT


           /\                                  /\
          /__\    /\                    /\    /__\
      _____||____/__\__________________/__\____||_____

The landing gear will not deploy. Pull up!'''.splitlines(),
        r'''[WARNING] TERRAIN COLLISION IMMINENT



                         ___|=|___
                        /   | |   \
                       /____|O|____\
                            | |
                            \ /
                             V
                             |
           /\                v                 /\
          /__\    /\                    /\    /__\
      _____||____/__\__________________/__\____||_____

Engines offline. The ship is falling toward the trees.'''.splitlines(),
        r'''[CRITICAL] IMPACT DETECTED






                         ___|=|___
                        /   | |   \
                       /____|O|____\
                            | |
           /\               \ /     *          /\
          /__\    /\    \    V    /     /\    /__\
      _____||____/__\____\__***__/_____/__\____||_____

The ship hits the ground. Flight recorder signal lost.'''.splitlines(),
    ]
    pages = [page for scene in frames[:2] for page in intro_steps(scene)]
    pages.extend(crash_frames)
    pages.extend(page for scene in frames[2:] for page in intro_steps(scene))
    show_intro_pages(pages)


def explosion_animation():
    show_intro_pages([
        r"""[REACTOR] CORE FAILURE IMMINENT

You take your hands off the controls.
The damaged hull cannot lift off. There is no safe way out.

If the core fails now, the creatures will still be aboard.""".splitlines(),
        r"""[CRITICAL] CORE COLLAPSE

                   \ | /
                    \|/
             _______*_______
        ____/______###______\____
       /__________#####__________\
       \____________*____________/

The core ruptures. The blast tears through the ship.""".splitlines(),
        r"""[FLIGHT RECORDER] FINAL ENTRY

    /\       /\       /\       /\
   /  \     /  \     /  \     /  \
  -----------\--------/-------------
       /       \    /       \

You die in the blast. So do both creatures.
The shockwave takes much of the forest with it.

You came to fix a ship. In the end, you had to decide
what you were willing to lose to keep them from getting out.""".splitlines(),
    ])


def reactor_repair_animation():
    show_intro_pages([
        r"""[REPAIR] MANUAL BYPASS OPEN

Coolant is flowing again. The temperature begins to fall.

           +-----------------+
           |      SEALED     |
           |                 |
           +-----------------+

You need a little more time. Something hits the door.""".splitlines(),
        r"""[WARNING] DOOR BREACH

     /---/                         __
    / o o\                       /oo\
   /  ___ \                 ____/|  |\____
  / /     \ \                  /|__|\
 /_/       \_\                / /  \ \

The Ghost slips through the door. The Hunter forces it open.
They reach you before the reactor stabilizes.

You had found a way to save the ship. You ran out of time.""".splitlines(),
    ])


def secret_ending():
    show_intro_pages([
        [
            "SECRET ENDING | THE SIGNAL",
            "",
            "You leave the ship behind and follow the trail uphill.",
            "The trees thin out. For the first time, your radio gets through.",
            "",
            "You send the crash coordinates and a warning:",
            "  Two creatures at the wreck. Do not land nearby.",
        ],
        [
            "[RADIO] MESSAGE RECEIVED",
            "",
            "A survey crew picks you up from the ridge at dawn.",
            "Below you, the ship's beacon still blinks through the trees.",
            "",
            "You came here to fix a ship. All you could bring back",
            "was a warning. Someone heard it.",
        ],
    ])
