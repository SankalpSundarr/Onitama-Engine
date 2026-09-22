# Verification

## Terminal game update

Checked on Windows with Python 3.12, NumPy 2.5.3, and Numba 0.67.0:

- Before restoring the intended opening depth, an interactive smoke run with
  scripted input completed a human White move, a real Numba depth-4 Black AI
  response, and a clean quit.
- Help, invalid text, and out-of-range move numbers are handled.
- All 25 square coordinates round-trip, including lowercase input; invalid
  coordinates are rejected.
- All four difficulty choices select the documented depths. After restoring
  the opening policy, controlled game-loop checks with search stubbed confirm
  depth 8 for AI turns through move 10 and the selected depth from move 12
  (the next AI turn), for all four difficulty choices.
- A controlled no-legal-move case stops without declaring a winner and
  reports zero completed moves.

This is a smoke check, not a full game-rules audit or performance benchmark.

## Original archive verification

Checked while preparing this archive:

- All Python files parse successfully.
- The active core engine is byte-for-byte identical to the supplied Numba file.
- With JIT decorators removed in memory, a depth-3 opening search returns a
  generated legal move. Applying it preserves disjoint bitboards and the five
  cards in circulation.
- Response-format checks with controlled search outputs confirm matching
  frontend coordinates from both routes, JSON-compatible coordinate integers,
  and `best_move: null` for an absent move in `/analyze`.
- The demo completes a short two-move run with JIT replaced in memory by an
  identity decorator; this checks its Python control flow only.

Numba and Flask were unavailable in the preparation environment, and their
installation could not be completed there. No compiled Numba run, actual Flask
HTTP integration test, Windows installation test, or performance benchmark is
claimed. Run the quick-start demo and local API checks on your machine.
