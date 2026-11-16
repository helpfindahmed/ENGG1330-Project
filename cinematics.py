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
    """Show the assignment, the crash, and the first playable objective."""
    crash_frames = [
        r'''You are a ship engineer headed to repair a mining freighter.
A navigation failure sends your ship down over a forest.

[LANDING GEAR] JAMMED
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
    aftermath = [
        "AFTER THE CRASH",
        "",
        "Both engines are down. You take a flashlight and step outside",
        "to check the damage. You lose sight of the wreck in the trees.",
        "",
        "Your handheld finally picks up the ship's beacon to the east.",
        "Then you hear something moving nearby.",
        "",
        "Get back to the ship and restore power before dark.",
    ]
    show_intro_pages([*crash_frames, aftermath])


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
