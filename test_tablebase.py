import unittest
import os
import random
import shutil
from typing import List, Tuple, Dict, Any

from tablebase import EndgameTablebase, GymGameWrapper
from games.hexapawn import Hexapawn
from games.onitama import Onitama


class TestHexapawn(unittest.TestCase):
    """Test the Hexapawn game implementation."""
    
    def setUp(self):
        self.game = Hexapawn()
    
    def test_initial_state(self):
        """Test that the initial state is set up correctly."""
        # Test board dimensions
        self.assertEqual(self.game.sizeI, 3)
        self.assertEqual(self.game.sizeJ, 3)
        
        # Test initial player
        self.assertEqual(self.game.current_player, '1')
        
        # Test initial piece positions
        for j in range(self.game.sizeJ):
            self.assertTrue(self.game.bm.isPieceSet('2', 0, j))  # Player 2's pawns on top row
            self.assertTrue(self.game.bm.isPieceSet('1', 2, j))  # Player 1's pawns on bottom row
    
    def test_legal_moves(self):
        """Test that legal moves are generated correctly."""
        # In the initial position, player 1 should have three forward moves
        moves = self.game.get_legal_moves()
        self.assertEqual(len(moves), 3)
        
        # All moves should be from row 2 to row 1
        for move in moves:
            _, from_i, _, to_i, _ = move
            self.assertEqual(from_i, 2)
            self.assertEqual(to_i, 1)
    
    def test_make_move(self):
        """Test that moves are executed correctly."""
        # Make a move
        self.game.make_move(('1', 2, 1, 1, 1))
        
        # Check that the piece moved
        self.assertFalse(self.game.bm.isPieceSet('1', 2, 1))
        self.assertTrue(self.game.bm.isPieceSet('1', 1, 1))
        
        # Check that player 2 is now to move
        self.assertEqual(self.game.current_player, '2')
    
    def test_win_condition(self):
        """Test that the win conditions are detected correctly."""
        # Player 1 reaches the top row
        self.game.bm.setPiece('1', 0, 0)
        self.assertTrue(self.game.is_over())
        self.assertEqual(self.game.winner, '1')
        
        # Reset and test player 2 reaches bottom row
        self.game = Hexapawn()
        self.game.bm.setPiece('2', 2, 0)
        self.assertTrue(self.game.is_over())
        self.assertEqual(self.game.winner, '2')
    
    def test_capture(self):
        """Test that captures work correctly."""
        # Set up a capture position
        self.game = Hexapawn()
        self.game.bm.setPiece('1', 1, 1)  # Player 1 pawn moved forward
        self.game.bm.deletePiece('1', 2, 1)  # Remove from original position
        
        # Player 2's turn
        self.game.current_player = '2'
        
        # Make a capture move
        self.game.make_move(('2', 0, 0, 1, 1))
        
        # Check that player 1's pawn was captured
        self.assertFalse(self.game.bm.isPieceSet('1', 1, 1))
        # Check that player 2's pawn is now at the position
        self.assertTrue(self.game.bm.isPieceSet('2', 1, 1))


class TestTablebase(unittest.TestCase):
    """Test the tablebase implementation."""
    
    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = "test_tablebase_temp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.tablebase_path = os.path.join(self.test_dir, "test_tablebase.pkl")
        
        # Create a small game for quick testing
        self.game = Hexapawn(sizeI=3, sizeJ=2)  # Smaller board for faster tests
        self.tablebase = EndgameTablebase(db_path=self.tablebase_path)
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_build_tablebase(self):
        """Test building a small tablebase."""
        # Build a small tablebase
        self.tablebase.build_tablebase(self.game, max_positions=100, max_random_plies=10)
        
        # Check that positions were added
        self.assertGreater(len(self.tablebase.tablebase), 0)
        
        # Check that the tablebase was saved
        self.assertTrue(os.path.exists(self.tablebase_path))
    
    def test_position_lookup(self):
        """Test looking up positions in the tablebase."""
        # Add a test position
        test_hash = 12345
        self.tablebase.add_position(
            test_hash, 
            value=1.0, 
            best_move=('1', 2, 0, 1, 0), 
            depth_to_terminal=3,
            is_terminal=False
        )
        
        # Look up the position
        position_info = self.tablebase.get_position_info(test_hash)
        
        # Check that the correct information is returned
        self.assertEqual(position_info['value'], 1.0)
        self.assertEqual(position_info['best_move'], ('1', 2, 0, 1, 0))
        self.assertEqual(position_info['depth_to_terminal'], 3)
        self.assertEqual(position_info['is_terminal'], False)
    
    def test_solve_terminal_position(self):
        """Test solving a terminal position."""
        # Create a game where player 1 is about to win
        game = Hexapawn()
        game.bm.setPiece('1', 1, 0)  # Player 1 pawn one step away from winning
        game.bm.deletePiece('1', 2, 0)  # Remove from original position
        
        # Ensure only one move to win
        game.bm.deletePiece('2', 0, 0)  # Remove player 2 pawn that could block
        
        # Solve the position
        positions_added = self.tablebase._solve_position(game)
        
        # Check that at least one position was added
        self.assertGreater(positions_added, 0)
        
        # Get the hash of the current position
        state_hash = game.hash()
        
        # Look up the position
        position_info = self.tablebase.get_position_info(state_hash)
        
        # Since player 1 can win in one move, best move should be to the top row
        if position_info and position_info.get('best_move'):
            _, _, _, to_i, _ = position_info['best_move']
            self.assertEqual(to_i, 0)


class TestGymWrapper(unittest.TestCase):
    """Test the Gymnasium wrapper."""
    
    def setUp(self):
        self.game = Hexapawn()
        self.wrapper = GymGameWrapper(self.game)
    
    def test_reset(self):
        """Test resetting the environment."""
        obs, info = self.wrapper.reset()
        
        # Check that observation is a numpy array with the right shape
        self.assertEqual(obs.shape, (2, 3, 3))  # 2 bitboards, 3x3 board
        
        # Check that the observation correctly represents the initial state
        # Bottom row should have player 1's pieces
        self.assertTrue((obs[0, 2, :] == 1).all())
        # Top row should have player 2's pieces
        self.assertTrue((obs[1, 0, :] == 1).all())
    
    def test_step(self):
        """Test taking a step in the environment."""
        self.wrapper.reset()
        
        # Try a valid action
        legal_moves = self.game.get_legal_moves()
        action = 0  # First legal move
        
        obs, reward, terminated, truncated, info = self.wrapper.step(action)
        
        # Check that observation is updated
        self.assertEqual(obs.shape, (2, 3, 3))
        
        # Check that the environment is not terminated (game not over yet)
        self.assertFalse(terminated)
        
        # Check that reward is 0 (game not over yet)
        self.assertEqual(reward, 0.0)


if __name__ == '__main__':
    unittest.main() 