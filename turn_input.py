"""Read one turn at a time while keeping text prompts in line mode."""

import os
import sys


def _read_command(read_key, prompt):
    while True:
        print("\r\033[2K" + prompt, end="", flush=True)
        key = read_key()
        if key in ("", "\x04", "X"):
            return "X"
        if key in ("\r", "\n", "\x1b"):
            continue
        if key != "F":
            print(key, end="", flush=True)
            return key

        print("\r\033[2KAim [WASD, Esc to cancel] > ", end="", flush=True)
        direction = read_key()
        if direction in ("", "\x04", "X"):
            return "X"
        if direction in ("W", "A", "S", "D"):
            return "F" + direction


def _read_windows_key():
    import msvcrt

    key = msvcrt.getwch()
    if key in ("\x00", "\xe0"):
        # Windows reports arrows and other special keys as two characters.
        msvcrt.getwch()
        return "\x1b"
    return key.upper()


def read_turn(prompt="Move [WASD | F + direction | E | T | H | X] > "):
    if not sys.stdin.isatty() or os.name not in ("nt", "posix"):
        return input("Enter your move: ").strip().upper()
    if os.name == "nt":
        return _read_command(_read_windows_key, prompt)

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
        return _read_command(read_key, prompt)
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, original)
