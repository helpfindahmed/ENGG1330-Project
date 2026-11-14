# ENGG1330-Project
Year 1 Sem 1 ENGG1330 Project
======================================================
PROJECT SURVIVAL: STRATEGY & MECHANICS GUIDE
======================================================

Welcome to the dark. This game is designed to be punishing but fair. Surviving the forest and the crashed ship requires route planning, resource management, and a deep understanding of how the enemy AI tracks you.

Here is everything you need to know to survive.

In a macOS, Linux, or Windows terminal, press WASD to move one turn at a time.
Press F and then a direction to fire. Menus and puzzle answers use Enter.
If the game shows `Enter your move:`, type your command and press Enter
(for a Big Bang, type both letters together, such as `FW`).
Interactive UTF-8 terminals show ☺ for the player, with cyan on macOS and
Linux terminals that support colour. Plain terminals use @. Set `NO_COLOR=1`
for plain ASCII.

------------------------------------------------------
1. THE DUAL AI SYSTEM (GHOST VS. HUNTER)
------------------------------------------------------
You are being hunted by two distinct entities that work together to trap you:
*   The Hunter (H): Relentlessly chases your exact current position.
*   The Ghost (G): Uses a pathfinding algorithm to predict your escape route and cut you off at choke points ahead of you.
*   The Grace Period: The aliens start moving after your first 8 turns in the forest. Use this time to secure early debris coins and position yourself.

------------------------------------------------------
2. MAP DESIGN: BREAKING LINE OF SIGHT
------------------------------------------------------
You cannot simply hold 'D' and sprint to the exit. If the aliens are within 8 tiles of you, they will sprint to close the gap.
*   Pillars and Islands: The map is deliberately filled with jagged walls and central islands. You must use these structures to break line of sight. Loop the Hunter around a wall to force it to recalculate its path.
*   The Gaps: We designed multiple routes through the central walls so you are never forced into a single dead-end corridor. Always have a secondary escape route in mind.

------------------------------------------------------
3. THE ECONOMY: WHY YOU CAN'T RUSH
------------------------------------------------------
Every step you take drains your Flashlight battery. If it hits 0, you die.
*   Level Carry-Over: Your battery, Big Bangs, and Traps carry over directly from the forest into the Level 2 Ship. Save enough battery to reach and repair the upper engine, which restores the ship's lights.
*   Debris Coins (*): Collect coins to buy extra battery, traps, or Big Bangs if you need them.
*   The Shop ($): Placed in opposite corners of the map. It acts as a high-risk rest stop. You have to push back into the corner of the maze to buy supplies, giving the aliens a chance to corner you. Maneuvering through requires proper thought and strategy.

------------------------------------------------------
4. COMBAT & DEFENSE
------------------------------------------------------
You have two primary defensive tools. Use them efficiently, as resources are strictly limited:
*   Big Bangs (F + Direction): This is a finite ammo resource. It shoots a beam that stuns any alien in its path for 5 turns. Save these for when the Hunter successfully cuts off your only escape corridor.
*   Traps (T): Traps cost 1 battery to place and arm when you step off them. Drop these in narrow 1-tile gaps behind you while being chased by the Ghost. Do not waste them in open rooms where enemies can path around them.

------------------------------------------------------
5. THE FINAL PHASE: THE SHIP
------------------------------------------------------
Once you reach the exit (>), you enter the crashed ship.
*   Enter the upper engine room [1], then the lower engine room [2]. Stand next to or on the control panel (C) and press E.
*   Your flashlight will continue to drain until one of the engines is online. Move with purpose.
*   Once the engine fires, the emergency lights come on (stopping battery drain), and once both the engines are on the Ghost and Hunter board the ship. You must navigate the tight corridors, dodge the aliens, and reach the Reactor [R] to initiate the self-destruct sequence.

## Member contributions

### Hongkang Liu (Louis)

- Drafted a first-floor map proposal and improved map readability with a
  distinct player marker, labeled engine-room entrances, and an ASCII fallback.
- Designed and implemented the two linked ship engine puzzles, including
  repair status, progressive hints, and retries within the puzzle panels.
- Added single-key turn-based movement and improved feedback for blocked moves,
  invalid commands, and menu input. Added in-game briefings and next objectives
  for the forest, engine rooms, and reactor.
- Playtested terminal controls on macOS, Windows, and Linux and verified
  the earlier integrated build in the offline course Docker container.
  Rechecked the ship route on Blackout after the module split at 80 columns
  by 24 rows.

### Syed Ahnaf Akif
- Developed the Hunter's pursuit logic and fixed pre-existing
  bugs during development.
- Developed the game's backstory and wrote and implemented the in-game
  dialogues    
- Created the initial UI changes, which Hongkang Liu (Louis) later refined
  and improved. 
- Added clearer feedback when obstacles block movement.
- Added the debug menu and checkpoints to access different parts of the game
  during development.
- Implemented the forest exit confirmations and the secret ending
- Implemented the reactor sequence, both reactor choices, the repair-death
  checkpoint, repeated-attempt dialogue, and explosion ending.
- Added help-menu unlocking through interaction with the help terminal.
  AI assistance used during development is recorded in ai_use.md.
