# AI Use

Generative AI used: Yes

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Design two linked engine repairs and integrate them into the existing
  ship level.
- Substantial parts affected: `engine_puzzles.py` and the engine interaction
  and instructions in `movement_logic.py`.
- What was kept, changed, or rejected: Added relay ordering for Engine 1 and
  used its ignition slot as a fuel valve clue for Engine 2. Kept the team's
  ship maps, flashlight carryover, enemy activation and reactor ending.
  After player feedback, labelled the engine rooms by deck position and
  asked players to enter the three part numbers in order. Added retries
  inside both panels and explicit repair confirmation before returning.
  Added progressive hints that become more specific after wrong answers.
  Added persistent repair instructions on the map and let players use the
  console while standing on it or beside it.
  Added separate upper and lower engine status labels after player feedback.
- How results were checked: Enumerated relay orders and valve settings to
  verify each puzzle has one solution. Scripted the ship-level controls to
  test incorrect input, panel cancellation, the engine prerequisite, power
  restoration, and reaching the reactor ending. Tested the map hints and both
  console positions. Checked both panel sizes
  against 80 by 24. See the later entry for the course container replay.

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Prototype direct WASD input and integrate it after testing.
- Substantial parts affected: `direct_wasd_demo.py`, `turn_input.py` and the
  movement input in `movement_logic.py`.
- What was kept and how it was checked: Movement and flash attacks advance
  one command at a time. Text prompts still submit with Enter. Tested the
  separate demo in a macOS terminal session before integrating it. Replayed
  forest controls and both ship repairs through the new input and checked
  terminal restoration on exit and interruption.

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Integrate progressive hints with the team's new ship screens and
  add Windows single-key movement.
- Substantial parts affected: Engine panel interaction in `movement_logic.py`
  and console input in `turn_input.py`.
- What was kept and how it was checked: Kept the team's updated map, fixed-size
  panel renderer, and power restoration after the upper engine. Replayed both
  repairs in an 80 by 24 macOS terminal and checked hint progression, retry and
  reopen behavior, and flashlight drain before and after the first repair.
  Checked Windows command handling with simulated console input. A native
  Windows console test remains pending.

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Fix issues found in the pre-push review.
- Substantial parts affected: The ship display in `movement_logic.py`, the
  upper engine hint in `engine_puzzles.py`, and Escape handling in
  `turn_input.py`.
- How results were checked: Replayed both engine repairs, boarding enemies
  and the reactor ending on macOS and in the offline course Docker image.
  Checked all 115 ship map frames against 80 by 24. Verified on macOS that
  a move typed immediately after Escape still advances one turn.

## Entry

- Member and date: Hongkang Liu, 12 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Improve first-time player guidance and feedback on invalid input.
- Substantial parts affected: Briefings, objectives, map rendering, and panel
  feedback in `movement_logic.py` and turn input in `turn_input.py`.
- How results were checked: Played from the opening story to the reactor
  ending on macOS with colour enabled and disabled. All 191 forest and ship
  map frames in each run fit 80 by 24. Compared all five maps against the
  team version to verify the geometry. Tested blocked moves, invalid keys
  and aiming, oversized menu and puzzle input, bracketed paste at movement
  prompts, and shrinking and restoring the terminal mid-game.
  Verified the cyan player icon in VS Code's terminal renderer at 80 by 24
  and checked the ASCII fallback under simulated Windows, non-UTF-8, and
  redirected output.
  Repeated the terminal checks on Ubuntu and Windows GitHub-hosted runners
  using the same game files. Both passed at 80 by 24, including direct WASD,
  player-marker alignment, resizing, invalid actions, and both engine puzzles.
  Paste rejection was exercised on Linux.
  Enabled the one-cell smiley on Windows UTF-8 consoles and confirmed that
  both the smiley and the explicit ASCII fallback stay aligned on Windows
  and Ubuntu at 80 by 24.
  Rebuilt the course Docker v03 image from the provided bundle and replayed
  the current game from the opening through the reactor ending in a fresh
  container with networking disabled. All 191 captured forest and ship map
  frames fit 80 by 24. The run covered invalid input, terminal resizing,
  engine retries, and battery behavior after the upper engine repair.
  Clarified the opening's playable objective and corrected the README's
  grace-period and battery guidance. Rechecked the full revised build in
  the same offline course v03 container at 80 by 24.
