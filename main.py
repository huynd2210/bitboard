import argparse
import random
import time
from typing import List, Tuple, Optional

from tablebase import EndgameTablebase, GymGameWrapper
from games.hexapawn import Hexapawn
from games.onitama import Onitama


def random_playout(game, max_moves: int = 100) -> List[Tuple]:
    """Play a random game and return the sequence of moves."""
    moves = []
    for _ in range(max_moves):
        if game.is_over():
            break
        
        legal_moves = game.get_legal_moves()
        if not legal_moves:
            break
            
        move = random.choice(legal_moves)
        moves.append(move)
        game.make_move(move)
    
    return moves


def play_with_tablebase(game, tablebase: EndgameTablebase) -> List[Tuple]:
    """Play a game using the tablebase for perfect play when available."""
    moves = []
    
    for _ in range(100):  # Limit to prevent infinite loops
        if game.is_over():
            break
        
        # Get best move using the new helper method
        best_move = tablebase.get_best_move(game)
        
        if best_move:
            # Use tablebase move
            print(f"Using tablebase move: {best_move}")
        else:
            # Use random move
            legal_moves = game.get_legal_moves()
            if not legal_moves:
                break
                
            best_move = random.choice(legal_moves)
            print(f"Using random move: {best_move}")
            
        moves.append(best_move)
        game.make_move(best_move)
        
    return moves


def human_vs_tablebase(game, tablebase: EndgameTablebase):
    """Allow a human to play against the tablebase."""
    print("Playing against tablebase-powered AI")
    print("Enter moves in the format: <from_i> <from_j> <to_i> <to_j>")
    print("For example: 2 1 1 1")
    
    try:
        while not game.is_over():
            # Display game state
            print("\nCurrent board:")
            game.render()
            
            # Determine current player
            player_name = "You" if game.is_first_player_turn() else "AI"
            print(f"\n{player_name}'s turn")
            
            if game.is_first_player_turn():  # Human's turn
                # Get legal moves
                legal_moves = game.get_legal_moves()
                if not legal_moves:
                    print("No legal moves available. You lose!")
                    break
                    
                # Display legal moves
                print("Legal moves:")
                for i, move in enumerate(legal_moves):
                    print(f"{i}: {move}")
                    
                # Get human move
                valid_input = False
                while not valid_input:
                    try:
                        move_idx = int(input("Enter move number: "))
                        if 0 <= move_idx < len(legal_moves):
                            move = legal_moves[move_idx]
                            valid_input = True
                        else:
                            print(f"Invalid move index. Please enter a number between 0 and {len(legal_moves)-1}")
                    except ValueError:
                        print("Please enter a valid number")
            else:  # AI's turn
                # Get best move using the new helper method
                best_move = tablebase.get_best_move(game)
                
                # Make move with thinking delay for human experience
                time.sleep(1)
                
                if best_move:
                    # Use tablebase move
                    print(f"AI uses tablebase move: {best_move}")
                else:
                    # Use random move
                    legal_moves = game.get_legal_moves()
                    if not legal_moves:
                        print("AI has no legal moves. AI loses!")
                        break
                        
                    best_move = random.choice(legal_moves)
                    print(f"AI uses random move: {best_move}")
                    
            # Make the move
            game.make_move(best_move)
        
        # Game over
        print("\nFinal board:")
        game.render()
        
        if game.winner == '1':
            print("You win!")
        elif game.winner == '2':
            print("AI wins!")
        else:
            print("Draw!")
    finally:
        # Ensure database connection is closed
        tablebase.close()


def build_tablebase(game_name: str, max_positions: int, output_path: str):
    """Build and save a tablebase for the specified game."""
    if game_name.lower() == 'hexapawn':
        game = Hexapawn()
        print("Building tablebase for Hexapawn")
    elif game_name.lower() == 'onitama':
        game = Onitama()
        print("Building tablebase for Onitama")
    else:
        raise ValueError(f"Unknown game: {game_name}")
    
    tablebase = EndgameTablebase(db_path=output_path)
    
    try:
        print(f"Building tablebase with max {max_positions} positions...")
        tablebase.build_tablebase(game, max_positions=max_positions, show_progress=True)
        
        # Get statistics about the built tablebase
        position_count = tablebase.get_position_count()
        print(f"Tablebase built with {position_count} positions.")
        print(f"Tablebase saved to {output_path}")
    finally:
        # Ensure database connection is closed
        tablebase.close()


def analyze_tablebase(tablebase_path: str):
    """Analyze and print statistics about a tablebase."""
    tablebase = EndgameTablebase(db_path=tablebase_path)
    
    # Load the tablebase
    tablebase.load_if_exists()
    
    # Get statistics using the new API
    stats = tablebase.get_statistics()
    
    if stats['total'] == 0:
        print(f"No tablebase found at {tablebase_path}")
        tablebase.close()
        return
    
    print(f"Tablebase statistics for {tablebase_path}:")
    print(f"Total positions: {stats['total']}")
    
    # Calculate percentages
    win_percentage = (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
    loss_percentage = (stats['losses'] / stats['total'] * 100) if stats['total'] > 0 else 0
    draw_percentage = (stats['draws'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    print(f"Wins: {stats['wins']} ({win_percentage:.1f}%)")
    print(f"Losses: {stats['losses']} ({loss_percentage:.1f}%)")
    print(f"Draws: {stats['draws']} ({draw_percentage:.1f}%)")
    print(f"Maximum depth to terminal: {stats['max_depth']}")
    
    # Close the connection
    tablebase.close()


def main():
    parser = argparse.ArgumentParser(description='Abstract strategy game tablebase tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Build tablebase command
    build_parser = subparsers.add_parser('build', help='Build a tablebase')
    build_parser.add_argument('game', help='Game to build tablebase for (hexapawn or onitama)')
    build_parser.add_argument('--max-positions', type=int, default=100000, help='Maximum positions to store')
    build_parser.add_argument('--output', default='tablebase.pkl', help='Output file path')
    
    # Analyze tablebase command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a tablebase')
    analyze_parser.add_argument('tablebase', help='Tablebase file to analyze')
    
    # Play command
    play_parser = subparsers.add_parser('play', help='Play against the tablebase')
    play_parser.add_argument('game', help='Game to play (hexapawn or onitama)')
    play_parser.add_argument('tablebase', help='Tablebase file to use')
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == 'build':
        build_tablebase(args.game, args.max_positions, args.output)
    elif args.command == 'analyze':
        analyze_tablebase(args.tablebase)
    elif args.command == 'play':
        # Create the game
        if args.game.lower() == 'hexapawn':
            game = Hexapawn()
        elif args.game.lower() == 'onitama':
            game = Onitama()
        else:
            print(f"Unknown game: {args.game}")
            return
        
        # Load the tablebase
        tablebase = EndgameTablebase(db_path=args.tablebase)
        
        # Play the game
        human_vs_tablebase(game, tablebase)
    else:
        parser.print_help()


if __name__ == '__main__':
    main() 