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
  Clarified Engine 1's relay labels, slots and input after player feedback.
- How results were checked: Enumerated relay orders and valve settings to
  verify each puzzle has one solution. Scripted the ship-level controls to
  test incorrect input, panel cancellation, the engine prerequisite, power
  restoration, and reaching the reactor ending. Checked both panel sizes
  against 80 by 24. The full game and course container still need verification.
