#!/usr/bin/env python
"""
Test script for the complete Hexapawn tablebase.

This script verifies that positions can be properly retrieved from the tablebase
using the same fixed seed for Zobrist hashing.
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

def test_hexapawn_tablebase():
    """Test the complete Hexapawn tablebase."""
    # Path to the database file
    db_path = "hexapawn_complete.duckdb"
    
    # Check if the database exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} not found!")
        print("Please run build_hexapawn_full.py first.")
        return
    
    print(f"Loading tablebase from: {db_path}")
    
    try:
        # Load the tablebase
        tablebase = EndgameTablebase(db_path=db_path)
        
        # Get position count
        position_count = tablebase.get_position_count()
        print(f"Tablebase loaded with {position_count} positions.")
        
        # Create a Hexapawn game instance with the same seed
        print(f"Creating Hexapawn instance with seed {FIXED_SEED}")
        game = Hexapawn(zobristSeed=FIXED_SEED)
        
        # Get the hash of the initial position
        initial_hash = game.hash()
        print(f"Initial position hash: {initial_hash}")
        
        # Check if the initial position is in the tablebase
        print("Searching for initial position in tablebase...")
        position_info = tablebase.get_position_info(initial_hash)
        
        if position_info:
            print("Initial position found in tablebase!")
            print(f"Value: {position_info['value']}")
            print(f"Depth to terminal: {position_info['depth_to_terminal']}")
            print(f"Best next state hash: {position_info.get('best_next_state_hash')}")
        else:
            print("ERROR: Initial position not found in tablebase!")
            
            # Try to get a sample position from the tablebase
            try:
                sample_result = tablebase.conn.execute("SELECT state_hash FROM positions LIMIT 1").fetchone()
                if sample_result:
                    print(f"Example hash in database: {sample_result[0]}")
            except Exception as e:
                print(f"Error querying database: {e}")
        
        # Test getting the best move
        print("\nTrying to get best move for initial position...")
        best_move = tablebase.get_best_move(game)
        if best_move:
            print(f"Best move from initial position: {best_move}")
            
            # Make the best move
            game.make_move(best_move)
            print("After making the best move:")
            game.render()
            
            # Get the new position's hash
            new_hash = game.hash()
            print(f"New position hash: {new_hash}")
            
            # Check if the new position is in the tablebase
            new_position_info = tablebase.get_position_info(new_hash)
            if new_position_info:
                print("New position found in tablebase!")
                print(f"Value: {new_position_info['value']}")
                print(f"Depth to terminal: {new_position_info['depth_to_terminal']}")
            else:
                print("ERROR: New position not found in tablebase!")
        else:
            print("ERROR: No best move found for initial position!")
        
        # Get statistics
        stats = tablebase.get_statistics()
        print("\nTablebase statistics:")
        print(f"Total positions: {stats['total']}")
        print(f"Wins: {stats['wins']} ({(stats['wins']/stats['total']*100):.1f}%)")
        print(f"Losses: {stats['losses']} ({(stats['losses']/stats['total']*100):.1f}%)")
        print(f"Draws: {stats['draws']} ({(stats['draws']/stats['total']*100):.1f}%)")
        print(f"Maximum depth to terminal: {stats['max_depth']}")
        
        # Close the database connection
        tablebase.close()
        
    except Exception as e:
        print(f"ERROR: An exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hexapawn_tablebase() 