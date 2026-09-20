import numpy as np
from numba import njit
import random
import time


def get_index(cn):
    for i,c in enumerate(CARD_NAMES):
        if c == cn:
            return i
# # Card definitions - convert to numpy arrays for numba
# CARD_OFFSETS = np.array([
#     [10, -5, 0, 0],      # Tiger
#     [-6, -4, 3, 7],      # Dragon  
#     [-2, 2, 5, 0],       # Crab
#     [-1, 1, 4, 6],       # Elephant
#     [-6, -4, 4, 6],      # Monkey
#     [-6, -4, 5, 0],      # Crane
#     [-1, 1, 5, 0],       # Boar
#     [2, -6, 6, 0],       # Frog
#     [-1, 1, -6, 6],      # Goose
#     [-5, 1, 5, 0],       # Horse
#     [4, 6, -5, 0],       # Mantis
#     [-5, -1, 5, 0],      # Ox
#     [-2, -4, 4, 0],      # Rabbit
#     [-1, 1, -4, 4],      # Rooster
#     [-1, 6, -4, 0],      # Eel
#     [1, 4, -6, 0]        # Cobra
# ], dtype=np.int8)

CARD_MOVE_COUNTS = np.array([2, 4, 3, 4, 4, 3, 3, 3, 4, 3, 3, 3, 3, 4, 3, 3], dtype=np.int64)

CARD_NAMES = ['Tiger', 'Dragon', 'Crab', 'Elephant', 'Monkey', 'Crane', 
              'Boar', 'Frog', 'Goose', 'Horse', 'Mantis', 'Ox', 
              'Rabbit', 'Rooster', 'Eel', 'Cobra']
CARD_OFFSETS = np.array([[(2, 0), (-1, 0), (0, 0), (0, 0)], 
        [(-1, -1), (-1, 1), (1, -2), (1, 2)], 
        [(0, -2), (0, 2), (1, 0), (0, 0)], 
        [(0, -1), (0, 1), (1, -1), (1, 1)], 
        [(-1, -1), (-1, 1), (1, -1), (1, 1)], 
        [(-1, -1), (-1, 1), (1, 0), (0, 0)], 
        [(0, -1), (0, 1), (1, 0), (0, 0)], 
        [(0, 2), (-1, -1), (1, 1), (0, 0)], 
        [(0, -1), (0, 1), (-1, -1), (1, 1)], 
        [(-1, 0), (0, 1), (1, 0), (0, 0)], 
        [(1, -1), (1, 1), (-1, 0), (0, 0)], 
        [(-1, 0), (0, -1), (1, 0), (0, 0)], 
        [(0, -2), (-1, 1), (1, -1), (0, 0)], 
        [(0, -1), (0, 1), (-1, 1), (1, -1)],
        [(0, -1), (-1, 1), (1, 1), (0, 0)],
        [(0, 1), (-1, -1), (1, -1), (0, 0),]], dtype = np.int64)

@njit
def get_possible_moves(card_idx, from_square, is_p1):
    """Get possible moves for a piece using a specific card"""
    moves = np.zeros(4, dtype=np.int64)
    move_count = 0
    
    r = from_square // 5
    c = from_square % 5
    
    factor = 1 if is_p1 else -1
    
    for i in range(CARD_MOVE_COUNTS[card_idx]):
        offset =  CARD_OFFSETS[card_idx, i]
        dr, dc = factor*offset[0], factor*offset[1]
        
        nr = r + dr
        nc = c + dc
        
        if 0 <= nr < 5 and 0 <= nc < 5:
            moves[move_count] = nr * 5 + nc
            move_count += 1
    
    return moves, move_count

@njit
def get_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1):
    """Generate all legal moves for current player"""
    moves = np.zeros((50, 3), dtype=np.int64)  # (from, to, card)
    move_count = 0
    
    if is_p1:
        our_bb = p1_bb
        opp_bb = p2_bb
        cards = p1_cards
        king_pos = wk_pos
    else:
        our_bb = p2_bb  
        opp_bb = p1_bb
        cards = p2_cards
        king_pos = bk_pos
    
    # For each piece
    for from_sq in range(25):
        if (our_bb >> from_sq) & 1:
            # Try both cards
            for card_idx in range(2):
                card = cards[card_idx]
                possible, count = get_possible_moves(card, from_sq, is_p1)
                
                for i in range(count):
                    to_sq = possible[i]
                    
                    # Can't capture own pieces
                    if (our_bb >> to_sq) & 1:
                        continue
                    
                    moves[move_count, 0] = from_sq
                    moves[move_count, 1] = to_sq
                    moves[move_count, 2] = card
                    move_count += 1
    
    return moves, move_count

@njit
def make_move(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, move):
    """Make a move and return new state + undo info"""
    from_sq, to_sq, card = move[0], move[1], move[2]
    
    if is_p1:
        our_bb = p1_bb
        opp_bb = p2_bb
        our_cards = p1_cards.copy()
        our_king_pos = wk_pos
        opp_king_pos = bk_pos
    else:
        our_bb = p2_bb
        opp_bb = p1_bb  
        our_cards = p2_cards.copy()
        our_king_pos = bk_pos
        opp_king_pos = wk_pos
    
    # Capture info for undo
    captured_piece = (opp_bb >> to_sq) & 1
    captured_king = (to_sq == opp_king_pos)
    
    # Update bitboards
    our_bb ^= (1 << from_sq)  # Remove from old position
    our_bb |= (1 << to_sq)    # Add to new position
    
    if captured_piece:
        opp_bb ^= (1 << to_sq)  # Remove captured piece
    
    # Update king positions
    if from_sq == our_king_pos:
        our_king_pos = to_sq
    if captured_king:
        opp_king_pos = -1
    
    # Handle card swap
    card_idx = 0 if card == our_cards[0] else 1
    old_card = our_cards[card_idx]
    our_cards[card_idx] = extra_card
    new_extra = old_card
    
    # Return new state
    if is_p1:
        new_p1_bb, new_p2_bb = our_bb, opp_bb
        new_p1_cards, new_p2_cards = our_cards, p2_cards
        new_wk_pos, new_bk_pos = our_king_pos, opp_king_pos
    else:
        new_p1_bb, new_p2_bb = opp_bb, our_bb
        new_p1_cards, new_p2_cards = p1_cards, our_cards
        new_wk_pos, new_bk_pos = opp_king_pos, our_king_pos
        
    return new_p1_bb, new_p2_bb, new_p1_cards, new_p2_cards, new_extra, new_wk_pos, new_bk_pos

@njit
def count_bits(bb):
    """Count set bits in bitboard"""
    count = 0
    while bb:
        bb &= bb - 1
        count += 1
    return count

@njit
def evaluate_position(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1):
    """Evaluate the current position"""
    # Check for terminal positions
    if wk_pos == 22:  # White king reaches temple
        return 2000
    if bk_pos == 2:   # Black king reaches temple  
        return -2000
    if wk_pos == -1:  # White king captured
        return -2000
    if bk_pos == -1:  # Black king captured
        return 2000
    
    # Material and mobility
    wp_count = count_bits(p1_bb)
    bp_count = count_bits(p2_bb)
    
    w_moves, w_count = get_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, True)
    b_moves, b_count = get_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, False)
    
    score = 100 * (wp_count - bp_count) + (w_count - b_count)
    
    # King safety
    for i in range(b_count):
        if b_moves[i, 1] == wk_pos:
            score -= 500
            break

    for i in range(w_count):
        if w_moves[i, 1] == bk_pos:
            score += 500
            break
    
    return score

@njit
def is_terminal(p1_bb, p2_bb, wk_pos, bk_pos):
    """Check if game is over"""
    return wk_pos == -1 or bk_pos == -1 or wk_pos == 22 or bk_pos == 2

@njit
def move_score_heuristic(p1_bb, p2_bb, wk_pos, bk_pos, is_p1, move):
    """Score move for ordering"""
    from_sq, to_sq, card = move[0], move[1], move[2]
    
    score = 0
    
    # Capturing moves
    if is_p1:
        if (p2_bb >> to_sq) & 1:
            if to_sq == bk_pos:
                score += 10000  # King capture
            else:
                score += 100    # Piece capture
        if from_sq == wk_pos and to_sq == 22:
            score += 10000  # Temple win
    else:
        if (p1_bb >> to_sq) & 1:
            if to_sq == wk_pos:
                score += 10000  # King capture  
            else:
                score += 100    # Piece capture
        if from_sq == bk_pos and to_sq == 2:
            score += 10000  # Temple win
    
    return score

@njit
def minimax(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, 
           depth, alpha, beta, node_count=1):
    """Minimax with alpha-beta pruning"""

    new_node_count = node_count

    if depth == 0 or is_terminal(p1_bb, p2_bb, wk_pos, bk_pos):
        score = evaluate_position(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)
        return score, np.array([-1, -1, -1], dtype=np.int64), new_node_count
    
    moves, move_count = get_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1)
    
    if move_count == 0:
        score = evaluate_position(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)
        return score, np.array([-1, -1, -1], dtype=np.int64), new_node_count
    
    # Sort moves by heuristic
    move_scores = np.zeros(move_count, dtype=np.int64)
    for i in range(move_count):
        move_scores[i] = move_score_heuristic(p1_bb, p2_bb, wk_pos, bk_pos, is_p1, moves[i])
    
    # Simple selection sort for numba
    for i in range(move_count - 1):
        max_idx = i
        for j in range(i + 1, move_count):
            if move_scores[j] > move_scores[max_idx]:
                max_idx = j
        if max_idx != i:
            # Swap scores
            move_scores[i], move_scores[max_idx] = move_scores[max_idx], move_scores[i]
            # Swap moves
            for k in range(3):
                moves[i, k], moves[max_idx, k] = moves[max_idx, k], moves[i, k]
    
    if is_p1:
        best_score = -10000
        best_move = np.array([-1, -1, -1], dtype=np.int64)
        
        for i in range(move_count):
            move = moves[i]
            new_p1_bb, new_p2_bb, new_p1_cards, new_p2_cards, new_extra, new_wk_pos, new_bk_pos = make_move(
                p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, move)
            
            score, _, new_node_count = minimax(new_p1_bb, new_p2_bb, new_p1_cards, new_p2_cards, new_extra, 
                              new_wk_pos, new_bk_pos, False, depth - 1, alpha, beta, new_node_count+1)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, best_score)
            if best_score >= beta:
                break
                
        return best_score, best_move, new_node_count
    else:
        best_score = 10000
        best_move = np.array([-1, -1, -1], dtype=np.int64)
        
        for i in range(move_count):
            move = moves[i]
            new_p1_bb, new_p2_bb, new_p1_cards, new_p2_cards, new_extra, new_wk_pos, new_bk_pos = make_move(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, move)
            
            score, _, new_node_count = minimax(new_p1_bb, new_p2_bb, new_p1_cards, new_p2_cards, new_extra,
                              new_wk_pos, new_bk_pos, True, depth - 1, alpha, beta, new_node_count+1)
            
            if score < best_score:
                best_score = score
                best_move = move
            
            beta = min(beta, best_score)
            if best_score <= alpha:
                break
                
        return best_score, best_move, new_node_count

def pretty_print_board(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1):
    """Pretty print the board state"""
    board = [[' ' for _ in range(5)] for _ in range(5)]
    
    # Place pieces
    for sq in range(25):
        r, c = sq // 5, sq % 5
        if (p1_bb >> sq) & 1:
            board[r][c] = 'K' if sq == wk_pos else 'P'
        elif (p2_bb >> sq) & 1:
            board[r][c] = 'k' if sq == bk_pos else 'p'
    
    # Print board
    horizontal_line = "   " + "+---" * 5 + "+"
    print(f"White cards: {CARD_NAMES[p1_cards[0]]} | {CARD_NAMES[p1_cards[1]]}")
    print("     A   B   C   D   E")
    
    for i in range(5):
        row_str = f"{i+1}  | " + " | ".join(board[i]) + " |"
        print(horizontal_line)
        if i == 2:
            print(row_str + f"   Extra: {CARD_NAMES[extra_card]}")
        else:
            print(row_str)
    
    print(horizontal_line)
    print("     A   B   C   D   E")
    print(f"Black cards: {CARD_NAMES[p2_cards[0]]} | {CARD_NAMES[p2_cards[1]]}")
    
    turn_str = "Player 1's turn (White)" if is_p1 else "Player 2's turn (Black)"
    print(f"   <-- {turn_str}")

def main():
    # Initialize game state
    p1_bb = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)
    p2_bb = (1 << 20) | (1 << 21) | (1 << 22) | (1 << 23) | (1 << 24)
    # cards = random.sample(range(16), 5)
    cards = ["Cobra", "Goose", "Elephant", "Frog", "Tiger"]

    def get_index(cn):
        for i,c in enumerate(CARD_NAMES):
            if c == cn:
                return i
    cards = [get_index(c) for c in cards]

    p1_cards = np.array([cards[0], cards[1]], dtype=np.int64)  # Tiger, Dragon
    p2_cards = np.array([cards[2], cards[3]], dtype=np.int64)  # Crab, Elephant
    extra_card = cards[4]  # Monkey
    wk_pos = 2
    bk_pos = 22
    is_p1 = True
    
    move_number = 0

    def depthf(move_number):
        if move_number <= 4: 
            return 6
        elif move_number <= 10:
            return 10
        return 12
    
    while not is_terminal(p1_bb, p2_bb, wk_pos, bk_pos):
        depth = 10 if move_number <= 4 else 12
        current_player = 1 if is_p1 else 2
        pretty_print_board(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)
        
        start_time = time.time()
        score, best_move, node_count = minimax(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, 
                                  wk_pos, bk_pos, is_p1, depth, -10000, 10000)
        end_time = time.time()
        thought_time = end_time - start_time
        if thought_time:
            nps = node_count/thought_time
        else:
            nps = float('inf')

        if best_move[0] == -1:  # No valid moves
            break
            
        # Make the move
        p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos = make_move(
            p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1, best_move)
        is_p1 = not is_p1
        
        print(f"Player {current_player} made move: from {best_move[0]} to {best_move[1]} using {CARD_NAMES[best_move[2]]}")
        print(f"Thought for {thought_time:.2f} seconds, score: {score}")
        print(f"It thought about {node_count} nodes at depth {depth}. It's NPS is {nps}")
        print(f"Current evaluation: {evaluate_position(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)}")
        print()
        
        move_number += 1
    
    print("Game Over!")
    pretty_print_board(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)
    final_score = evaluate_position(p1_bb, p2_bb, p1_cards, p2_cards, extra_card, wk_pos, bk_pos, is_p1)
    if final_score > 1000:
        print(f"White won! in {move_number} moves")
    elif final_score < -1000:
        print(f"Black won! in {move_number} moves")
    else:
        print("Draw")

if __name__ == "__main__":
    main()
