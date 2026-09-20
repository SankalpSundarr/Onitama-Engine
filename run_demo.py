"""Run a short, deterministic demo of the original Numba engine."""

import argparse
import platform
from time import perf_counter

import numba
import numpy as np

from onitama_optimized import (
    CARD_NAMES, evaluate_position, is_terminal, make_move, minimax,
    pretty_print_board,
)


def initial_state():
    """Same opening and five cards as the original main program."""
    cards = [CARD_NAMES.index(c) for c in
             ("Cobra", "Goose", "Elephant", "Frog", "Tiger")]
    return (31, 31 << 20,
            np.array(cards[:2], dtype=np.int64),
            np.array(cards[2:4], dtype=np.int64), cards[4], 2, 22)


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depth", type=positive_int, default=4,
                        help="search depth in plies (default: 4)")
    parser.add_argument("--plies", type=positive_int, default=1,
                        help="maximum number of moves to play (default: 1)")
    args = parser.parse_args()
    state = initial_state()
    is_p1 = True

    print(f"Python {platform.python_version()} | NumPy {np.__version__} | "
          f"Numba {numba.__version__}")
    print(f"Platform: {platform.platform()}")
    print("Warming up Numba; compilation can take a while...", flush=True)
    # Compile the directly called move function before later timed searches.
    _, warm_move, _ = minimax(*state, is_p1, 1, -10000, 10000)
    make_move(*state, is_p1, warm_move)
    print("Warm-up complete. Search timings below exclude the warm-up.")
    pretty_print_board(*state, is_p1)

    for ply in range(args.plies):
        start = perf_counter()
        score, move, nodes = minimax(*state, is_p1, args.depth, -10000, 10000)
        elapsed = perf_counter() - start
        nps = nodes / elapsed if elapsed else float("inf")
        if move[0] == -1:
            print("Engine returned no move. This is not automatically a draw.")
            break
        player = "White" if is_p1 else "Black"
        print(f"Move {ply + 1}: {player}, square {int(move[0])} -> "
              f"{int(move[1])}, {CARD_NAMES[int(move[2])]}")
        print(f"depth={args.depth} score={score} nodes={nodes:,} "
              f"seconds={elapsed:.6f} nodes_per_second={nps:,.0f}")
        state = make_move(*state, is_p1, move)
        is_p1 = not is_p1
        pretty_print_board(*state, is_p1)
        if is_terminal(state[0], state[1], state[5], state[6]):
            score = evaluate_position(*state, is_p1)
            print("White wins." if score > 0 else "Black wins.")
            break
    else:
        print("Demo move limit reached; no game result is implied.")


if __name__ == "__main__":
    main()
