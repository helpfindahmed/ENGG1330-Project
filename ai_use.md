# AI Use

Generative AI used: Yes

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Design two linked engine repairs and integrate them into the existing
  ship level.
- Substantial parts affected: `engine_puzzles.py` and the engine interaction
  and instructions in `main.py`.
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
  movement input in `main.py`.
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
- Substantial parts affected: Engine panel interaction in `main.py`
  and console input in `turn_input.py`.
- What was kept and how it was checked: Kept the team's updated map, fixed-size
  panel renderer, and power restoration after the upper engine. Replayed both
  repairs in an 80 by 24 macOS terminal and checked hint progression, retry and
  reopen behavior, and flashlight drain before and after the first repair.
  Checked Windows command handling with simulated console input. The later entry records the
  native Windows console test on the updated build.

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Fix issues found in the pre-push review.
- Substantial parts affected: The ship display in `main.py`, the
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
  feedback in `main.py` and turn input in `turn_input.py`.
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
  the pre-refactor build from the opening through the reactor ending in a fresh
  container with networking disabled. All 191 captured forest and ship map
  frames fit 80 by 24. The run covered invalid input, terminal resizing,
  engine retries, and battery behavior after the upper engine repair.
  Clarified the opening's playable objective and corrected the README's
  grace-period and battery guidance. Rechecked the full revised build in
  the same offline course v03 container at 80 by 24.


## Entry

- Member and date: Hongkang Liu, 14 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Check that my engine puzzles and player guidance carried over into
  Blackout, and document my contributions using the repository history.
- Substantial parts affected: My contribution entry in `README.md` and this log.
- How results were checked: On macOS, started Blackout at the ship using the
  debug menu, repaired both engines, tested invalid input and progressive
  hints, and reached the reactor ending. All 136 captured gameplay screens
  in this run fit 80 columns by 24 rows.

## Entry

- Member and date: Syed Ahnaf Akif, 15 November 2026 (expanded retrospective
  record of work previously disclosed on 11 November 2026).
- Tool and model/version: OpenAI ChatGPT/Codex. Exact model versions were not recorded.
- Purpose: Refine my existing Hunter pursuit logic and assist with debugging.
- Substantial parts affected: Hunter behaviour in `alien_logic.py` and its
  supporting state and movement code, adapted from the earlier single-file game.
- What was kept, changed, or rejected: Developed the original Hunter logic
  and used AI to refine the implementation. Kept direct pursuit of the
  player's current position and shortest-path routing around obstacles.
  Required preservation of existing maps, resources, and unrelated mechanics.
- How results were checked: Reviewed source comparisons and integration changes.
  Later manual checks were performed for shortest-path detours, unreachable
  goals, identical start and goal, Hunter targeting, movement at distances
  8 and 9, and the eight-turn forest grace period.

## Entry

- Member and date: Syed Ahnaf Akif, 15 November 2026 (retrospective record).
- Tool and model/version: OpenAI ChatGPT/Codex. Exact model versions were not recorded.
- Purpose: Refine and implement my backstory, dialogue, obstacle feedback,
  help-menu unlocking, and cinematic presentation.
- Substantial parts affected: `cinematics.py`, `level_forest.py`,
  `level_ship.py`, `menus.py`, `state.py`, and shared display helpers in `ui.py`.
- What was kept, changed, or rejected: Developed the backstory and dialogue,
  personally revised the text, and used AI to help refine and integrate it.
  Rejected generic names, excessive exposition, and the typewriter effect.
  Used AI for the narration animations, including assistance with the final
  animated section. The current crash and warning use timed frames. Added obstacle feedback
  and help unlocking with AI assistance during implementation and review.
- How results were checked: Reviewed and revised the narrative drafts.
  AI inspected message branches and blocked-movement handling,
  and checked that opening the manual sets the help-unlocked flag. Review
  also identified that opening the manual from the main menu unlocks H.
  Cinematic size checks are recorded in the pagination entry below.

## Entry

- Member and date: Syed Ahnaf Akif, 15 November 2026 (retrospective record).
- Tool and model/version: OpenAI ChatGPT/Codex. Exact model versions were not recorded.
- Purpose: Create debug entry points and preserve shop positioning during changes.
- Substantial parts affected: `main.py`, `menus.py`, `state.py`, and
  `level_forest.py`.
- What was kept, changed, or rejected: Used AI assistance to create the debug
  menu and development checkpoints. Retained full-game, forest, and ship
  starts; these are level entry points rather than saved-game checkpoints.
  Used AI to help retain the shop's existing position during map updates.
- How results were checked: AI ran checks passed for invalid debug
  input, case-insensitive commands, and Enter selecting the full game.
  Reviewed the game-start branches and shop-coordinate restoration code.
  No new shop playtest was performed for this review.

## Entry

- Member and date: Syed Ahnaf Akif, 15 November 2026 (retrospective record).
- Tool and model/version: OpenAI ChatGPT/Codex. Exact model versions were not recorded.
- Purpose: Implement forest exit confirmations, the secret ending, and
  the reactor choices, checkpoint, and ending sequences.
- Substantial parts affected: `menus.py`, `level_forest.py`, `level_ship.py`,
  and `cinematics.py`, including their earlier single-file implementations.
- What was kept, changed, or rejected: Specified the exit and ending behaviour
  and used AI to assist with implementation. Kept Yes/No confirmations,
  the secret-ending glitch and joke, repair-death retries, retained engine
  progress, repeated-attempt dialogue, and the do-nothing explosion ending.
  Used AI for the reactor animations and other cinematic effects.
  Preserved the existing linked engine puzzles credited to Louis.
- How results were checked: Reviewed exit handling, reactor prerequisites,
  and the explosion call. AI ran checks confirmed that invalid
  confirmation followed by No leaves shared state unchanged. Reactor checks
  covered invalid input, two repair attempts, repeated-death dialogue, and
  choosing to do nothing; shared state and repaired-engine flags were retained.

## Entry

- Member and date: Syed Ahnaf Akif, 15 November 2026.
- Tool and model/version: OpenAI ChatGPT/Codex. Exact model version was not recorded.
- Purpose: Fix narration overflow and keep cinematics within an 80 by 24 terminal.
- Substantial parts affected: `intro_steps`, `intro_frame`, and `intro_story`
  in `cinematics.py`.
- What was kept, changed, or rejected: Supplied an error screenshot and
  requested that overflowing paragraphs move to another page. Kept the
  narration and story-event order. Used the AI-generated pagination fix
  to limit each text page to 18 rows and 72 columns and preserve Enter and
  Backspace navigation across pages and story sections.
- How results were checked: Manual checks were performed for syntax, unchanged
  narration, pagination without text loss, page navigation,
  invalid-key handling, and resize messages. All 8 narration pages 
  fitted the text area with room for the prompt.


## Entry

- Member and date: Syed Ahnaf Akif, 15 November 2026 (including documentation
  assistance from 14 November 2026).
- Tool and model/version: OpenAI ChatGPT/Codex. Exact model version was not recorded;
- Purpose: Compare versions, document contributions and AI use.
- Substantial parts affected: `README.md`, `ai_use.md`,
- What was kept, changed, or rejected: Used AI to organise my contribution
  account and document assistance.
  Kept the distinction between my original work, AI assistance, and
  teammates' contributions. Adapted this disclosure to the group's log format.
- How results were checked: The assistant reviewed the uploaded source and
  relevant earlier versions. All 11 latest Python modules passed syntax
  compilation. Focused behavioural checks are recorded above. Documentation
  was checked against my stated contributions and available evidence;
  known code limitations were reported without changing gameplay.
