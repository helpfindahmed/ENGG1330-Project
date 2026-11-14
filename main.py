import sys
import time
from cinematics import play_introduction
from menus import main_menu, open_terminal, debug_menu
from level_forest import run_forest_level
from level_ship import run_ship_level

def main():
    while True:
        start_choice = main_menu()
        if start_choice == "X":
            sys.exit(0)
        elif start_choice == "2":
            open_terminal()
            continue
        elif start_choice == "3":
            debug_mode = debug_menu()
            break
        else:
            debug_mode = "full"
            break

    if debug_mode == "full":
        play_introduction()
    elif debug_mode == "forest":
        print("Starting forest debug sequence...")
        time.sleep(0.5)

    if debug_mode == "ship":
        clear_first_level = True
    else:
        clear_first_level = run_forest_level()

    if clear_first_level:
        run_ship_level()

if __name__ == "__main__":
    main()