# ENGG1330-Project
Subclass D, Group 4

======================================================
BLACKOUT: STRATEGY & MECHANICS GUIDE
======================================================

Welcome to the dark. Blackout is a single-player, turn-based science-fiction
horror adventure played entirely in the terminal. Surviving the forest and the
crashed ship requires route planning, resource management, and an understanding
of how the two creatures track you. Repairing the ship is only part of the problem.

Group members: 

Here is everything you need to know to survive long enough to finish.

------------------------------------------------------
1. THE ASSIGNMENT: HOW YOU GOT HERE
------------------------------------------------------

You are a spacecraft systems engineer, travelling between planets to fix
problems someone else insists they did not cause.

However, an unscheduled course correction sends your ship towards an unidentified
planet. You crash in an enormous forest. Both engines are offline, and the
ship's thrust regulator is missing. A maintenance signal leads you outside
to look for it. Detours and unreliable navigation leave you lost before your
navigation system finally identifies the planet as exceptionally dangerous.

It is getting dark. Your immediate objective is to survive the forest and
return to your ship. Once aboard, solve two connected engine puzzles and
reach the reactor.
Or you could try your luck and go deeper into the forest. That option exists 
for a perfectly reasonable reason.

*   Distinctive Features: A direct-pursuit Hunter and an intercepting Ghost,
    limited supplies, linked engine repairs, a secret exit, and terminal
    cinematics.
*   Completion: Repair both engines and resolve the reactor sequence. Its
    final explosion ends the game; attempting repair returns you to the
    decision after a scripted death. The secret exit in the forest provides
    a separate ending. None of these endings rescues
    the player.
*   Playtime: The design target is approximately 5–10 minutes. Reading speed,
    puzzle retries, and repeated repair attempts affect the actual duration.

------------------------------------------------------
2. GETTING STARTED
------------------------------------------------------

Use Python 3 in an interactive terminal at least 80 columns wide and 24 rows
high. The game uses only Python's standard library. It runs offline and needs
no package installation, graphical window, audio device, or network connection.

The course environment recorded in the testing log is Docker **v03**. Use the
course-provided container and its launch instructions. Once inside the container, 
change to the folder containing `main.py` and run exactly:

```bash
python3 main.py
```

The same command works on macOS and Linux with Python 3 installed. On Windows,
from the project folder, use:

```powershell
py -3 main.py
```

Keep all eleven Python modules together under their normal names:
`main.py`, `state.py`, `map_data.py`, `alien_logic.py`, `level_forest.py`,
`level_ship.py`, `engine_puzzles.py`, `turn_input.py`, `ui.py`, `menus.py`,
and `cinematics.py`. Uploaded copies with names such as `menus(1).py` must be
renamed to `menus.py` so that imports resolve.

*   New Game: Play the introduction and enter the forest.
*   Survival Manual: Read the controls and objectives.
*   Debug Mode: Enter `forest` to skip the introduction, `ship` to skip both
    the introduction and forest, or press Enter for the full game. The ship
    start still requires both engine repairs; it is not a completed save.
*   Quit and Restart: Press X during gameplay, or use Ctrl+C during narration.
    To restart after an ending, run `python3 main.py` again in the container
    or use the same launch command you used locally.

If the terminal becomes too small, resize it to at least 80 by 24. Gameplay
may ask you to press Enter to resume. Narration uses Enter to advance and
Backspace to revisit earlier pages.

------------------------------------------------------
3. CONTROLS AND TURN RULES
------------------------------------------------------

In an interactive macOS, Linux, or Windows terminal, press WASD to move one
turn at a time. Menus and puzzle answers use Enter. If the game shows
`Enter your move:`, type the command and press Enter; for a Big Bang, enter
both letters together, such as `FW`.

*   W / A / S / D: Attempt to move up, left, down, or right.
*   F, then W / A / S / D: Fire a Big Bang in that direction.
*   T: Place a trap. Move off its tile to arm it.
*   E: Use an adjacent terminal or shop, or a control panel on or beside you.
*   H: Reopen the manual once it is unlocked.
*   X: Quit the current run.

A successful move, fired attack, or placed trap can advance enemy behaviour.
Blocked movement and invalid commands do not. Reopening help with H and
declining an exit confirmation do not advance enemy movement. Using E at the 
forest terminal or shop consumes an action after the menu closes, even if you 
leave the shop without buying anything. 
Read the prices before the creatures arrive.
Interactive UTF-8 terminals show ☺ for the player, with cyan on supported
macOS and Linux terminals. Plain terminals use @. Set `NO_COLOR=1` to request
plain ASCII. On macOS, Linux, or inside the course container:

```bash
NO_COLOR=1 python3 main.py
```

------------------------------------------------------
4. THE DUAL AI SYSTEM (GHOST VS. HUNTER)
------------------------------------------------------

You are being hunted by two distinct entities:

*   The Hunter (H): Pursues your exact current position using a shortest
    walkable path. It takes two steps when its path distance from you is
    greater than 8, and one step otherwise.
*   The Ghost (G): Scores positions along a possible route from you to the
    ship exit and tries to intercept you. It takes two steps when its path
    distance from you is greater than 4, and one step otherwise. At very
    close range it targets you directly.
*   The Grace Period: Enemies do not move during the first 8 forest enemy-turn
    updates. The eighth produces a warning; movement begins on the ninth.
    Invalid keys and blocked attempts do not use up this grace period.
*   Aboard the Ship: There is no new grace period once enemies are active.
    They update after qualifying main-deck actions. They do not move inside
    engine rooms or the reactor, or on the action that changes rooms.

Walls change the paths the creatures can take. They do not hide your position:
there is no line-of-sight or stealth-detection system. Use the maze to force
longer routes and create space for a trap or flash attack.

------------------------------------------------------
5. THE MAP AND THE ECONOMY
------------------------------------------------------

The forest is one playable maze. Its floor dots are hidden for a cleaner
view; the ship and its rooms display dots as walkable floor.

*   # Wall: Blocks movement and flash attacks. Space padding outside the
    ship is also blocked.
*   ? Help Terminal: Stand beside it and press E to unlock the in-game manual.
    Opening the Survival Manual from the main menu also unlocks the in-game manual.
*   $ Shop: Stand beside it and press E. The forest has two fixed shops,
    near the upper-right and lower-left parts of the map.
*   * Debris Coins: Walk over them to collect 10 coins.
*   > Forest Ship Exit: Attempt to enter it and confirm that you want to
    make a run towards the ship.
*   < Forest Secret Exit: The lower-left exit offers a trip deeper into
    the forest. In ship rooms, < instead returns you to the main deck.

You start with 100 battery, 3 Big Bang charges, 3 traps, and no coins.
Ordinary successful movement costs 1 battery until the upper engine restores
power. Placing a forest trap also costs 1 battery. Blocked movement, forest
exit transitions, and ship room transitions do not deduct that movement cost.
If battery reaches zero while the flashlight is required, the run ends.

*   Battery: 40 coins buys 50 battery. Only two battery purchases are allowed
    per run. The code does not cap battery at 100 after a purchase.
*   Traps: 20 coins buys one trap.
*   Big Bangs: 30 coins buys two charges.
*   Carry-Over: Battery, coins, carried traps, Big Bang charges, and the
    battery purchase count carry into the ship. Traps already placed in the
    forest do not follow you aboard.

A shop visit completes at most one purchase. Opening a menu does not make the
forest safe; the action can give the creatures another move when it closes.

------------------------------------------------------
6. COMBAT & DEFENSE
------------------------------------------------------

You have two defensive tools. Use them efficiently, as resources are limited.

*   Big Bangs: One charge fires a straight beam up to 4 walkable tiles.
    Obstacles stop the beam. An enemy in its path receives a stun counter
    of 5; the counter decreases when that enemy is processed on active
    enemy updates. Stunned creatures appear as lowercase g or h.
*   Traps: Place one at your current position and step off to arm it.
    An enemy entering an armed trap consumes it and receives a stun counter
    of 3. You cannot stack traps on the same tile. Trap placement costs
    battery in the forest, but not on the ship's main deck.
*   Placement Protection: On the action that places a trap, enemies cannot
    finish a movement step on your tile. They can still move elsewhere.
*   Collision: Walking onto an unstunned creature, or allowing a creature
    to reach you during its movement, ends the run.

Traps are available only on the main deck once aboard. The engine rooms and
reactor do not contain moving enemies. The trap-protection rule gives you a
moment to act; it does not stop the entire forest.

------------------------------------------------------
7. THE FINAL PHASE: THE SHIP
------------------------------------------------------

Confirm the forest's > exit to enter the crashed ship with your remaining
supplies. The ship is dark, and the engines need more than encouragement.

*   Upper Engine [1]: Enter the room at the top of the deck. Stand on or
    beside C and press E. Use the clues to put cooling, starter, and fuel
    pump connections in order. Its repair restores the lights and stops
    flashlight drain. Remember the starter's position.
*   Lower Engine [2]: Enter the room at the bottom of the deck. Balance
    three fuel valves using the starter position from the upper engine,
    their required total, and the relationship between the first two valves.
    You must repair the upper engine first.
*   Puzzle Feedback: Enter three digits, with optional spaces. X closes a
    panel. Incorrect valid settings produce progressive hints; malformed
    input asks you to enter the correct format. Closing a panel does not
    erase completed repairs.
*   Both Engines Online: The Ghost and Hunter board the main deck. Return
    through < and reach R on the left side of the ship. You can enter the
    reactor room earlier, but its controls require both completed repairs.
*   Reactor Choice: Stand on or beside C and press E. Attempting repair
    plays a fatal encounter, then returns you to the same decision with
    both engines still repaired. A second attempt earns an additional line
    of dialogue. Choosing to do nothing lets the reactor fail and ends the
    game in an explosion that destroys the ship, the creatures aboard,
    and much of the surrounding forest.

The two puzzles are connected by both a prerequisite and a clue: the upper
engine's result determines part of the lower engine's answer. The reactor
checkpoint keeps that completed work in memory. There is no disk save, and
restarting the program starts a new run.

The secret forest branch is separate from the reactor choices. It plays a
short glitch sequence, a false death, and a development-in-progress joke,
then displays restart instructions. There is no additional playable forest.

------------------------------------------------------
8. CODE ORGANISATION AND CHECKS
------------------------------------------------------

The modules separate the game's responsibilities:

*   `main.py`: Menu selection and progression between introduction, forest,
    and ship.
*   `state.py`: Shared resources, positions, and grid/path helpers.
*   `map_data.py`: Forest, main deck, two engine rooms, and reactor maps.
*   `alien_logic.py`: Pursuit, interception, pathfinding, stun, and capture.
*   `level_forest.py` / `level_ship.py`: Movement, actions, room changes,
    interactions, and level outcomes.
*   `engine_puzzles.py`: Linked puzzle clues, hints, and solution checks.
*   `turn_input.py`: Platform-specific turn input and paste handling.
*   `ui.py`: Map display, bounded panel input, dialogue, and resize checks.
*   `menus.py`: Main/debug menus, shop, manual, briefing, and confirmations.
*   `cinematics.py`: Narration pagination, timed frames, and ending animations.

From the project directory, perform a syntax check with:

```bash
python3 -m py_compile main.py state.py map_data.py alien_logic.py level_forest.py level_ship.py engine_puzzles.py turn_input.py ui.py menus.py cinematics.py
```

This checks Python syntax; it does not prove that gameplay or terminal output
is correct. Then launch `python3 main.py` in an 80 by 24 terminal and check:

1. Advance and revisit narration pages. Shrink the terminal, restore its size,
   and confirm that play resumes without losing the page.
2. Enter the forest. Try blocked movement, an invalid command, help, the shop,
   a flash attack, and a trap. Check resources before and after each action.
3. Decline both exits and try an invalid confirmation. Confirm that declining
   leaves the player in place without an extra enemy turn. Accept the secret
   exit on a separate run and check its ending and restart instructions.
4. Accept the ship exit and compare carried resources. Debug Mode → `ship`
   provides a quicker separate test of the engine and reactor sections.
5. Try the lower engine before the upper one. Check rejection, invalid puzzle
   input, wrong settings, progressive hints, cancellation, and both repairs.
   Verify that the upper engine stops battery drain and both engines activate
   the creatures on the main deck.
6. Reach the reactor, attempt repair twice, and check the checkpoint and
   repeated-death dialogue. Choose to do nothing and check the final sequence.
7. Repeat the final submission run in a fresh course v03 container offline.
   Restart by launching `main.py` again, rather than running a level module.

Recorded checks:

*   Louis's entries in `ai_use.md` report macOS, Windows, and Linux testing,
    an earlier integrated build replayed in the offline course v03 container,
    and a later ship-route check after the module split. Those results apply
    to the versions identified in that log.
*   Assistant-run checks on the latest uploaded modules passed syntax
    compilation, shortest-path cases, Hunter speed thresholds, forest grace,
    debug validation, help unlocking, and invalid-then-declined confirmation.
    Reactor checks covered two repair deaths, repeated dialogue, choosing
    to do nothing, and retained engine state.
*   All 8 narration pages and 36 cinematic frame calls were checked against
    the 72-column by 18-row text area inside the 80 by 24 screen. The pagination
    repair was also checked for text preservation, page navigation, and resize
    messages. These focused checks used isolated copies and simulated input;
    they were not a new full-game Windows or course Docker run.

The focused assistant checks were development checks outside the submitted
modules, not an installed test framework. The syntax command and manual steps
above are reproducible from the project itself.

------------------------------------------------------
9. KNOWN LIMITATIONS
------------------------------------------------------

*   Opening the manual from the main menu unlocks H before a forest terminal
    is visited. This follows the shared `open_terminal()` implementation.
*   Ship startup assigns `alien_logic.turn = 0`, while the active enemy counter
    is stored in `s["turn"]`. The assignment does not reset that counter.
    Ship enemy updates still bypass the forest grace period explicitly.
*   Some enemy warnings use interception language for the Hunter, although
    its actual target is the player's current position.
*   The secret ending intentionally stops at a development-in-progress message.
    There is no save/load system or automatic restart after an ending.
*   Terminal rendering depends on an interactive terminal with ANSI support.
    Redirected input uses a line-based fallback, and UTF-8 player display has
    an ASCII fallback. The latest cinematic changes were not natively retested
    on Windows in this review.

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

- Developed the Hunter's pursuit logic and fixed pre-existing bugs during
  development, using AI assistance to refine existing code.
- Developed the backstory and wrote, revised, and implemented the in-game
  dialogue. Added clearer feedback when obstacles block movement.
- Made initial UI changes that Louis later refined and improved.
- Added the debug menu and level entry points used during development.
- Implemented the forest exit confirmations and the secret ending.
- Implemented the reactor choices, repair-death checkpoint, repeated-attempt
  dialogue, and explosion ending with AI implementation and animation assistance.
- Added help-menu unlocking through terminal interaction and worked with AI
  to correct narration overflow through paragraph-aware pagination.

### Ahmed Habib

- Built the foundational movement and collision engine ([README.md](README.md)`open_tile`, wall/terminal 
  blocking, and tile state restoration) that the turn-based game runs on.
- Designed and hand-crafted the playable ASCII maps (`map_data.py`), iteratively 
  reshaping corridors, choke points, and looping paths so players can outmaneuver 
  stalkers using map geometry rather than luck.
- Created and coded the core combat and defense mechanics, including directional 
  "Big Bang" flash beam attacks, trap placement, step-off arming, trap recovery, and placement-turn protection.
- Led the gameplay iteration and balancing process: scrapped early unfun mechanics 
  (pressure plates, mirror puzzles, weapon heat bars, 4-tile fog-of-war, and starting with 50 coins) 
  and engineered the final debris coin (`*`) and two-shop (`$`) economy.
- Playtested and mathematically balanced battery drain and strategic shop coordinates 
  so players are forced to take calculated risks in the forest to survive up to Upper Engine 1
- Came up with Breadth-First Search (BFS) routing architecture which was implemented by Ahnaf, 
  and later added the 8-turn forest grace period and enemy stun timers.
- Designed the custom `BLACKOUT` ASCII main menu (`menus.py`), and executed the full architectural 
  refactoring from a monolithic file into the final 11-module structure
- Produced the complete demo including gameplay footage, explanation, explaining the code and 
  finally the AI reflection (which was compiled by everyone)

### Dai Tianqi
- Developed and integrated a complete in-game shop system in menu.py. Implemented the purchase process,
  coin management, and the application of purchased item effects during gameplay. Connected these components
  into a cohesive system, allowing players to spend their available coins on useful resources and benefit
  from their purchases. 
- Designed and implemented an informative status bar displaying remaining Flash uses, trap counts, and
  coin balance, helping players track resources and make strategic decisions.
- Established the foundation for the ship-based second level, developing the initial map and a three-room
  layout comprising engine rooms and a reactor room.
- Created the game’s ending animation and conducted compatibility testing, checking that the interface
  and animations fit within an 80 × 24 terminal display and testing execution in Docker.
- Produced the complete promotional trailer, combining gameplay footage, audio, and feature demonstrations
  to showcase the game’s core mechanics and atmosphere.

## Sources and acknowledgements

The project adapts the group's existing Python game through successive stages.
Its backstory, dialogue, enemy behaviour, linked puzzles, and ending choices
reflect the contributions above.

Generative AI assisted with design refinement, code, debugging, dialogue,
terminal animations, documentation, and code-explanation study materials.
[ai_use.md](ai_use.md) records the substantive uses, retained changes, and
checks. AI-generated output was adapted to the existing game and its terminal
constraints. The group remains responsible for understanding and checking it.

The supplied game uses Python's standard library and text-based artwork stored
in the source files.
