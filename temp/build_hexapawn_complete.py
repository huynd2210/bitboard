#!/usr/bin/env python
"""
Script to build a complete tablebase for Hexapawn.
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path if running from temp directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.hexapawn import Hexapawn
from tablebase import EndgameTablebase

def build_complete_hexapawn_tablebase():
    """Build a complete tablebase for the Hexapawn game."""
    # Path to the database file
    db_path = "hexapawn_complete.duckdb"
    
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
    
    # Start time measurement
    start_time = time.time()
    
    print(f"Building complete tablebase for Hexapawn...")
    print(f"Board size: {game.sizeI}x{game.sizeJ}")
    print(f"This may take a while...")
    
    # Build the tablebase - using a large max_positions to ensure capturing all states
    # The theoretical upper bound for 3x3 Hexapawn is around 2000 positions
    tablebase.build_tablebase(
        game, 
        max_positions=10000,  # Large enough to capture all positions
        max_random_plies=20,  # Hexapawn games are short
        batch_save=500,       # Save every 500 positions
        show_progress=True
    )
    
    # End time measurement
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Get statistics
    stats = tablebase.get_statistics()
    
    print(f"\nTablebase building completed in {elapsed_time:.2f} seconds.")
    print(f"Total positions: {stats['total']}")
    print(f"Wins: {stats['wins']} ({(stats['wins']/stats['total']*100):.1f}%)")
    print(f"Losses: {stats['losses']} ({(stats['losses']/stats['total']*100):.1f}%)")
    print(f"Draws: {stats['draws']} ({(stats['draws']/stats['total']*100):.1f}%)")
    print(f"Maximum depth to terminal: {stats['max_depth']}")
    
    # Get database file size
    size_bytes = os.path.getsize(db_path)
    size_kb = size_bytes / 1024
    
    print(f"Database file size: {size_kb:.2f} KB")
    
    # Close the database connection
    tablebase.close()
    
    print(f"\nComplete Hexapawn tablebase saved to: {db_path}")
    print("You can use this tablebase with the main.py script:")
    print(f"  python main.py play hexapawn {db_path}")

if __name__ == "__main__":
    build_complete_hexapawn_tablebase() 