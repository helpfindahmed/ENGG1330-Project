"""Read one command at a time while keeping text prompts in line mode."""

import os
import sys


def read_turn(prompt="Move [WASD | F + direction | E | T | X] > "):
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
            print(prompt, end="", flush=True)
            key = read_key()
            if key in ("", "\x04", "X"):
                print()
                return "X"
            if key in ("\r", "\n", "\x1b"):
                print()
                continue
            if key != "F":
                print(key)
                return key

            print("F")
            print("Aim [WASD, Esc to cancel] > ", end="", flush=True)
            direction = read_key()
            print()
            if direction in ("", "\x04", "X"):
                return "X"
            if direction in ("W", "A", "S", "D"):
                return "F" + direction
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, original)
