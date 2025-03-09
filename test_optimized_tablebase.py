import os
import sys
import random
from games.hexapawn import Hexapawn
from tablebase import EndgameTablebase

def test_optimized_tablebase():
    """
    Test the optimized tablebase implementation that stores 
    state hashes instead of move data.
    """
    print("Testing optimized tablebase implementation...")
    
    # Create a temporary database
    db_path = "optimized_test.duckdb"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        except Exception as e:
            print(f"Error removing database: {e}")
            sys.exit(1)
    
    # Create a new tablebase
    tablebase = EndgameTablebase(db_path=db_path)
    
    # Create a game instance
    game = Hexapawn(sizeI=3, sizeJ=3)
    
    # Build a small tablebase
    print("Building small tablebase...")
    tablebase.build_tablebase(game, max_positions=20, show_progress=False)
    
    # Get statistics
    stats = tablebase.get_statistics()
    print(f"Tablebase statistics:")
    print(f"Total positions: {stats['total']}")
    print(f"Wins: {stats['wins']}")
    print(f"Losses: {stats['losses']}")
    print(f"Draws: {stats['draws']}")
    print(f"Max depth: {stats['max_depth']}")
    
    # Test playing a game with the tablebase
    print("\nPlaying a test game with tablebase...")
    game = Hexapawn()  # Reset game to initial state
    
    # Play until game over or max moves reached
    move_count = 0
    while not game.is_over() and move_count < 10:
        print(f"\nMove {move_count + 1}:")
        
        # Get best move
        best_move = tablebase.get_best_move(game)
        
        if best_move:
            print(f"Found tablebase move: {best_move}")
        else:
            legal_moves = game.get_legal_moves()
            if not legal_moves:
                print("No legal moves available.")
                break
                
            best_move = random.choice(legal_moves)
            print(f"Using random move: {best_move}")
        
        # Make the move
        game.make_move(best_move)
        
        # Show the board
        print("Board after move:")
        game.render()
        
        move_count += 1
    
    # Check if game is over
    if game.is_over():
        print(f"\nGame over. Winner: {game.winner}")
    else:
        print("\nMax moves reached.")
    
    # Print database file size
    if os.path.exists(db_path):
        size_bytes = os.path.getsize(db_path)
        print(f"\nTablebase file size: {size_bytes} bytes")
    
    # Close the database
    tablebase.close()
    print("Test completed.")

if __name__ == "__main__":
    test_optimized_tablebase() 