# Onitama Engine

A Python Onitama engine by Sankalp Sundar, using integer bitboards,
Numba compilation, and minimax search with alpha-beta pruning.

## Implemented features

- Two 25-square bitboards plus explicit master positions.
- Card-based move generation, captures, and card exchange.
- Master capture and temple victory detection.
- Alpha-beta minimax with capture and immediate-win move ordering.
- Static evaluation using material, mobility, and master threats.
- Search node counts and elapsed-time reporting.
- Interactive terminal play against the AI, with four difficulty levels.
- A local Flask API for requesting moves and evaluating positions.

## Quick start: Windows PowerShell

Use a 64-bit Python installation. Python 3.12 is the setup target below.
Open PowerShell in this folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_demo.py --depth 4 --plies 1
```

The first run compiles the engine before reporting search timing. The demo
prints the board, a selected move, score, searched nodes, elapsed time, and
nodes per second. The environment does not need to be activated.

For a longer self-play demo:

```powershell
.\.venv\Scripts\python.exe run_demo.py --depth 6 --plies 20
```

The move limit stops the demonstration without declaring a draw. Higher depths
can take much longer; the engine has no time limit. Ctrl+C stops the program.

On macOS/Linux, create an environment with `python3 -m venv .venv`, then use
`.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.

## Play against the AI

After installing the dependencies above, run:

```powershell
.\.venv\Scripts\python.exe play_onitama.py
```

You play White and move first; the AI plays Black. Choose Easy (depth 4),
Medium (6), Hard (8), or Expert (10). By design, the AI uses depth 8 during
the first 10 moves (counting both players' moves), then switches to your
selected depth. Even Easy therefore searches at depth 8 in the opening.
Higher depths can take much longer, with no search deadline.
The first turn also needs time for Numba compilation; the first AI
timing includes any remaining search compilation.

- Choose a move by its number in the displayed legal-move list, or enter
  `from to card`, such as `A1 B2 Tiger` (format example; the move must be legal).
- Coordinates run from `A1` to `E5`, matching the printed board. Coordinates
  and card names are case-insensitive.
- Enter `help` to show legal moves again, or `quit` at a move prompt to exit.
  Ctrl+C also exits.
- Your master is `K` and your students are `P`; the AI uses `k` and `p`.
  Capture the opposing master or move your master from `C1` to the temple at
  `C5` to win. The AI's target temple is `C1`.

Each game starts with the same cards: White has Cobra and Goose, Black has
Elephant and Frog, and Tiger is the side card. The used card is exchanged
with the side card after each move. If a player has no legal move, the game
stops without declaring a winner; pass-and-card-exchange is not implemented.

## Local API

```powershell
.\.venv\Scripts\python.exe backend.py
```

Visit <http://127.0.0.1:5000/health> for a JSON status response.
This is an API; no browser game interface is included. A request to `/` is
not a game page. The development server binds to the local machine.

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Server status |
| `GET /bot-info` | Engine information |
| `POST /bot-move` | Best move, search depth 8 |
| `POST /analyze` | Score, move count, nodes, and best move, depth 6 |

Both POST routes expect `board`, `currentPlayer`, `blueCards`, `redCards`,
and `sideCard`. The board is a 5-by-5 JSON array. Empty squares are `null`;
`b`/`r` are students, and `B`/`R` are masters. Blue starts at frontend row 4,
red at row 0. Card names are case-insensitive. `currentPlayer` is `blue` or
`red`. Returned coordinates are zero-based frontend row/column coordinates.
Evaluation is from Blue/White's perspective; positive scores favor Blue.
The first search request also incurs JIT compilation time.

## Source files

| File | Purpose |
| --- | --- |
| `onitama_optimized.py` | Original main engine |
| `run_demo.py` | Configurable, bounded demo with JIT warm-up |
| `play_onitama.py` | Human-versus-AI terminal game with difficulty selection |
| `backend.py` | Local Flask API with coordinate and JSON fixes |
| `requirements.txt` | Dependencies installed by pip |
| `legacy/` | Earlier files retained for historical context |

`python onitama_optimized.py` runs the original self-play loop at depth 10,
then 12. Use `run_demo.py` for a quick first run.

## Scope and limitations

This is a research/prototype engine. A complete rules audit has not been
performed. In particular, the current search ends the branch when it generates
zero moves; no pass-and-card-exchange transition is implemented. Card diagrams
should also be checked against the intended game edition before competitive
use. There is no repetition adjudication, search deadline, transposition table,
iterative deepening, or quiescence search in this version.

The API assumes well-formed game states and is intended for local development.
It is not a production deployment configuration. GitHub hosts the repository;
running this Flask/Python engine on a public website needs a separate service.

## Performance

The demo counts search nodes, including internal nodes. This is not the number
of calls to the static evaluation function. Timings exclude the warm-up search.
Measure several positions and report the CPU, Python/Numba/NumPy versions,
depth, node count, and elapsed time alongside throughput. A one-move demo is
a smoke check, not a full performance study.

## Starter packaging changes

- The core engine is copied from the supplied Numba implementation.
- Added `run_demo.py`, dependency instructions, and Git ignore settings.
- Added `play_onitama.py` for interactive terminal games against the AI.
- Both API routes now use the same frontend coordinate conversion.
- Coordinate outputs are converted to Python integers for JSON serialization.
- `/analyze` returns `best_move: null` when no move is returned by the engine.
- The development server uses localhost with debug mode disabled.
- Earlier implementations are retained under `legacy/`, with their limitations
  documented there.

See `SETUP_WINDOWS.md` for publishing the repository on GitHub.
