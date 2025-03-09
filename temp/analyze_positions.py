#!/usr/bin/env python
"""
Script to analyze multiple Hexapawn positions using the tablebase.

This script creates different Hexapawn positions and uses the tablebase
to evaluate them and find the best moves.
"""
import sys
import os
from pathlib import Path

# Add project root to path if running from temp directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.hexapawn import Hexapawn
from tablebase import EndgameTablebase

# Use the same fixed seed as in build_hexapawn_full.py
FIXED_SEED = 42

def setup_position(initial_moves):
    """Set up a specific position by making a sequence of moves from the initial position."""
    game = Hexapawn(zobristSeed=FIXED_SEED)
    
    # Make the specified moves
    for move in initial_moves:
        game.make_move(move)
    
    return game

def render_board(game):
    """Render the Hexapawn board with a readable format."""
    # Print top border
    print("  " + "-" * (game.sizeJ * 3 + 1))
    
    # Print board
    for i in range(game.sizeI):
        print(f"{i} |", end="")
        for j in range(game.sizeJ):
            if game.bm.isPieceSet('1', i, j):
                print(" 1 ", end="")
            elif game.bm.isPieceSet('2', i, j):
                print(" 2 ", end="")
            else:
                print("   ", end="")
        print("|")
    
    # Print bottom border
    print("  " + "-" * (game.sizeJ * 3 + 1))
    
    # Print column coordinates
    print("  ", end="")
    for j in range(game.sizeJ):
        print(f" {j} ", end="")
    print()

def analyze_position(game, tablebase, position_name):
    """Analyze a position using the tablebase."""
    print(f"\n=== Position: {position_name} ===")
    print(f"Current player: {game.current_player}")
    render_board(game)
    
    # Get position hash
    position_hash = game.hash()
    print(f"Position hash: {position_hash}")
    
    # Check if position is in tablebase
    position_info = tablebase.get_position_info(position_hash)
    if position_info:
        print("\nPosition found in tablebase:")
        print(f"Value: {position_info['value']}")
        print(f"Depth to terminal: {position_info['depth_to_terminal']}")
        terminal_status = "Yes" if position_info['is_terminal'] else "No"
        print(f"Is terminal: {terminal_status}")
        
        # Interpret the value
        if position_info['is_terminal']:
            if position_info['value'] == 1.0:
                print("Result: Player 1 wins")
            elif position_info['value'] == -1.0:
                print("Result: Player 2 wins")
            else:
                print("Result: Draw")
        else:
            if game.current_player == '1':
                if position_info['value'] == 1.0:
                    print("Evaluation: Player 1 can force a win")
                elif position_info['value'] == -1.0:
                    print("Evaluation: Player 2 can force a win")
                else:
                    print("Evaluation: Draw with best play")
            else:  # player 2's turn
                if position_info['value'] == 1.0:
                    print("Evaluation: Player 1 can force a win")
                elif position_info['value'] == -1.0:
                    print("Evaluation: Player 2 can force a win")
                else:
                    print("Evaluation: Draw with best play")
        
        # Get and display best move
        best_move = tablebase.get_best_move(game)
        if best_move:
            _, from_i, from_j, to_i, to_j = best_move
            print(f"\nBest move: ({from_i},{from_j}) to ({to_i},{to_j})")
        else:
            print("\nNo best move found (terminal position or not in tablebase)")
    else:
        print("\nPosition NOT found in tablebase!")

def analyze_positions():
    """Analyze multiple Hexapawn positions using the tablebase."""
    # Path to the database file
    db_path = "hexapawn_complete.duckdb"
    
    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} not found!")
        print("Please run build_hexapawn_full.py first.")
        return
    
    print(f"Loading tablebase from: {db_path}")
    tablebase = EndgameTablebase(db_path=db_path)
    
    # Define positions to analyze
    positions = [
        {
            "name": "Initial position",
            "moves": []
        },
        {
            "name": "After first move (P1 left pawn forward)",
            "moves": [('1', 2, 0, 1, 0)]
        },
        {
            "name": "P1 about to win",
            "moves": [
                ('1', 2, 0, 1, 0),  # P1 moves left pawn up
                ('2', 0, 1, 1, 1),  # P2 moves middle pawn to capture
                ('1', 2, 2, 1, 2),  # P1 moves right pawn up
                ('2', 0, 0, 1, 0),  # P2 moves left pawn to block
            ]
        },
        {
            "name": "P2 about to win",
            "moves": [
                ('1', 2, 1, 1, 1),  # P1 moves middle pawn up
                ('2', 0, 0, 1, 0),  # P2 moves left pawn down
                ('1', 2, 2, 1, 2),  # P1 moves right pawn up
                ('2', 0, 2, 1, 1),  # P2 captures with right pawn
            ]
        }
    ]
    
    # Analyze each position
    for position in positions:
        game = setup_position(position["moves"])
        analyze_position(game, tablebase, position["name"])
    
    # Close the database connection
    tablebase.close()
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    analyze_positions() 