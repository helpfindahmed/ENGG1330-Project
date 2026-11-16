# AI Use

Generative AI used: Yes

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Design and integrate the two linked engine puzzles.
- Substantial parts affected: `engine_puzzles.py` and the original ship level.
- What was kept, changed, or rejected: Kept the linked relay and fuel puzzles, repair feedback and progressive hints.
- How results were checked: Checked unique solutions, panel size, retries and ship progression.

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Prototype single-key movement and flashlight controls.
- Substantial parts affected: `direct_wasd_demo.py`, `turn_input.py` and the original movement loop.
- What was kept, changed, or rejected: Kept one turn per action and Enter for typed answers.
- How results were checked: Tested movement, both engine repairs and terminal recovery on macOS.

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Integrate progressive hints and support Windows keyboard input.
- Substantial parts affected: Engine panels and `turn_input.py`.
- What was kept, changed, or rejected: Kept the ship layout and power-restoration rules during integration.
- How results were checked: Replayed both repairs on macOS and simulated Windows console input.

## Entry

- Member and date: Hongkang Liu, 11 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Fix display and input issues found in review.
- Substantial parts affected: Ship display, `engine_puzzles.py` and `turn_input.py`.
- What was kept, changed, or rejected: Adjusted the ship display, an engine hint and Escape handling.
- How results were checked: Replayed the ship route on macOS and in course Docker at 80 by 24.

## Entry

- Member and date: Hongkang Liu, 12 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Improve player guidance, map readability and invalid-input feedback.
- Substantial parts affected: Briefings, objectives, map rendering, README and `turn_input.py`.
- What was kept, changed, or rejected: Added clearer objectives and a player marker with an ASCII fallback.
- How results were checked: Tested controls on Windows, Ubuntu and macOS, and replayed the earlier build in offline course Docker.

## Entry

- Member and date: Hongkang Liu, 14 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Review Blackout after the module split and document my contributions.
- Substantial parts affected: `README.md` and `ai_use.md`.
- What was kept, changed, or rejected: Updated my contribution record and kept the existing game rules.
- How results were checked: Replayed both engine repairs and the reactor ending on macOS at 80 by 24.

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
  known code limitations were reported without changing gameplay.**

## Entry

- Member and date: Tianqi Dai, 9 November 2026.
- Tool and model/version, where available: OpenAI ChatGPT. Exact model
  version was not recorded.
- Purpose: Prototype a recognisable ship map using simple terminal
  characters.
- Relevant prompts and outputs used, or retained transcript location:
  In the conversation "Generating a Large Ship Map", requested:
  "Generate a 60 by 24 map using simple characters and make it resemble
  a large ship as closely as possible."
  Follow-up prompts included:
  "Add a visible outline of the ship's hull."
  "Change the dimensions to 60 by 18."
  ChatGPT supplied character-based ship layouts, including a revised
  60-column by 18-row version with a visible hull and ship features.
- Files/materials affected: The initial ship-map design and character-map
  data for Level 2.
- What we kept, changed or rejected: Kept the simple-character format and
  recognisable ship outline. Changed the requested dimensions from
  60 by 24 to 60 by 18 and requested a clearer ship-body outline.
- How we checked it; tests and corrections: Reviewed the proposed
  appearance and requested the hull and size revisions. ChatGPT described
  the generated maps as matching the requested dimensions. No independent
  row-by-row measurement log was retained for this design session.

## Entry

- Member and date: Tianqi Dai, 9 November 2026.
- Tool and model/version, where available: OpenAI ChatGPT. Exact model
  version was not recorded.
- Purpose: Establish the ship-level structure and connect it to the
  existing first level.
- Relevant prompts and outputs used, or retained transcript location:
  In the conversation "Branch: Generating a Large Ship Map", requested:
  "I have already added a Boolean named clear_level_1. It becomes True
  after the first level is completed. Use this to determine whether the
  player can enter Level 2, and keep everything else unchanged."
  Also requested:
  "Follow the structure of the first-level code. The puzzles in the three
  rooms do not need to be designed yet, but the room maps must load."
  ChatGPT supplied a Level 2 prototype containing the ship, upper engine
  room, lower engine room and reactor-room maps.
- Files/materials affected: The original ship-level Python implementation,
  room-map data and transition from Level 1 to Level 2. The final module
  names were not established in this session.
- What we kept, changed or rejected: Kept the existing clear_level_1 state
  and first-level structure. Requested working room entry and map loading
  while deferring room puzzles. This entry covers the level foundation,
  not the later linked engine puzzles developed by another member.
- How we checked it; tests and corrections: Subsequent gameplay
  observations exposed exit-handling and engine-progression issues.
  These were reported with screenshots and addressed in the next entry.
  No complete automated integration-test record was retained for the
  prototype.

## Entry

- Member and date: Tianqi Dai, 9 November 2026, with later manual checks
  reported retrospectively.
- Tool and model/version, where available: OpenAI ChatGPT. Exact model
  version was not recorded.
- Purpose: Add a character-based ship explosion animation after
  reactor activation.
- Relevant prompts and outputs used, or retained transcript location:
  In the conversation "Branch: Generating a Large Ship Map", requested:
  "Add a character-based animation of the ship exploding after the reactor
  is activated. Give me a version that I can copy and paste directly."
  ChatGPT supplied an explosion_animation() implementation and instructions
  for inserting its call after reactor activation.
- Files/materials affected: The prototype's ending-animation routine
  and reactor activation sequence.
- What we kept, changed or rejected: Used AI assistance for the requested
  character-animation implementation and its insertion point. This
  records assistance with the earlier prototype rather than claiming
  ownership of all subsequent reactor choices or ending revisions.
- How we checked it; tests and corrections: I later reported checking
  the game and animation against the 80 by 24 terminal requirement and
  testing execution inside Docker. Exact testing dates, container logs
  and individual pass/fail results were not recorded in this conversation.
  These were my reported checks, not tests independently run by ChatGPT.

## Entry

- Member and date: Tianqi Dai, 15 November 2026.
- Tool and model/version, where available: OpenAI ChatGPT. Exact model
  version was not recorded.
- Purpose: Help produce a promotional trailer introducing the game's
  functions and atmosphere.
- Relevant prompts and outputs used, or retained transcript location:
  In the conversation "Game Evaluation", requested assistance with
  trailer production and supplied this reference video:
  https://www.youtube.com/watch?v=KRvEFwHXm8s
  The follow-up request was:
  "Use the presentation style in this video as a reference, for example
  the introduction before the 'Set a trap' section."
  Outputs included BLACKOUT_Trailer_57s.mp4 and
  BLACKOUT_Voiceover_Guide.txt.
- Files/materials affected: The 57-second trailer, gameplay demonstrations,
  feature-introduction sequences, audio presentation and accompanying
  voiceover guide.
- What we kept, changed or rejected: Used AI assistance to develop the
  video and explain game functions through feature cards and gameplay
  demonstrations. The initial delivered version was described as
  including atmospheric audio without spoken narration. The voiceover
  guide was a separate output.
- How we checked it; tests and corrections: Reviewed the trailer's
  presentation and gameplay demonstrations. Identified incorrect trap
  placement and an unwanted character in the stun sequence, then
  requested the corrections recorded below. No separate audio-quality
  or encoding-test report was retained.

## Entry

- Member and date: Tianqi Dai, 15 November 2026.
- Tool and model/version, where available: OpenAI ChatGPT. Exact model
  version was not recorded.
- Purpose: Correct two gameplay inaccuracies in the trailer.
- Relevant prompts and outputs used, or retained transcript location:
  In the conversation "Game Evaluation", requested:
  "There is a problem in the 'Set a trap' section. You placed the trap
  to the player's left, but it should be placed under the player's feet
  and become active after the player moves away."
  Also requested:
  "In the 'Stun. Then Run!' section, there is an extra 'X' to the
  player's left. Remove it."
  ChatGPT returned a revised trailer and reported applying both
  corrections.
- Files/materials affected: The trap-placement and stun-demonstration
  sequences in BLACKOUT_Trailer_57s.mp4.
- What we kept, changed or rejected: Rejected the incorrect trap position
  and unwanted "X". Explicitly requested:
  "Only change these parts and keep everything else unchanged."
  The correction pass was therefore limited to those two sequences.
- How we checked it; tests and corrections: Compared the original
  demonstrations with the intended game mechanics and identified the
  two discrepancies through visual review. The assistant reported
  completing the revision. A separate final acceptance review was
  not recorded.

## Entry

- Member and date: Tianqi Dai, November 2026. 15 November, 2026.
- Tool and model/version, where available: OpenAI ChatGPT. Exact model
  version was not recorded.
- Purpose: Refine the trailer's flashcards and surrounding visual style.
- Relevant prompts and outputs used, or retained transcript location:
  In the conversation "Game Evaluation", uploaded
  "Black and White Minimalist Horror Mystery Presentation (1).png"
  and requested:
  "Remove the numerical labels from every flashcard and add animation
  effects. Use the uploaded image as the style reference."
  "Replace the first flashcard with the uploaded image and keep the
  remaining flashcard content unchanged."
  "Give the surrounding gameplay frame a similarly dark, mysterious
  and suspenseful style. I mean the outer frame, not the background
  of the central gameplay area."
- Files/materials affected: The trailer's opening card, subsequent
  flashcard presentation and outer gameplay frame, together with the
  uploaded reference image.
- What we kept, changed or rejected: Requested that the remaining
  flashcard content stay unchanged. Asked for a darker surrounding
  frame inspired by the reference while retaining the central gameplay
  background. Rejected the numbered flashcard presentation.
- How we checked it; tests and corrections: Used the uploaded image
  as the visual reference and gave explicit constraints on which
  areas could change. The available record confirms this request,
  but does not confirm a completed revision or final visual acceptance.

## Entry

- Member and date: Ahmed Habib, 15 November 2026 (retrospective record).
- Tool and model/version: Google Gemini. Exact model versions were not recorded.
- Purpose: Prototype initial stealth and puzzle concepts and establish the
  turn-based movement engine and map layouts.
- Substantial parts affected: `map_data.py`, `state.py`, `level_forest.py`,
  and `level_ship.py`, including their earlier `movement_logic.py` implementation.
- What was kept, changed, or rejected: Used AI to prototype early ideas, then
  rejected pressure-plate puzzles, mirror lasers, a weapon heat bar, a 4-tile
  fog-of-war radius, and starting with 50 coins after playtesting. Designed
  the custom forest and ship ASCII maps with looping corridors and choke
  points myself.
- How results were checked: Play tested the early prototype before discarding it.
  Manual checks were performed on all prototypes and a final game was decided 
  after discussing with teammates

## Entry

- Member and date: Ahmed Habib, 15 November 2026 (retrospective record).
- Tool and model/version: Google Gemini. Exact model versions were not recorded.
- Purpose: Implement directional Big Bang flash attacks, trap mechanics, the
  forest grace period, and enemy stun counters.
- Substantial parts affected: `level_forest.py`, `level_ship.py`, `state.py`,
  and `alien_logic.py`, including their earlier single-file implementations.
- What was kept, changed, or rejected: Selected Breadth-First Search (BFS) for
  enemy routing (implemented by Ahnaf). Added a wall check so flash beams stop at obstacles
  and prevented stacking multiple traps on the same tile. Debugging for trap logic, alongside
  flash fire.
- How results were checked: Manually tested firing Big Bangs into walls in all
  four directions, placing and recovering traps near enemies, and counting
  initial forest turns to confirm that blocked moves and invalid keys do not
  consume the grace period.

## Entry

- Member and date: Ahmed Habib, 15 November 2026 (retrospective record).
- Tool and model/version: Google Gemini. Exact model versions were not recorded.
- Purpose: Implement the supply shop interface, debris coin economy, and
  battery-drain balance.
- Substantial parts affected: `menus.py`, `map_data.py`, `state.py`,
  `level_forest.py`, and `level_ship.py`.
- What was kept, changed, or rejected: Designed the debris coin (`*`) and
  two-shop (`$`) economy, chose all shop and coin coordinates, and balanced
  battery drain so players must use the shop to survive until Upper Engine 1
  restores ship power. Used AI to assist with the `enter_shop` menu code and
  turn-update handling. Kept the two-purchase battery limit, supply carry-over
  to the ship, and the rule that closing a shop or terminal advances enemy
  movement.
- How results were checked: Replayed multiple forest routes to verify that
  reaching Upper Engine 1 requires collecting coins and visiting a shop,
  that supplies carry into the ship, and that creatures advance when the
  shop menu closes.

## Entry

- Member and date: Ahmed Habib, 15 November 2026.
- Tool and model/version: Google Gemini. Exact model version was not recorded.
- Purpose: Refactor the single-file codebase into 11 modules, update the
  `BLACKOUT` main menu and Docker configuration, and document contributions.
- Substantial parts affected: `main.py`, `state.py`, `level_forest.py`,
  `level_ship.py`, `ui.py`, `menus.py`, `Dockerfile`, `README.md`, and
  `ai_use.md`.
- What was kept, changed, or rejected: Planned the 11-module structure and
  designed the `BLACKOUT` ASCII title banner myself, rejecting an AI banner
  edit that broke character alignment. Used AI to help resolve circular
  imports through `state.py`, wrap the level loops into callable functions,
  fix the Level 2 `alien_stunned` list reset, update `Dockerfile` to run
  `main.py`, and format my contribution entries. Preserved the teammates'
  existing puzzles, pursuit logic, cinematics, and input handling.
- How results were checked: All 11 modules passed `python3 -m py_compile`.
  Rebuilt and ran the Docker container (`docker run --rm -it blackout-game`)
  and verified gameplay transitions from the main menu through the forest,
  ship engine repairs, and reactor ending.
## Entry

- Member and date: Hongkang Liu, 16 November 2026.
- Tool and model/version: OpenAI Codex. Exact model version was not recorded.
- Purpose: Refine the game after playtesting and make progression easier to follow.
- Substantial parts affected: `cinematics.py`, `menus.py`, `ui.py`, `turn_input.py`, `level_forest.py`, `alien_logic.py`, `level_ship.py`, `engine_puzzles.py` and README.
- What was kept, changed, or rejected: Shortened the opening, improved controls and forest balance, clarified the fuel puzzle, and revised the endings, death screens and mission-complete screen.
- How results were checked: Tested the full route, both reactor choices, the forest ending and invalid input on macOS. Ran the final gameplay ZIP offline in course Docker at 80 by 24.

- Final balance check: Restored the eight-turn forest grace period and verified
  a recharge route through both repairs and MISSION COMPLETE in course Docker.

- Resize follow-up: Made movement and aiming pause immediately below 80 by 24.
  Checked idle resize and recovery without consuming a turn on macOS, and
  simulated the Windows input path.
