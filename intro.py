"""Opening story and narrative screen transitions."""

import os
import sys
import textwrap
import time

from terminal_ui import _intro_key, intro_draw, intro_terminal_size


def intro_steps(text):
    """Build sentence reveals, keeping system blocks and objectives together."""
    import re

    steps = []
    lines = []
    for paragraph in text.split("\n\n"):
        if not paragraph.strip():
            continue
        if paragraph.startswith(("[", "OBJECTIVE:")):
            units = [paragraph]
        else:
            units = re.split(r"(?<=[.!?])\s+", paragraph)
        for unit in units:
            added = [line for part in unit.splitlines()
                     for line in (textwrap.wrap(part, width=72) or [""])]
            if len(added) > 18:
                raise ValueError("Introduction sentence exceeds its text area")
            separator = [""] if lines else []
            if len(lines) + len(separator) + len(added) > 18:
                lines = []
                separator = []
            lines = lines + separator + added
            steps.append(lines[:])
    return steps or [[""]]


def intro_frame(text, start=0):
    """Reveal one sentence per Enter; Backspace revisits the previous step."""
    steps = intro_steps(text)
    index = min(start, len(steps) - 1)
    prompt = "Enter to continue | Backspace to go back | Ctrl+C to quit"
    interactive = sys.stdin.isatty()
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
    """Short narrative pages with Enter and Backspace navigation."""
    frames = [
        (
            'You are a spacecraft systems engineer. Your employer sends you '
            'between planets to fix equipment nobody bothers maintaining.\n'
            '\n'
            'You don’t get paid enough for this, but you do get paid.\n'
            '\n'
            'That has kept you here for six years.\n'
            '\n'
            'Today’s job is an overheating mining plant. Someone installed the'
            ' coolant regulator backwards.\n'
            '\n'
            'Your supervisor has allowed two hours.\n'
            'Travel, apparently, is something you do in your spare time.'
        ),
        (
            'Halfway there, the ship changes course.\n'
            '\n'
            '[NAVIGATION] UNSCHEDULED COURSE CORRECTION\n'
            '\n'
            'You cancel it. The ship turns again.\n'
            '\n'
            'You switch to manual control, but the navigation display keeps '
            'jumping. An unidentified planet fills the window.\n'
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
            'Then the signal disappears.\n'
            '\n'
            '[ROUTE GUIDANCE] RECALCULATING\n'
            '\n'
            'You climb a slope to recover it. When you turn back, you cannot '
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
            'It is getting dark. Something moves behind the trees.\n'
            '\n'
            'You stop looking for the regulator.\n'
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
        result = intro_frame(frames[index], start=1 if index == 4 else 0)
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
