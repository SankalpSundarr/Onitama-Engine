"""Play as White against the Onitama engine in the terminal."""

import time

import numpy as np

from onitama_optimized import (
    CARD_NAMES, evaluate_position, get_index, get_legal_moves, is_terminal,
    make_move, minimax, pretty_print_board,
)

def square_to_coords(square):
    """Convert square number to chess notation (e.g., 0 -> 'A1')"""
    row = square // 5 + 1
    col = chr(ord('A') + square % 5)
    return f"{col}{row}"

def coords_to_square(coords):
    """Convert chess notation to square number (e.g., 'A1' -> 0)"""
    if len(coords) != 2:
        return -1
    col = coords[0].upper()
    row = coords[1]

    if col < 'A' or col > 'E' or row < '1' or row > '5':
        return -1

    return (int(row) - 1) * 5 + (ord(col) - ord('A'))

def display_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1):
    """Display all legal moves in a readable format"""
    moves, move_count = get_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1)

    if move_count == 0:
        print("No legal moves available!")
        return []

    print(f"\nLegal moves ({move_count} available):")
    move_list = []
    for i in range(move_count):
        move = moves[i]
        from_coords = square_to_coords(move[0])
        to_coords = square_to_coords(move[1])
        card_name = CARD_NAMES[move[2]]
        print(f"{i+1:2d}. {from_coords} -> {to_coords} using {card_name}")
        move_list.append((move[0], move[1], move[2]))

    return move_list

def get_human_move(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1):
    """Get a move from the human player"""
    while True:
        print("\nChoose your move:")
        print("1. Type move number from the list above")
        print("2. Type move in format 'from to card' (e.g., 'A1 B2 Tiger')")
        print("3. Type 'help' to see legal moves again")
        print("4. Type 'quit' to exit")

        user_input = input("> ").strip()

        if user_input.lower() == 'quit':
            return None

        if user_input.lower() == 'help':
            display_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1)
            continue

        # Get legal moves
        legal_moves = display_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1)

        # Try parsing as move number
        try:
            move_num = int(user_input)
            if 1 <= move_num <= len(legal_moves):
                move = legal_moves[move_num - 1]
                return np.array([move[0], move[1], move[2]], dtype=np.int64)
            else:
                print(f"Please enter a number between 1 and {len(legal_moves)}")
                continue
        except ValueError:
            pass

        # Try parsing as move string
        parts = user_input.split()
        if len(parts) == 3:
            from_coords, to_coords, card_name = parts
            from_sq = coords_to_square(from_coords)
            to_sq = coords_to_square(to_coords)

            # Find card index
            card_idx = -1
            for i, name in enumerate(CARD_NAMES):
                if name.lower() == card_name.lower():
                    card_idx = i
                    break

            if from_sq == -1 or to_sq == -1 or card_idx == -1:
                print("Invalid move format. Use format 'A1 B2 Tiger' or select from the numbered list.")
                continue

            # Check if move is legal
            for move in legal_moves:
                if move[0] == from_sq and move[1] == to_sq and move[2] == card_idx:
                    return np.array([from_sq, to_sq, card_idx], dtype=np.int64)

            print("That move is not legal!")
            continue

        print("Invalid input. Type 'help' for options.")

def setup_game():
    """Setup a new game"""
    print("Welcome to Onitama!")
    print("You play as White (uppercase letters), AI plays as Black (lowercase)")
    print("Goal: Capture the opponent's king or move your king to the temple (opposite starting position)")
    print()

    # Choose difficulty
    while True:
        print("Choose AI difficulty:")
        print("1. Easy (depth 4)")
        print("2. Medium (depth 6)")
        print("3. Hard (depth 8)")
        print("4. Expert (depth 10)")

        try:
            choice = int(input("> "))
            if choice == 1:
                ai_depth = 4
                break
            elif choice == 2:
                ai_depth = 6
                break
            elif choice == 3:
                ai_depth = 8
                break
            elif choice == 4:
                ai_depth = 10
                break
            else:
                print("Please choose 1-4")
        except ValueError:
            print("Please enter a number")

    # Setup initial position
    p1_bb = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)  # White pieces
    p2_bb = (1 << 20) | (1 << 21) | (1 << 22) | (1 << 23) | (1 << 24)  # Black pieces

    # Fixed opening cards, matching the demo.
    cards = ["Cobra", "Goose", "Elephant", "Frog", "Tiger"]
    cards = [get_index(c) for c in cards]

    p1_cards = np.array([cards[0], cards[1]], dtype=np.int64)
    p2_cards = np.array([cards[2], cards[3]], dtype=np.int64)
    extra_card = cards[4]

    wk_pos = 2  # White king starts at C1
    bk_pos = 22  # Black king starts at C5
    is_p1 = True  # Human plays as white (player 1)

    return p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, ai_depth

def main():
    """Main game loop"""
    p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, ai_depth = setup_game()

    move_number = 1

    while not is_terminal(p1_bb, p2_bb, wk_pos, bk_pos):
        print(f"\n{'='*60}")
        print(f"Move {move_number}")
        pretty_print_board(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)

        if is_p1:  # Human turn (White)
            # Display legal moves first
            legal_moves = display_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1)
            if not legal_moves:
                break

            move = get_human_move(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1)
            if move is None:  # User quit
                print("Thanks for playing!")
                return

            print(f"You played: {square_to_coords(move[0])} -> {square_to_coords(move[1])} using {CARD_NAMES[move[2]]}")

        else:  # AI turn
            print("AI is thinking...")
            start_time = time.time()
            score, move, node_count = minimax(p1_bb, p2_bb, p1_cards, p2_cards, extra_card,
                                      wk_pos, bk_pos, is_p1, ai_depth, -10000, 10000)
            end_time = time.time()

            if move[0] == -1:  # No valid moves
                break

            thought_time = end_time - start_time
            nps = node_count / thought_time if thought_time > 0 else float('inf')

            print(f"AI played: {square_to_coords(move[0])} -> {square_to_coords(move[1])} using {CARD_NAMES[move[2]]}")
            print(f"AI thought for {thought_time:.2f}s, searched {node_count:,} nodes "
                  f"(score: {score}), {nps:,.0f} nodes/s.")

        # Make the move
        p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos = make_move(
            p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, move)

        is_p1 = not is_p1
        move_number += 1

    # Game over
    print(f"\n{'='*60}")
    print("GAME OVER!")
    pretty_print_board(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)

    final_score = evaluate_position(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)
    if not is_terminal(p1_bb, p2_bb, wk_pos, bk_pos):
        print("Game stopped because no legal move was available. No winner is declared.")
    elif final_score > 0:
        print("Congratulations! You won!")
    else:
        print("AI wins! Better luck next time!")

    print(f"Game lasted {move_number - 1} moves.")

if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nThanks for playing!")
