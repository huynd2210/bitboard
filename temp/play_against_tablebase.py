#!/usr/bin/env python
"""
Interactive script to play against the perfect Hexapawn tablebase.

This script allows a human player to play against the perfect tablebase.
The computer will always make optimal moves using the tablebase.
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

def render_board_with_coordinates(game):
    """Render the board with coordinates for move selection."""
    # Print column coordinates
    print("  ", end="")
    for j in range(game.sizeJ):
        print(f" {j} ", end="")
    print()
    
    # Print top border
    print("  " + "-" * (game.sizeJ * 3 + 1))
    
    # Print board with row coordinates
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

def get_human_move(game):
    """Get a move from the human player."""
    legal_moves = game.get_legal_moves()
    if not legal_moves:
        print("No legal moves available!")
        return None
    
    print("\nLegal moves:")
    for i, move in enumerate(legal_moves):
        _, from_i, from_j, to_i, to_j = move
        print(f"{i+1}. Move from ({from_i},{from_j}) to ({to_i},{to_j})")
    
    while True:
        try:
            choice = int(input("\nEnter your move number: ")) - 1
            if 0 <= choice < len(legal_moves):
                return legal_moves[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def play_against_tablebase():
    """Play a game against the perfect tablebase."""
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
    
    # Determine who goes first
    while True:
        player_choice = input("Do you want to play as player 1 or player 2? (1/2): ").strip()
        if player_choice in ["1", "2"]:
            break
        print("Invalid choice. Please enter 1 or 2.")
    
    human_player = player_choice
    computer_player = "2" if human_player == "1" else "1"
    
    print(f"\nYou are playing as Player {human_player}.")
    print(f"Computer is playing as Player {computer_player}.")
    print("The board coordinates are (row, column) starting from (0,0) at the top-left.")
    print("Player 1 pawns start at the bottom and move upward.")
    print("Player 2 pawns start at the top and move downward.")
    
    # Game loop
    current_turn = "1"  # Player 1 always goes first in Hexapawn
    
    while not game.is_over():
        print("\n" + "=" * 40)
        print(f"Current turn: Player {current_turn}")
        render_board_with_coordinates(game)
        
        if current_turn == human_player:
            # Human's turn
            print("\nYour turn!")
            move = get_human_move(game)
            if move is None:
                break
        else:
            # Computer's turn
            print("\nComputer's turn...")
            move = tablebase.get_best_move(game)
            if move is None:
                print("Computer couldn't find a move! This shouldn't happen.")
                break
            
            _, from_i, from_j, to_i, to_j = move
            print(f"Computer moves from ({from_i},{from_j}) to ({to_i},{to_j})")
        
        # Make the move
        game.make_move(move)
        
        # Switch turns
        current_turn = "2" if current_turn == "1" else "1"
    
    # Game over
    print("\n" + "=" * 40)
    print("GAME OVER")
    render_board_with_coordinates(game)
    
    if game.winner:
        if game.winner == human_player:
            print("Congratulations! You won!")
        else:
            print("The computer won. Better luck next time!")
    else:
        print("The game ended in a draw.")
    
    # Close the database connection
    tablebase.close()

if __name__ == "__main__":
    play_against_tablebase() 