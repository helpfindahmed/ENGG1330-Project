import os

raw_map = [
    "########",
    "#@.....#",
    "#.##...#",
    "#....>.#",
    "########"
]

grid = [list(row) for row in raw_map]

player_x = -1
player_y = -1

for y in range(len(grid)):
    for x in range(len(grid[y])):
        if grid[y][x] == "@":
            player_y = y
            player_x = x

# Initial screen clear and render
os.system('cls' if os.name == 'nt' else 'clear')
for row in grid:
    print("".join(row))

loop = True
print("X to exit")

while loop:
    target_x = player_x
    target_y = player_y
    valid_move = False

    move = input("Enter your move: ").upper()

    if move == "W":
        target_y -= 1
        valid_move = True
    elif move == "A":
        target_x -= 1
        valid_move = True
    elif move == "S":
        target_y += 1
        valid_move = True
    elif move == "D":
        target_x += 1
        valid_move = True
    elif move == "X":
        loop = False
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        for row in grid:
            print("".join(row))
        print("Invalid input")
        print("X to exit")
        continue

    if valid_move:
        if grid[target_y][target_x] == "#":
            msg = "Blocked by tree"
        elif grid[target_y][target_x] == ">":
            msg = "You escaped the dark woods!"
            loop = False
        else:
            grid[target_y][target_x] = "@"
            grid[player_y][player_x] = "."
            player_x = target_x
            player_y = target_y
            msg = ""

    os.system('cls' if os.name == 'nt' else 'clear')
    for row in grid:
        print("".join(row))
    print("X to exit")

    if msg:
        print(msg)