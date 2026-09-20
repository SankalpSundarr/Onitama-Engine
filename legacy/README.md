# Earlier versions

These files are preserved from the original uploads for historical context.
The main program and API do not import them.

- `onitama_optimized_wonjit.py`: JIT decorators are commented out, but it still
  imports Numba. Its one-dimensional offset decoder is incorrect: for example,
  `-1` decodes to `(-1, -1)` instead of `(0, -1)`. It must not be used as a
  correctness reference or an equivalent non-JIT performance baseline until
  this and the remaining differences have been addressed.
- `Onitama_data.py`: an earlier 14-card dictionary. The active engine defines
  16 cards internally, including Eel and Cobra.
