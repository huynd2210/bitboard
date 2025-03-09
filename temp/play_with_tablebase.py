#!/usr/bin/env python
"""
Script to play a game of Hexapawn against the tablebase.
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path if running from temp directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.hexapawn import Hexapawn
from tablebase import EndgameTablebase

def play_with_tablebase():
    """Play a game of Hexapawn against the tablebase."""
    db_path = "hexapawn_endgame.duckdb"
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Tablebase {db_path} not found.")
        print("Please run test_endgame_tablebase.py first to create the tablebase.")
        sys.exit(1)
    
    # Connect to the tablebase
    tablebase = EndgameTablebase(db_path=db_path)
    print(f"Connected to tablebase: {db_path}")
    
    # Create a new game
    game = Hexapawn()
    
    # Print initial state
    print("\nInitial board position:")
    game.render()
    
    # Play the game until it's over
    move_count = 0
    while not game.is_over():
        move_count += 1
        print(f"\nMove {move_count}:")
        print(f"Player {game.current_player}'s turn")
        
        # For player 1 (human)
        if game.current_player == '1':
            # Get legal moves
            legal_moves = game.get_legal_moves()
            print("\nLegal moves:")
            for i, move in enumerate(legal_moves):
                print(f"{i}: {move}")
            
            # Get human input
            try:
                choice = int(input("Enter move number (or -1 for tablebase move): "))
                if choice == -1:
                    # Use tablebase move
                    move = tablebase.get_best_move(game)
                    if not move:
                        print("No tablebase move found, using random move")
                        move = legal_moves[0]
                else:
                    # Use human-selected move
                    move = legal_moves[choice]
            except (ValueError, IndexError):
                print("Invalid choice, using first legal move")
                move = legal_moves[0]
        
        # For player 2 (tablebase)
        else:
            print("\nAI is thinking...")
            time.sleep(1)  # Simulate thinking
            
            # Try to get move from tablebase
            move = tablebase.get_best_move(game)
            
            if move:
                print(f"AI plays tablebase move: {move}")
            else:
                # Fallback to random move
                legal_moves = game.get_legal_moves()
                move = legal_moves[0]
                print(f"AI plays random move (no tablebase entry): {move}")
        
        # Make the move
        game.make_move(move)
        
        # Print the new state
        print("\nBoard after move:")
        game.render()
    
    # Game over
    print("\nGame over!")
    if game.winner:
        print(f"Player {game.winner} wins!")
    else:
        print("Draw!")
    
    # Close the tablebase
    tablebase.close()

if __name__ == "__main__":
    play_with_tablebase() 