"""Run with python3 direct_wasd_demo.py in a terminal."""

from turn_input import read_turn


def main():
    x, y = 0, 0
    turn = 0
    print("Direct WASD demo. E opens a text prompt. F then WASD aims. X quits.")
    while True:
        print(f"Turn {turn} | player x={x} | enemy turns={turn} | player y={y}")
        command = read_turn("Move [WASD | F + direction | E | T | X] > ")
        if command == "X":
            break
        if command == "E":
            answer = input("Panel answer (press Enter) > ")
            print(f"Panel received: {answer}")
        elif command in ("W", "A", "S", "D", "FW", "FA", "FS", "FD", "T"):
            x += {"A": -1, "D": 1}.get(command, 0)
            y += {"W": -1, "S": 1}.get(command, 0)
            turn += 1
            if command.startswith("F"):
                print(f"Flash: {command}")


if __name__ == "__main__":
    main()
