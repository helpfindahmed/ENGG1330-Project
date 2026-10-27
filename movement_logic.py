import os


raw_map = [
    "########",
    "#@.....#",
    "#.##...#",
    "#....>.#",
    "########"
]


s = {"grid": [list(row) for row in raw_map],
     "px":-1,
     "py":-1,
     "battery":0,
     "traps":0,
     "beam_range":4,
     "ghosts":[[-1,-1], [-1,-1]],
     "tl":[[-1,-1,0],[-1,-1,0],[-1,-1,0],[-1,-1,-1],[-1,-1,-1]] #tl is trap locations 3rd number index: -1: not bought ---- 0 and coordinates -1,-1: owned but not placed ---- 0 and coordinates != -1,-1: on the map ---- 2: triggered
     }


s["battery"] = 100
s["traps"] = 3


for y in range(len(s["grid"])):
    for x in range(len(s["grid"][y])):
        if s["grid"][y][x] == "@":
            s["py"] = y
            s["px"] = x
            

# Initial screen clear and render
os.system('cls' if os.name == 'nt' else 'clear')
for row in s["grid"]:
    print("".join(row))

loop = True
print("X to exit")

while loop:
    target_x = s["px"]
    target_y = s["py"]
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
    elif move == "T":
        
        valid_move = True
    elif move == "X":
        loop = False
    else:
        os.system('cls' if os.name == 'nt' else 'clear')
        for row in s["grid"]:
            print("".join(row))
        print("Invalid input")
        print("X to exit")
        continue

    if valid_move:
        s["battery"] -= 1
        if s["grid"][target_y][target_x] == "#":
            msg = "Blocked by tree"
        elif s["grid"][target_y][target_x] == ">":
            msg = "You escaped the dark woods!"
            loop = False
        else:
            s["grid"][target_y][target_x] = "@"
            s["grid"][s["py"]][s["px"]] = "."
            s["px"] = target_x
            s["py"] = target_y
            msg = ""

    os.system('cls' if os.name == 'nt' else 'clear')
    for row in s["grid"]:
        print("".join(row))
    print("X to exit")

    if msg:
        print(msg)