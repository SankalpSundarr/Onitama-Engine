from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

# Import your bot
from onitama_optimized import minimax, get_legal_moves, CARD_NAMES

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_card_index(card_name):
    """Convert card name to index"""
    card_name_cap = card_name.capitalize()
    for i, name in enumerate(CARD_NAMES):
        if name == card_name_cap:
            return i
    raise ValueError(f"Unknown card: {card_name}")

def frontend_to_bitboards(board):
    """
    Convert frontend board to bitboards
    Frontend: 2D array with 'r'/'R' for red (row 0), 'b'/'B' for blue (row 4), None for empty
    Bot expects: p1 at bottom (squares 0-4), p2 at top (squares 20-24)
    So we need to flip: frontend row 0 -> bot row 4, frontend row 4 -> bot row 0
    """
    p1_bb = 0  # Blue pieces (player 1), initially at bot squares 0-4
    p2_bb = 0  # Red pieces (player 2), initially at bot squares 20-24
    wk_pos = -1  # Blue king position
    bk_pos = -1  # Red king position
    
    for row in range(5):
        for col in range(5):
            # Flip the board: frontend row 0 -> bot row 4, frontend row 4 -> bot row 0
            bot_row = 4 - row
            sq = bot_row * 5 + col
            piece = board[row][col]
            
            if piece:
                if piece.lower() == 'b':
                    p1_bb |= (1 << sq)
                    if piece == 'B':
                        wk_pos = sq
                elif piece.lower() == 'r':
                    p2_bb |= (1 << sq)
                    if piece == 'R':
                        bk_pos = sq
    
    return p1_bb, p2_bb, wk_pos, bk_pos

def square_to_coords(sq):
    """Convert square index to row, col (with board flip)"""
    sq = int(sq)  # Convert NumPy scalars to JSON-compatible Python integers.
    bot_row = sq // 5
    col = sq % 5
    # Flip back: bot row 0 -> frontend row 4, bot row 4 -> frontend row 0
    frontend_row = 4 - bot_row
    return frontend_row, col

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Onitama bot server is running'})

@app.route('/bot-move', methods=['POST'])
def get_bot_move():
    """
    Receive game state from frontend and return bot's best move
    """
    try:
        # Get game state from request
        game_state = request.json
        
        # Extract game state components
        board = game_state['board']
        current_player = game_state['currentPlayer']  # 'blue' or 'red'
        blue_cards = game_state['blueCards']
        red_cards = game_state['redCards']
        side_card = game_state['sideCard']
        
        # Convert board to bitboards
        p1_bb, p2_bb, wk_pos, bk_pos = frontend_to_bitboards(board)
        
        # Debug output
        print(f"\n=== Converting board for {current_player} ===")
        print(f"P1 (Blue) bitboard: {bin(p1_bb)}, king at: {wk_pos}")
        print(f"P2 (Red) bitboard: {bin(p2_bb)}, king at: {bk_pos}")
        
        # Convert card names to indices
        p1_cards = np.array([get_card_index(blue_cards[0]), get_card_index(blue_cards[1])], dtype=np.int64)
        p2_cards = np.array([get_card_index(red_cards[0]), get_card_index(red_cards[1])], dtype=np.int64)
        extra_card = get_card_index(side_card)
        
        print(f"Blue cards: {blue_cards} -> {p1_cards}")
        print(f"Red cards: {red_cards} -> {p2_cards}")
        print(f"Side card: {side_card} -> {extra_card}")
        
        # Determine if bot is player 1 (blue) or player 2 (red)
        is_p1 = (current_player == 'blue')
        
        # Set search depth (adjust based on game phase)
        depth = 8  # You can make this dynamic based on position
        
        # Get best move from bot
        print(f"Bot thinking for {current_player}...")
        score, best_move, node_count = minimax(
            p1_bb, p2_bb, p1_cards, p2_cards, extra_card,
            wk_pos, bk_pos, is_p1, depth, -10000, 10000
        )
        
        print(f"Bot evaluated {node_count} nodes, score: {score}")
        
        if best_move[0] == -1:
            return jsonify({'error': 'No valid moves available'}), 400
        
        # Convert move to frontend format
        from_row, from_col = square_to_coords(best_move[0])
        to_row, to_col = square_to_coords(best_move[1])
        card_name = CARD_NAMES[best_move[2]].lower()
        
        frontend_move = {
            'from': {'row': from_row, 'col': from_col},
            'to': {'row': to_row, 'col': to_col},
            'card': card_name
        }
        
        print(f"Bot move: {frontend_move}")
        
        return jsonify(frontend_move)
    
    except Exception as e:
        print(f"Error processing bot move: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/bot-info', methods=['GET'])
def bot_info():
    """
    Return information about the bot
    """
    return jsonify({
        'name': 'Onitama Minimax Bot',
        'version': '1.0',
        'algorithm': 'Minimax with Alpha-Beta Pruning',
        'description': 'Optimized Onitama bot using bitboards and numba JIT compilation'
    })

@app.route('/analyze', methods=['POST'])
def analyze_position():
    """
    Analyze a position and return evaluation and the best move
    """
    try:
        game_state = request.json
        board = game_state['board']
        current_player = game_state['currentPlayer']
        blue_cards = game_state['blueCards']
        red_cards = game_state['redCards']
        side_card = game_state['sideCard']
        
        # Convert to bot format
        p1_bb, p2_bb, wk_pos, bk_pos = frontend_to_bitboards(board)
        p1_cards = np.array([get_card_index(blue_cards[0]), get_card_index(blue_cards[1])], dtype=np.int64)
        p2_cards = np.array([get_card_index(red_cards[0]), get_card_index(red_cards[1])], dtype=np.int64)
        extra_card = get_card_index(side_card)
        is_p1 = (current_player == 'blue')
        
        # Get all legal moves
        moves, move_count = get_legal_moves(p1_bb, p2_bb, p1_cards, p2_cards, wk_pos, bk_pos, is_p1)
        
        # Analyze position
        depth = 6
        score, best_move, node_count = minimax(
            p1_bb, p2_bb, p1_cards, p2_cards, extra_card,
            wk_pos, bk_pos, is_p1, depth, -10000, 10000
        )
        
        frontend_move = None
        if best_move[0] != -1:
            from_row, from_col = square_to_coords(best_move[0])
            to_row, to_col = square_to_coords(best_move[1])
            frontend_move = {
                'from': {'row': from_row, 'col': from_col},
                'to': {'row': to_row, 'col': to_col},
                'card': CARD_NAMES[int(best_move[2])].lower()
            }

        return jsonify({
            'evaluation': int(score),
            'legal_moves': int(move_count),
            'nodes_searched': int(node_count),
            'best_move': frontend_move
        })
    
    except Exception as e:
        print(f"Error analyzing position: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Onitama Bot Server...")
    print("=" * 50)
    print("Server running on http://localhost:5000")
    print("\nEndpoints:")
    print("  - POST /bot-move    : Get bot's best move")
    print("  - POST /analyze     : Analyze current position")
    print("  - GET  /health      : Health check")
    print("  - GET  /bot-info    : Bot information")
    print("=" * 50)
    print("\nLocal API only. Check http://127.0.0.1:5000/health in your browser.")
    print("The bot will think for a few seconds before making moves.\n")
    
    app.run(debug=False, port=5000, host='127.0.0.1')