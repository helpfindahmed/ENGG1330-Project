import os


raw_map = [
    "#######################",
    "#@..........###.......#",
    "#.######..............#",
    "#.....$..#...######.###",
    "#.....................#",
    "#........###.....>....#",
    "#######################"
]


s = {"grid": [list(row) for row in raw_map],
     "px":-1,
     "py":-1,
     "oxygen":0,
     "traps":0,
     "coins": 70,
     "heat": 0,
     "beam_range":4,
     "ghosts":[[-1,-1], [-1,-1]],
     "tl":[] #add traps as you go on so everytime a trap is added you add a dictionary stating position and triggered status
     }


s["oxygen"] = 100
s["traps"] = 3

def show_status():
    print(f"OxygenLevel: [{'*' * (s['oxygen'] // 10):10}] {s['oxygen']}")
    print(f" CoinsLeft : [{'*' * (s['coins'] // 7):10}] {s['coins']}")
    print(f" HeatLevel : [{'*' * (s['heat'] // 10):10}] {s['heat']}")
    print(f" Trap_Left : [{'*' * s['traps']}] {s['traps']}")
    
def enter_shop():
    print("enter 1 for 20 OxygenLevel    - 40cc")
    print("enter 2 for a trap            - 20cc")
    print("enter 3 for lowering 20 heat  - 30cc")
    opt = int(input())
    if(opt == 1) and s["coins"]>=40:
        if(s["oxygen"]<=80):
            s["oxygen"]+=20
        else:
            s["oxygen"] = 100
        s["coins"]-=40
        
    elif(opt == 2) and s["coins"]>=20:
        s["traps"]+=1
        s["coins"]-=20

    elif(opt == 3) and s["coins"]>=30:
        if(s["heat"]>=20):
            s["heat"]-=20
        else:
            s["heat"]=0
        s["coins"]-=30
    elif(opt!=1)and(opt!=2)and(opt!=3):
        print("invalid input")
    else:
        print("Not enough money")

for y in range(len(s["grid"])):
    for x in range(len(s["grid"][y])):
        if s["grid"][y][x] == "@":
            s["py"] = y
            s["px"] = x
            

# Initial screen clear and render
os.system('cls' if os.name == 'nt' else 'clear')
for row in s["grid"]:
    print("".join(row))
show_status()

trap = False
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
        if s["traps"] > 0:
            if any(t["tx"] == s["px"] and t["ty"] == s["py"] for t in s["tl"]):
                msg = "There is already a trap there"
            else:
                s["traps"] -= 1
                s["oxygen"] -= 1
                s["tl"].append({"tx": s["px"], "ty": s["py"], "triggered": False}) #inside the global dictionary you add the status of a new trap that has been placed on the map
                msg = "Trap placed. Step off to arm it."
                trap = True
        else:
            msg = "No traps left."
    elif move == "E":
        if (s["grid"][target_y][target_x+1] == "$") or (s["grid"][target_y][target_x-1] == "$") or (s["grid"][target_y+1][target_x] == "$") or (s["grid"][target_y-1][target_x] == "$"):
            enter_shop()
        else:
            print("Please get to the shop")
        continue
        
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
        if s["grid"][target_y][target_x] == "#":
            msg = "Blocked by tree"

        elif s["grid"][target_y][target_x] == ">":
            msg = "You escaped the dark woods!"
            loop = False

        else:
            if s["grid"][target_y][target_x] == "X":
                s["traps"] += 1
                # This is a list comprehension. It rebuilds the trap list from scratch, keeping only the traps that are NOT at target coordinates.
                s["tl"] = [t for t in s["tl"] if not (t["tx"] == target_x and t["ty"] == target_y)]
                msg = "Trap recovered!"

            # Draw the player on the new tile
            s["grid"][target_y][target_x] = "@"

            # Check if you are leaving a trap behind on your old tile
            left_trap = False
            for trap in s["tl"]:
                if trap["tx"] == s["px"] and trap["ty"] == s["py"]:
                    trap["triggered"] = True  # The trap arms when you step off
                    left_trap = True

            # Draw an X if there is a trap, otherwise draw a dirt path (.)
            if left_trap:
                s["grid"][s["py"]][s["px"]] = "X"
            else:
                s["grid"][s["py"]][s["px"]] = "."

            # Update coordinates and drain oxygen
            s["px"] = target_x
            s["py"] = target_y
            msg = ""
            s["oxygen"] -= 1
            if s["oxygen"] == 0:
                loop = False
                msg = "Game Over! Ran out of Oxygen."

    os.system('cls' if os.name == 'nt' else 'clear')
    for row in s["grid"]:
        print("".join(row))
    show_status()
    print("X to exit")

    if msg:
        print(msg)
