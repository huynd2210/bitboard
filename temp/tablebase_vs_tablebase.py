#!/usr/bin/env python
"""
Script that simulates a perfect game of Hexapawn where both players
use the tablebase to make optimal moves.

This demonstrates perfect play and verifies the tablebase works correctly.
"""
import sys
import os
import time
from pathlib import Path

# Add project root to path if running from temp directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.hexapawn import Hexapawn
from tablebase import EndgameTablebase

# Use the same fixed seed as in build_hexapawn_full.py
FIXED_SEED = 42

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

def get_position_evaluation(game, tablebase):
    """Get evaluation of the current position from the tablebase."""
    position_hash = game.hash()
    position_info = tablebase.get_position_info(position_hash)
    
    if position_info:
        evaluation = ""
        if position_info['is_terminal']:
            if position_info['value'] == 1.0:
                evaluation = "Player 1 wins"
            elif position_info['value'] == -1.0:
                evaluation = "Player 2 wins"
            else:
                evaluation = "Draw"
        else:
            if position_info['value'] == 1.0:
                evaluation = "Player 1 can force a win"
            elif position_info['value'] == -1.0:
                evaluation = "Player 2 can force a win"
            else:
                evaluation = "Draw with perfect play"
                
        return {
            "value": position_info['value'],
            "depth": position_info['depth_to_terminal'],
            "evaluation": evaluation
        }
    
    return None

def simulate_perfect_game():
    """Simulate a perfect game where both players use the tablebase."""
    # Path to the database file
    db_path = "hexapawn_complete.duckdb"
    
    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} not found!")
        print("Please run build_hexapawn_full.py first.")
        return
    
    print(f"Loading tablebase from: {db_path}")
    tablebase = EndgameTablebase(db_path=db_path)
    
    # Create a new game
    game = Hexapawn(zobristSeed=FIXED_SEED)
    
    print("\n=== PERFECT HEXAPAWN GAME ===")
    print("Both players will make the perfect move according to the tablebase.")
    print("Game starts with Player 1 (bottom pawns).")
    
    # Game loop
    move_number = 1
    
    while not game.is_over():
        print("\n" + "=" * 40)
        print(f"Move {move_number}")
        print(f"Player {game.current_player}'s turn")
        
        # Get position evaluation
        evaluation = get_position_evaluation(game, tablebase)
        if evaluation:
            print(f"Position evaluation: {evaluation['evaluation']}")
            print(f"Value: {evaluation['value']}")
            print(f"Moves to terminal: {evaluation['depth']}")
        
        # Display the current board
        render_board(game)
        
        # Get the best move from the tablebase
        best_move = tablebase.get_best_move(game)
        
        if best_move:
            # Parse the move
            _, from_i, from_j, to_i, to_j = best_move
            print(f"Best move: ({from_i},{from_j}) to ({to_i},{to_j})")
            
            # Make the move
            game.make_move(best_move)
            
            # Increment move counter
            move_number += 1
            
            # Add a small delay for readability
            time.sleep(1)
        else:
            print("No best move found! This shouldn't happen with a complete tablebase.")
            break
    
    # Game over
    print("\n" + "=" * 40)
    print("GAME OVER")
    render_board(game)
    
    if game.winner:
        print(f"Player {game.winner} wins!")
    else:
        print("The game ended in a draw.")
    
    # Close the database connection
    tablebase.close()
    
    print("\nPerfect game simulation complete!")

def simulate_multiple_perfect_games():
    """Simulate multiple perfect games with different starting moves."""
    # Path to the database file
    db_path = "hexapawn_complete.duckdb"
    
    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} not found!")
        print("Please run build_hexapawn_full.py first.")
        return
    
    print(f"Loading tablebase from: {db_path}")
    tablebase = EndgameTablebase(db_path=db_path)
    
    # Create a new game for initial moves
    initial_game = Hexapawn(zobristSeed=FIXED_SEED)
    
    # Get all legal first moves
    first_moves = initial_game.get_legal_moves()
    
    print(f"\nFound {len(first_moves)} possible first moves.")
    print("Simulating a perfect game for each first move.\n")
    
    # Simulate a perfect game for each possible first move
    for i, first_move in enumerate(first_moves):
        # Create a new game
        game = Hexapawn(zobristSeed=FIXED_SEED)
        
        # Make the first move
        _, from_i, from_j, to_i, to_j = first_move
        print(f"\n{'=' * 60}")
        print(f"GAME {i+1}: First move: ({from_i},{from_j}) to ({to_i},{to_j})")
        
        # Make the first move
        game.make_move(first_move)
        
        # Simulate the rest of the game
        move_number = 2  # We've already made move 1
        
        while not game.is_over():
            print(f"\nMove {move_number}")
            print(f"Player {game.current_player}'s turn")
            
            # Get the best move from the tablebase
            best_move = tablebase.get_best_move(game)
            
            if best_move:
                # Parse the move
                _, from_i, from_j, to_i, to_j = best_move
                print(f"Best move: ({from_i},{from_j}) to ({to_i},{to_j})")
                
                # Make the move
                game.make_move(best_move)
                
                # Increment move counter
                move_number += 1
            else:
                print("No best move found! This shouldn't happen with a complete tablebase.")
                break
        
        # Game over
        print("\nGAME OVER")
        render_board(game)
        
        if game.winner:
            print(f"Player {game.winner} wins!")
        else:
            print("The game ended in a draw.")
    
    # Close the database connection
    tablebase.close()
    
    print("\nAll perfect game simulations complete!")

if __name__ == "__main__":
    # Ask user which simulation to run
    print("Choose a simulation mode:")
    print("1. Single perfect game")
    print("2. Multiple perfect games (one for each possible first move)")
    
    choice = input("Enter your choice (1/2): ").strip()
    
    if choice == "1":
        simulate_perfect_game()
    elif choice == "2":
        simulate_multiple_perfect_games()
    else:
        print("Invalid choice. Please enter 1 or 2.") 