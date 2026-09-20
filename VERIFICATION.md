# Starter verification

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
