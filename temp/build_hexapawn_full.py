#!/usr/bin/env python
"""
Script to build a complete Hexapawn tablebase.

This script builds a complete tablebase for Hexapawn by exploring
all possible positions reachable from the initial position.
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path if running from temp directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.hexapawn import Hexapawn
from tablebase import EndgameTablebase

# Fixed seed for consistent Zobrist hashing
FIXED_SEED = 42

def build_complete_hexapawn_tablebase():
    """Build a complete tablebase for Hexapawn."""
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
    
    # Create a Hexapawn game instance with fixed seed
    # The BitboardManager inside Hexapawn will use this seed for Zobrist hashing
    game = Hexapawn(zobristSeed=FIXED_SEED)
    
    # Start time measurement
    start_time = time.time()
    
    # Build the complete tablebase
    print(f"Building complete tablebase for Hexapawn...")
    print(f"Board size: {game.sizeI}x{game.sizeJ}")
    print(f"Using fixed Zobrist hash seed: {FIXED_SEED}")
    
    # Use the new complete tablebase building method
    positions = tablebase.build_complete_tablebase(game, show_progress=True)
    
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
    print("Important: When using this tablebase, make sure to initialize Hexapawn with the same seed:")
    print(f"  game = Hexapawn(zobristSeed={FIXED_SEED})")

if __name__ == "__main__":
    build_complete_hexapawn_tablebase() 