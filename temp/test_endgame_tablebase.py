#!/usr/bin/env python
"""
Script to demonstrate and test the endgame tablebase approach.

This script:
1. Creates a small endgame tablebase through random playouts to terminal positions
2. Tests that the tablebase can be used to make optimal moves from known positions
3. Illustrates the "bottom-up" approach of building an endgame tablebase
"""
import os
import sys
import random
from pathlib import Path

# Add project root to path if running from temp directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.hexapawn import Hexapawn
from tablebase import EndgameTablebase

def test_endgame_tablebase():
    """Demonstrate and test the endgame tablebase approach."""
    # Path to the database file
    db_path = "hexapawn_endgame.duckdb"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        except Exception as e:
            print(f"Error removing database: {e}")
            sys.exit(1)
    
    # Create a new tablebase
    tablebase = EndgameTablebase(db_path=db_path)
    
    # Create a Hexapawn game instance
    game = Hexapawn()
    
    print("Starting position:")
    game.render()
    
    # First, let's manually create a near-terminal position
    print("\nCreating a near-terminal position...")
    
    # This is a position where player 1 can win in one move by advancing a pawn to the top row
    game = Hexapawn()
    # Move player 1's center pawn forward
    game.make_move(('1', 2, 1, 1, 1))
    # Move player 2's center pawn forward
    game.make_move(('2', 0, 1, 1, 1))
    # Capture with player 1's right pawn
    game.make_move(('1', 2, 2, 1, 1))
    # Move player 2's left pawn forward
    game.make_move(('2', 0, 0, 1, 0))
    
    print("Near-terminal position (player 1 can win in one move):")
    game.render()
    
    # Verify this position isn't terminal yet
    assert not game.is_terminal(), "Position should not be terminal yet"
    
    # Make a copy of this position for later testing
    test_position = game.clone()
    test_position_hash = test_position.hash()
    
    # Now manually add this position and its children to the tablebase
    print("\nAnalyzing position and adding to tablebase...")
    tablebase._solve_position(game)
    tablebase.save()
    
    # Get statistics
    print("\nTablebase statistics:")
    stats = tablebase.get_statistics()
    print(f"Total positions: {stats['total']}")
    print(f"Wins: {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Draws: {stats['draws']}")
    
    # Now test that we can retrieve the best move from this position
    print("\nTesting retrieval of best move...")
    position_info = tablebase.get_position_info(test_position_hash)
    
    if position_info:
        print(f"Position value: {position_info['value']}")
        print(f"Depth to terminal: {position_info['depth_to_terminal']}")
        print(f"Is terminal: {position_info['is_terminal']}")
        print(f"Best next state hash: {position_info['best_next_state_hash']}")
        
        # Get best move
        best_move = tablebase.get_best_move(test_position)
        if best_move:
            print(f"Best move: {best_move}")
            
            # Make the best move and check if it leads to a win
            test_position.make_move(best_move)
            print("\nPosition after best move:")
            test_position.render()
            
            if test_position.is_terminal():
                print(f"Game over. Winner: {test_position.winner}")
                assert test_position.winner == '1', "Player 1 should win with optimal play"
            else:
                print("Game not over yet after best move.")
        else:
            print("Error: No best move found!")
    else:
        print("Error: Position not found in tablebase!")
    
    # Now build a more substantial tablebase
    print("\nBuilding larger endgame tablebase...")
    tablebase.build_tablebase(
        Hexapawn(),
        max_positions=100,
        max_random_plies=5,  # Limit depth to focus on endgame positions
        show_progress=True
    )
    
    # Get updated statistics
    print("\nUpdated tablebase statistics:")
    stats = tablebase.get_statistics()
    print(f"Total positions: {stats['total']}")
    print(f"Wins: {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Draws: {stats['draws']}")
    
    # Close the database connection
    tablebase.close()
    
    print(f"\nEndgame tablebase saved to: {db_path}")
    print("Test completed.")

if __name__ == "__main__":
    test_endgame_tablebase() 