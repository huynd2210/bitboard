import copy
import random
from typing import List, Tuple, Dict, Optional, Any

from bitboard import BitboardManager


class Hexapawn:
    """
    Implementation of the Hexapawn game.
    
    Hexapawn is a simple chess-like game played on a 3x3 board, where:
    - Each player starts with 3 pawns on their back rank
    - Pawns move forward one square if unoccupied
    - Pawns capture diagonally forward
    - Players win by reaching the opponent's back rank or capturing all opponent pawns
    - A player loses if they have no legal moves
    """
    
    def __init__(self, sizeI: int = 3, sizeJ: int = 3, zobristSeed: int = None):
        """
        Initialize a new Hexapawn game.
        
        Args:
            sizeI: Number of rows on the board
            sizeJ: Number of columns on the board
            zobristSeed: Fixed seed for Zobrist hashing to ensure consistent hashes
        """
        self.sizeI = sizeI
        self.sizeJ = sizeJ
        self.bm = BitboardManager(sizeI=sizeI, sizeJ=sizeJ, useZobrist=True, zobristSeed=zobristSeed)
        self.current_player = '1'  # Player 1 goes first
        self.winner = None
        self._init_board()
    
    def _init_board(self):
        """Initialize the bitboards for both players."""
        # Create bitboards for both players
        self.bm.buildBitboard('1', self.sizeI, self.sizeJ)
        self.bm.buildBitboard('2', self.sizeI, self.sizeJ)
        
        # Set player 2's pawns on the top row
        self.bm.setAllBitsAtRow('2', 0)
        
        # Set player 1's pawns on the bottom row
        self.bm.setAllBitsAtRow('1', self.sizeI - 1)
    
    def clone(self):
        """Create a deep copy of the current game state."""
        # Create a new game with the same zobristSeed
        new_game = Hexapawn(self.sizeI, self.sizeJ, zobristSeed=self.bm.zobristSeed)
        
        # Copy the bitboard data directly
        new_game.bm.bitboardManager['1'].data = self.bm.bitboardManager['1'].data
        new_game.bm.bitboardManager['2'].data = self.bm.bitboardManager['2'].data
        
        # Make sure the zobrist tables are identical
        new_game.bm.zobristTable = self.bm.zobristTable
        
        # Copy game state
        new_game.current_player = self.current_player
        new_game.winner = self.winner
        return new_game
    
    def is_first_player_turn(self) -> bool:
        """Return whether it's the first player's turn."""
        return self.current_player == '1'
    
    def is_over(self) -> bool:
        """Check if the game is over."""
        # Check if any player reached the opponent's side
        if self.bm.isAnyPieceSetAtRow('1', 0):
            self.winner = '1'
            return True
        if self.bm.isAnyPieceSetAtRow('2', self.sizeI - 1):
            self.winner = '2'
            return True
        
        # Check if any player has no pieces left
        if self.bm.isEmpty('1'):
            self.winner = '2'
            return True
        if self.bm.isEmpty('2'):
            self.winner = '1'
            return True
        
        # Check if current player has no legal moves
        if not self.get_legal_moves():
            self.winner = '2' if self.current_player == '1' else '1'
            return True
        
        return False
    
    def is_terminal(self) -> bool:
        """Alias for is_over for compatibility with tablebase."""
        return self.is_over()
    
    def get_value(self) -> float:
        """
        Get the value of the current position.
        
        Returns:
            1.0 if player 1 wins, -1.0 if player 2 wins, 0.0 for draw
        """
        if not self.is_over():
            return 0.0
            
        if self.winner == '1':
            return 1.0
        elif self.winner == '2':
            return -1.0
        else:
            return 0.0  # Draw
    
    def hash(self) -> int:
        """Get a unique hash for the current position."""
        # We use the Zobrist hash of the bitboard plus current player
        player_bit = 1 if self.current_player == '1' else 0
        board_hash = self.bm.zobrist_hash([player_bit])
        return board_hash
    
    def get_legal_moves(self) -> List[Tuple[str, int, int, int, int]]:
        """Get all legal moves for the current player."""
        return self.get_all_possible_moves(self.is_first_player_turn())
    
    def get_all_possible_moves(self, is_first_player_turn: bool) -> List[Tuple[str, int, int, int, int]]:
        """
        Get all possible moves for the specified player.
        
        Args:
            is_first_player_turn: True if getting moves for player 1, False for player 2
            
        Returns:
            List of moves as (bitboard_id, from_i, from_j, to_i, to_j)
        """
        player_id = '1' if is_first_player_turn else '2'
        opponent_id = '2' if is_first_player_turn else '1'
        
        # Movement direction depends on the player
        forward = -1 if is_first_player_turn else 1
        
        # Check pawns for the specified player
        moves = []
        piece_coords = self.bm.getCoordinatesOfPieces(player_id)
        
        for i, j in piece_coords:
            # Forward move (if square is empty)
            new_i = i + forward
            if (0 <= new_i < self.sizeI and 
                not self.bm.isPieceSet(player_id, new_i, j) and 
                not self.bm.isPieceSet(opponent_id, new_i, j)):
                moves.append((player_id, i, j, new_i, j))
            
            # Diagonal captures (if opponent piece is present)
            for new_j in [j-1, j+1]:
                if (0 <= new_i < self.sizeI and 0 <= new_j < self.sizeJ and 
                    self.bm.isPieceSet(opponent_id, new_i, new_j)):
                    moves.append((player_id, i, j, new_i, new_j))
        
        return moves
    
    def make_move(self, move: Tuple[str, int, int, int, int]):
        """
        Make a move on the board.
        
        Args:
            move: Tuple of (bitboard_id, from_i, from_j, to_i, to_j)
        """
        bitboard_id, from_i, from_j, to_i, to_j = move
        opponent_id = '2' if bitboard_id == '1' else '1'
        
        # Move with capture
        self.bm.moveWithCapture(bitboard_id, from_i, from_j, to_i, to_j, [opponent_id])
        
        # Switch player
        self.current_player = '1' if self.current_player == '2' else '2'
    
    def render(self):
        """Render the current state of the board."""
        self.bm.showAllBitboard()


# For Gymnasium compatibility
def create_hexapawn_env():
    """Create a Gymnasium-compatible Hexapawn environment."""
    from tablebase import GymGameWrapper
    game = Hexapawn()
    return GymGameWrapper(game) 