"""Terminal sizing, bounded rendering, and line input."""

import os
import sys
import textwrap
import time


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


def panel_answer(lines, prompt="Setting > ", max_length=16):
    """Bound puzzle input to one screen, including invalid or pasted input."""
    saved = None
    answer = ""
    overflow = 0
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
                # Reject overflow so a truncated prefix cannot be submitted.
                return "\x00" if overflow else answer.strip()
            if key in ("\x08", "\x7f"):
                if overflow:
                    overflow -= 1
                else:
                    answer = answer[:-1]
            elif max_length and key and len(key) == 1 and " " <= key <= "~":
                if len(answer) < max_length:
                    answer += key
                else:
                    overflow += 1
    except (EOFError, KeyboardInterrupt):
        raise SystemExit(0)
    finally:
        if saved is not None:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, saved)
