"""Read one turn at a time while keeping text prompts in line mode."""

import os
import sys
import time


PASTED_MOVE = "PASTED_MOVE"
TERMINAL_TOO_SMALL = "TERMINAL_TOO_SMALL"

def _read_command(read_key, prompt):
    while True:
        print("\r\033[2K" + prompt, end="", flush=True)
        key = read_key()
        if key == TERMINAL_TOO_SMALL:
            return TERMINAL_TOO_SMALL
        if key in ("", "\x04", "X"):
            return "X"
        if key in ("\r", "\n", "\x1b"):
            continue
        if key != "F":
            if len(key) == 1 and key.isprintable():
                print(key, end="", flush=True)
            return key

        print("\r\033[2KAim [WASD, Esc to cancel] > ", end="", flush=True)
        direction = read_key()
        if direction in ("", "\x04", "X"):
            return "X"
        if direction in (PASTED_MOVE, TERMINAL_TOO_SMALL):
            return direction
        if direction in ("W", "A", "S", "D"):
            return "F" + direction
        if direction not in ("\r", "\n", "\x1b"):
            return "F?"


def _read_windows_key(wait=None):
    import msvcrt

    if wait is not None and not msvcrt.kbhit():
        time.sleep(wait)
        return None
    key = msvcrt.getwch()
    if key in ("\x00", "\xe0"):
        # Windows reports arrows and other special keys as two characters.
        msvcrt.getwch()
        return "\x1b"
    return key.upper()


def posix_key_reader(fd, wait=None):
    """Return a key reader that filters terminal escapes and bracketed paste."""
    import select

    pending_key = b""

    def discard_paste():
        # Terminals that support bracketed paste send an end marker.
        end_marker = b"\x1b[201~"
        tail = b""
        while select.select([fd], [], [], 1)[0]:
            part = os.read(fd, 1)
            if not part:
                break
            tail = (tail + part)[-len(end_marker):]
            if tail == end_marker:
                break

    def read_key():
        nonlocal pending_key
        if not pending_key and wait is not None and not select.select([fd], [], [], wait)[0]:
            return None
        key = pending_key or os.read(fd, 1)
        pending_key = b""
        if key != b"\x1b":
            return key.decode("ascii", errors="replace").upper()

        # Consume terminal escape sequences so an arrow's final letter
        # cannot become a movement command.
        if select.select([fd], [], [], 0.03)[0]:
            prefix = os.read(fd, 1)
            if prefix in (b"[", b"O"):
                sequence = prefix
                while select.select([fd], [], [], 0.03)[0]:
                    part = os.read(fd, 1)
                    if not part:
                        break
                    if len(sequence) < 8:
                        sequence += part
                    if b"@" <= part <= b"~":
                        break
                if sequence == b"[200~":
                    discard_paste()
                    return PASTED_MOVE
            else:
                pending_key = prefix
        return "\x1b"

    return read_key


def read_turn(prompt="Move [WASD | F + direction | E | T | H | X] > ", *,
              can_play=None):
    if not sys.stdin.isatty() or os.name not in ("nt", "posix"):
        try:
            return input("Enter your move: ").strip().upper()
        except EOFError:
            return "X"
    wait = 0.05 if can_play is not None else None

    def read_checked(read_key):
        while can_play is None or can_play():
            key = read_key()
            if key is not None:
                if can_play is not None and not can_play():
                    break
                return key
        return TERMINAL_TOO_SMALL

    if os.name == "nt":
        return _read_command(lambda: read_checked(lambda: _read_windows_key(wait)), prompt)

    import termios
    import tty

    fd = sys.stdin.fileno()
    original = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd, termios.TCSANOW)
        print("\033[?2004h", end="", flush=True)
        read_key = posix_key_reader(fd, wait=wait)
        return _read_command(lambda: read_checked(read_key), prompt)
    finally:
        termios.tcsetattr(fd, termios.TCSANOW, original)
        print("\033[?2004l", end="", flush=True)
