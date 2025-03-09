import copy
import random
from typing import List, Tuple, Dict, Optional, Any

from bitboard import BitboardManager


class Card:
    """
    Represents a movement card in Onitama.
    
    Each card has a name, a set of possible movements, and an indicator 
    of which player starts with this card (B for Blue, R for Red).
    """
    
    def __init__(self, name: str, movements: List[Tuple[int, int]], start_player_indicator: str):
        """
        Initialize a card.
        
        Args:
            name: Name of the card
            movements: List of (dx, dy) tuples representing possible movements
            start_player_indicator: 'B' for Blue, 'R' for Red
        """
        self.name = name
        self.movements = movements
        self.start_player_indicator = start_player_indicator


class CardList:
    """Standard set of cards in Onitama."""
    
    cards = [
        Card("Tiger", [(1, 0), (-2, 0)], "B"),
        Card("Dragon", [(1, -1), (1, 1), (-1, -2), (-1, 2)], "R"),
        Card("Frog", [(-1, -1), (0, -2), (1, 1)], "R"),
        Card("Rabbit", [(1, -1), (-1, 1), (0, 2)], "B"),
        Card("Crab", [(-1, 0), (0, -2), (0, 2)], "B"),
        Card("Elephant", [(0, -1), (-1, -1), (0, 1), (-1, 1)], "R"),
        Card("Goose", [(0, -1), (-1, -1), (0, 1), (1, 1)], "B"),
        Card("Rooster", [(0, -1), (1, -1), (0, 1), (-1, 1)], "R"),
        Card("Monkey", [(-1, -1), (-1, 1), (1, -1), (1, 1)], "B"),
        Card("Mantis", [(1, 0), (-1, 1), (-1, -1)], "R"),
        Card("Horse", [(1, 0), (-1, 0), (0, -1)], "R"),
        Card("Ox", [(-1, 0), (1, 0), (0, 1)], "B"),
        Card("Crane", [(-1, 0), (1, -1), (1, 1)], "B"),
        Card("Boar", [(-1, 0), (0, -1), (0, 1)], "R"),
        Card("Eel", [(0, 1), (-1, -1), (1, -1)], "B"),
        Card("Cobra", [(0, -1), (-1, 1), (1, 1)], "R"),
    ]


class Onitama:
    """
    Implementation of the Onitama game.
    
    Onitama is a two-player abstract strategy game where:
    - Each player controls four pawns and one master pawn
    - Movement is dictated by cards with specific patterns
    - A player wins by capturing the opponent's master or moving their master to the opponent's temple
    """
    
    def __init__(self, randomize_cards: bool = True, seed: Optional[int] = None):
        """
        Initialize a new Onitama game.
        
        Args:
            randomize_cards: Whether to select cards randomly
            seed: Random seed for card selection
        """
        self.sizeI = 5
        self.sizeJ = 5
        self.bm = BitboardManager(sizeI=self.sizeI, sizeJ=self.sizeJ, useZobrist=True)
        
        # Set positions of temples
        self.blue_temple = (0, 2)
        self.red_temple = (4, 2)
        
        if seed is not None:
            random.seed(seed)
            
        self.blue_cards = []
        self.red_cards = []
        self.neutral_card = None
        self.winner = None
        
        self._init_board()
        
        if randomize_cards:
            self._init_random_cards()
        else:
            self._init_default_cards()
            
        # Determine starting player
        self.current_player = self.neutral_card.start_player_indicator
    
    def _init_board(self):
        """Initialize the board with pieces for both players."""
        # Create bitboards for pieces
        # Blue: 'B' for master, 'b' for pawn
        # Red: 'R' for master, 'r' for pawn
        self.bm.buildBitboard('B')
        self.bm.buildBitboard('b')
        self.bm.buildBitboard('R')
        self.bm.buildBitboard('r')
        
        # Set up blue pieces (top row)
        self.bm.setPiece('B', 0, 2)  # Blue master at temple
        self.bm.setPiece('b', 0, 0)
        self.bm.setPiece('b', 0, 1)
        self.bm.setPiece('b', 0, 3)
        self.bm.setPiece('b', 0, 4)
        
        # Set up red pieces (bottom row)
        self.bm.setPiece('R', 4, 2)  # Red master at temple
        self.bm.setPiece('r', 4, 0)
        self.bm.setPiece('r', 4, 1)
        self.bm.setPiece('r', 4, 3)
        self.bm.setPiece('r', 4, 4)
    
    def _init_random_cards(self):
        """Randomly select and distribute cards."""
        # Create a copy of the card list
        available_cards = copy.deepcopy(CardList.cards)
        random.shuffle(available_cards)
        
        # Distribute cards: 2 for blue, 2 for red, 1 neutral
        self.blue_cards = [available_cards.pop(), available_cards.pop()]
        self.red_cards = [available_cards.pop(), available_cards.pop()]
        self.neutral_card = available_cards.pop()
    
    def _init_default_cards(self):
        """Set up a default card distribution for testing."""
        # Simple predictable setup
        self.blue_cards = [CardList.cards[0], CardList.cards[2]]  # Tiger and Frog
        self.red_cards = [CardList.cards[1], CardList.cards[3]]   # Dragon and Rabbit
        self.neutral_card = CardList.cards[4]  # Crab
    
    def clone(self):
        """Create a deep copy of the current game state."""
        new_game = Onitama(randomize_cards=False)
        new_game.bm.bitboardManager['B'].data = self.bm.bitboardManager['B'].data
        new_game.bm.bitboardManager['b'].data = self.bm.bitboardManager['b'].data
        new_game.bm.bitboardManager['R'].data = self.bm.bitboardManager['R'].data
        new_game.bm.bitboardManager['r'].data = self.bm.bitboardManager['r'].data
        new_game.blue_cards = copy.deepcopy(self.blue_cards)
        new_game.red_cards = copy.deepcopy(self.red_cards)
        new_game.neutral_card = copy.deepcopy(self.neutral_card)
        new_game.current_player = self.current_player
        new_game.winner = self.winner
        return new_game
    
    def is_first_player_turn(self) -> bool:
        """Return whether it's the first player's (Blue's) turn."""
        return self.current_player == 'B'
    
    def is_over(self) -> bool:
        """Check if the game is over."""
        # Check if blue master is at red temple
        if self.bm.isPieceSet('B', *self.red_temple):
            self.winner = 'B'
            return True
        
        # Check if red master is at blue temple
        if self.bm.isPieceSet('R', *self.blue_temple):
            self.winner = 'R'
            return True
        
        # Check if either master is captured
        if self.bm.isEmpty('B'):
            self.winner = 'R'
            return True
        if self.bm.isEmpty('R'):
            self.winner = 'B'
            return True
        
        # In Onitama, there are always legal moves, so no need to check for stalemate
        
        return False
    
    def is_terminal(self) -> bool:
        """Alias for is_over for compatibility with tablebase."""
        return self.is_over()
    
    def get_value(self) -> float:
        """
        Get the value of the current position.
        
        Returns:
            1.0 if Blue wins, -1.0 if Red wins, 0.0 otherwise
        """
        if not self.is_over():
            return 0.0
            
        if self.winner == 'B':
            return 1.0
        elif self.winner == 'R':
            return -1.0
        else:
            return 0.0  # Shouldn't happen in Onitama
    
    def hash(self) -> int:
        """Get a unique hash for the current position."""
        # Use Zobrist hash combining board state, current player, and card distribution
        player_bit = 1 if self.current_player == 'B' else 0
        
        # Include card information in the hash
        card_info = []
        for card in self.blue_cards:
            card_info.append(hash(card.name))
        for card in self.red_cards:
            card_info.append(hash(card.name))
        card_info.append(hash(self.neutral_card.name))
        
        board_hash = self.bm.zobrist_hash([player_bit] + card_info)
        return board_hash
    
    def get_legal_moves(self) -> List[Tuple[str, int, int, int, int, int]]:
        """Get all legal moves for the current player."""
        if self.current_player == 'B':
            player_pieces = ['B', 'b']
            cards = self.blue_cards
        else:  # 'R'
            player_pieces = ['R', 'r']
            cards = self.red_cards
        
        moves = []
        
        # For each card
        for card_idx, card in enumerate(cards):
            # For each piece
            for piece_type in player_pieces:
                piece_coords = self.bm.getCoordinatesOfPieces(piece_type)
                
                # For each piece of this type
                for i, j in piece_coords:
                    # For each movement pattern on the card
                    for di, dj in card.movements:
                        # Adjust direction for Red player (they play from opposite side)
                        if self.current_player == 'R':
                            di, dj = -di, -dj
                            
                        new_i, new_j = i + di, j + dj
                        
                        # Check if the move is valid
                        if (0 <= new_i < self.sizeI and 0 <= new_j < self.sizeJ):
                            # Can't move to a square occupied by own piece
                            if (self.current_player == 'B' and 
                                (self.bm.isPieceSet('B', new_i, new_j) or self.bm.isPieceSet('b', new_i, new_j))):
                                continue
                            if (self.current_player == 'R' and 
                                (self.bm.isPieceSet('R', new_i, new_j) or self.bm.isPieceSet('r', new_i, new_j))):
                                continue
                                
                            # Valid move: (piece_type, from_i, from_j, to_i, to_j, card_idx)
                            moves.append((piece_type, i, j, new_i, new_j, card_idx))
        
        return moves
    
    def get_all_possible_moves(self, is_first_player_turn: bool) -> List[Tuple[str, int, int, int, int, int]]:
        """
        Get all possible moves for the specified player.
        
        Args:
            is_first_player_turn: True if getting moves for Blue, False for Red
            
        Returns:
            List of moves as (piece_type, from_i, from_j, to_i, to_j, card_idx)
        """
        # Save current player
        current = self.current_player
        
        # Temporarily set player for move generation
        self.current_player = 'B' if is_first_player_turn else 'R'
        moves = self.get_legal_moves()
        
        # Restore current player
        self.current_player = current
        
        return moves
    
    def make_move(self, move: Tuple[str, int, int, int, int, int]):
        """
        Make a move on the board.
        
        Args:
            move: Tuple of (piece_type, from_i, from_j, to_i, to_j, card_idx)
        """
        piece_type, from_i, from_j, to_i, to_j, card_idx = move
        
        # Determine opponent pieces for capture
        opponent_pieces = ['R', 'r'] if self.current_player == 'B' else ['B', 'b']
        
        # Move piece with capture
        self.bm.moveWithCapture(piece_type, from_i, from_j, to_i, to_j, opponent_pieces)
        
        # Exchange the used card with the neutral card
        if self.current_player == 'B':
            temp = self.blue_cards[card_idx]
            self.blue_cards[card_idx] = self.neutral_card
            self.neutral_card = temp
        else:  # 'R'
            temp = self.red_cards[card_idx]
            self.red_cards[card_idx] = self.neutral_card
            self.neutral_card = temp
        
        # Switch player
        self.current_player = 'R' if self.current_player == 'B' else 'B'
    
    def render(self):
        """Render the current state of the board."""
        self.bm.showAllBitboard()
        print(f"Current player: {self.current_player}")
        print("Blue cards:", [card.name for card in self.blue_cards])
        print("Red cards:", [card.name for card in self.red_cards])
        print("Neutral card:", self.neutral_card.name)


# For Gymnasium compatibility
def create_onitama_env():
    """Create a Gymnasium-compatible Onitama environment."""
    from tablebase import GymGameWrapper
    game = Onitama()
    return GymGameWrapper(game) 