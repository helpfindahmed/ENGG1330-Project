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
  Added persistent repair instructions on the map and let players use the
  console while standing on it or beside it.
  Added separate upper and lower engine status labels after player feedback.
- How results were checked: Enumerated relay orders and valve settings to
  verify each puzzle has one solution. Scripted the ship-level controls to
  test incorrect input, panel cancellation, the engine prerequisite, power
  restoration, and reaching the reactor ending. Tested the map hints and both
  console positions. Checked both panel sizes
  against 80 by 24. The full game and course container still need verification.

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
