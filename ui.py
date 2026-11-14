import os
import sys
import textwrap

# Pull in the terminal sizing tools you moved to cinematics
from cinematics import intro_terminal_size, intro_draw, _intro_key
from turn_input import read_turn

MAP_COLORS = {
    "@": "96", "☺": "96",
    "1": "93", "2": "93", "R": "93", "C": "93", "?": "93",
    ">": "92", "<": "92",
    "$": "95", "*": "95",
}

def plain_map():
    return (not sys.stdout.isatty() or os.environ.get("TERM") == "dumb"
            or "NO_COLOR" in os.environ)


def player_icon():
    encoding = (sys.stdout.encoding or "").lower().replace("-", "")
    # Use the one-cell text face in UTF-8 terminals, including Windows ConPTY.
    return "☺" if not plain_map() and encoding == "utf8" else "@"


def print_map(display, panel, show_floor):
    color = os.name == "posix" and bool(os.environ.get("TERM")) and not plain_map()
    icon = player_icon()
    for index, row in enumerate(display):
        tiles = "".join(row).replace("@", icon)
        if not show_floor:
            tiles = tiles.replace(".", " ")
        side = panel[index].replace("@", icon) if index < len(panel) else ""
        tiles = f"{tiles:<60}"
        if color:
            tiles = "".join(
                f"\033[{MAP_COLORS[tile]}m{tile}\033[0m" if tile in MAP_COLORS else tile
                for tile in tiles
            )
        print(f"{tiles} {side}".rstrip())

def print_dialogue(msg, width=78, max_lines=4):
    if not msg:
        return
    lines = []
    for paragraph in msg.splitlines():
        lines.extend(textwrap.wrap(paragraph, width=width) or [""])
    for line in lines[:max_lines]:
        print(line)

def terminal_ready():
    size = intro_terminal_size()
    if size[0] >= 80 and size[1] >= 24:
        return True
    intro_draw([], "", size)
    return False

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

def read_map_turn(redraw):
    while True:
        if terminal_ready():
            move = read_turn()
            if move == "X" or terminal_ready():
                return move
        panel_answer(["Terminal resized. Press Enter to resume."], "Continue > ", 0)
        redraw()