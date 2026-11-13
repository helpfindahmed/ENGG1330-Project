"""Optional forest ending and reactor finale."""

import os
import sys

from intro import intro_timed_frame
from terminal_ui import panel_answer


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
        intro_timed_frame(["[CONTAINMENT SIGNAL LOST]"], 1.0)
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)
    finally:
        if saved is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, saved)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    panel_answer(["SECRET ENDING - SIGNAL LOST", "",
                  "You follow the trail away from the wreck.",
                  "The ship's beacon fades. Nothing answers your radio.",
                  "By dawn, you are out of the forest.",
                  "Whatever was on the ship is still out there.", "",
                  "To restart, run this Python file again."],
                 "Press Enter to exit > ", 0)


def play_reactor_frames(frames):
    """Run bounded cinematics with no echoed keys or gameplay-state changes."""
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


def reactor_repair_animation():
    frames = [
        ("[DIAGNOSTICS] COOLANT CONTROL UNRESPONSIVE\n"
         "[MANUAL OVERRIDE] ACCEPTED\n\n"
         "You isolate the failed controller and open the bypass.\n\n"
         "COOLANT FLOW  [##--------]  20%", 0.9),
        ("[REPAIR] BYPASS RESPONDING\n"
         "[CORE TEMPERATURE] FALLING\n\n"
         "COOLANT FLOW  [########--]  80%\n\n"
         "The readings begin to settle.", 0.8),
        ("[REPAIR] STABILIZATION IN PROGRESS\n\n"
         "           +----------------+\n"
         "           |     SEALED     |\n"
         "           |                |\n"
         "           +----------------+\n\n"
         "A heavy impact bends the door inward.\n"
         "[DOOR INTEGRITY] 72%", 0.7),
        ("[REPA_R] ST_BIL_ZATION IN PR_GRESS\n\n"
         "           +-------/--------+\n"
         "           |      /         |\n"
         "           |     /          |\n"
         "           +----------------+\n\n"
         "[IMPACT] DETECTED\n[DOOR INTEGRITY] 38%", 0.15),
        ("[REPAIR] STABILIZATION IN PROGRESS\n"
         "[DOOR INTEGRITY] 38%\n\n"
         "The display recovers. Another impact tears a hinge loose.", 0.55),
        ("[DOOR INTEGRITY] 0%\n[WARNING] CONTAINMENT BREACH\n\n"
         "     /---/                         __\n"
         "    / o o\\                       /oo\\\n"
         "   /  ___ \\                 ____/|  |\\____\n"
         "  / /     \\ \\                  /|__|\\\n"
         " /_/       \\_\\                / /  \\ \\\n\n"
         "The Ghost slips through the broken frame.\n"
         "The Hunter forces the rest of the door aside.\n"
         "You reach for the controls. Neither lets you finish.", 0.9),
        ("", 0.2),
        ("YOU DIED.", 1.0),
    ]
    play_reactor_frames(frames)


def reactor_decision():
    """Checkpoint: retries stay here without consuming a combat turn."""
    attempts = 0
    feedback = ""
    while True:
        lines = ["[WARNING] REACTOR UNSTABLE", "",
                 "Coolant control has failed. Core temperature is rising.",
                 "", "[1] Attempt to repair the reactor", "[2] Do nothing"]
        if feedback:
            lines += ["", feedback]
        choice = panel_answer(lines, "Choose 1 or 2, then press Enter > ")
        if choice == "2":
            return
        if choice != "1":
            feedback = "Invalid choice. Enter 1 or 2."
            continue
        attempts += 1
        reactor_repair_animation()
        lines = ["YOU DIED.", ""]
        if attempts >= 2:
            lines += ["You don't learn, do you?", ""]
        lines += ["CHECKPOINT: REACTOR CONTROL PANEL",
                  "Both engines remain repaired."]
        panel_answer(lines, "Press Enter to return to the decision > ", 0)
        feedback = ""


def explosion_animation():
    frames = [
        ("[REACTOR] NO CORRECTIVE ACTION\n\n"
         "You leave the controls untouched.\n"
         "The temperature continues to rise.\n\n"
         "TEMPERATURE  [######----]\nPRESSURE     [#####-----]", 0.8),
        ("[EMERGENCY] COOLANT BOILING\n"
         "[WARNING] PRESSURE LIMIT EXCEEDED\n\n"
         "TEMPERATURE  [#########-]\nPRESSURE     [##########]\n\n"
         "The deck shakes beneath your feet.", 0.7),
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

The reactor casing splits. You have nowhere to go.""", 0.55),
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
You and the creatures aboard are caught in the blast.""", 0.8),
        (r"""  <<<<<<<<                     >>>>>>>>

    /\       /\       /\       /\
   /  \     /  \     /  \     /  \
  -----------\--------/-------------
       /       \    /       \

The shockwave flattens the trees around the wreck.
Much of the surrounding forest is destroyed.""", 0.9),
        ("       .                        .\n"
         "                 *\n\n"
         "   .                    .\n\n"
         "Fragments fall through the smoke.", 0.6),
        ("                         .\n\n\n\nSilence.", 0.8),
        ("THE END.", 0.8),
    ]
    play_reactor_frames(frames)
    panel_answer(["THE END.", "", "You died in the reactor explosion.",
                  "The Ghost and Hunter were destroyed aboard the ship.",
                  "Much of the surrounding forest is gone.", "",
                  "To restart, run this Python file again."],
                 "Press Enter to exit > ", 0)
