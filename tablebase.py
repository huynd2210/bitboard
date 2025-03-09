import random
import pickle
import os
from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np
from tqdm import tqdm
import duckdb

class EndgameTablebase:
    """
    Endgame tablebase implementation for abstract strategy games.
    
    This class provides functionality to build and query an endgame tablebase
    for abstract strategy games, using the bitboard representation.
    
    The tablebase is built by:
    1. Randomly selecting legal moves until a terminal state is reached
    2. Backtracking one level and solving that subtree
    3. Storing solved states in a database
    4. Repeating until the entire game tree is solved or a stopping condition is reached
    """
    
    def __init__(self, db_path: str = "tablebase.duckdb"):
        """
        Initialize the endgame tablebase.
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path
        self.conn = None
        self.connect_db()
        self.in_memory_cache = {}  # Cache for frequently accessed positions
    
    def connect_db(self):
        """Connect to the database and create tables if they don't exist."""
        # Close previous connection if exists
        if self.conn is not None:
            self.conn.close()
            
        # Connect to the database
        self.conn = duckdb.connect(self.db_path)
        
        # Create tables if they don't exist
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                state_hash VARCHAR PRIMARY KEY,
                value FLOAT,
                depth_to_terminal INTEGER,
                is_terminal BOOLEAN
            )
        """)
        
        # Updated schema to store next state hash instead of move_data
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS best_moves (
                state_hash VARCHAR PRIMARY KEY,
                best_next_state_hash VARCHAR,
                FOREIGN KEY (state_hash) REFERENCES positions(state_hash)
            )
        """)
        
        # Create indices for better performance
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_state_hash ON positions (state_hash)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_best_moves_state_hash ON best_moves (state_hash)")
        
        # Commit changes
        self.conn.commit()
    
    def load_if_exists(self):
        """Load the tablebase from disk if it exists."""
        if os.path.exists(self.db_path):
            try:
                # Get count of positions
                result = self.conn.execute("SELECT COUNT(*) FROM positions").fetchone()
                position_count = result[0] if result else 0
                print(f"Connected to tablebase at {self.db_path} with {position_count} positions")
            except Exception as e:
                print(f"Error connecting to tablebase: {e}")
                # Recreate tables
                self.connect_db()
    
    def save(self):
        """Save any pending changes to the database."""
        self.conn.commit()
        print(f"Saved changes to {self.db_path}")
    
    def get_position_info(self, state_hash: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a position from the tablebase.
        
        Args:
            state_hash: Hash of the state to query
            
        Returns:
            Dictionary containing position information or None if not found
        """
        # Convert hash to string for database storage
        hash_str = str(state_hash)
        
        # Check in-memory cache first
        if hash_str in self.in_memory_cache:
            return self.in_memory_cache[hash_str]
        
        # Query the database
        result = self.conn.execute("""
            SELECT p.value, p.depth_to_terminal, p.is_terminal, b.best_next_state_hash
            FROM positions p
            LEFT JOIN best_moves b ON p.state_hash = b.state_hash
            WHERE p.state_hash = ?
        """, [hash_str]).fetchone()
        
        if not result:
            # Try to find the closest hash as a fallback (for debugging only)
            close_hash = self.conn.execute("""
                SELECT state_hash FROM positions LIMIT 1
            """).fetchone()
            if close_hash:
                print(f"Debug: Position not found. Example hash in DB: {close_hash[0]}")
                print(f"Debug: Looking for hash: {hash_str}")
            return None
            
        value, depth_to_terminal, is_terminal, best_next_state_hash = result
        
        # Create position info dictionary
        position_info = {
            'value': value,
            'depth_to_terminal': depth_to_terminal,
            'is_terminal': is_terminal,
            'best_next_state_hash': best_next_state_hash
        }
        
        # Add to cache
        self.in_memory_cache[hash_str] = position_info
        
        return position_info
    
    def add_position(self, state_hash: int, value: float, best_move=None, best_next_state_hash=None, 
                     depth_to_terminal: int = 0, is_terminal: bool = False):
        """
        Add a position to the tablebase.
        
        Args:
            state_hash: Hash of the state
            value: Value of the position (-1 loss, 0 draw, 1 win)
            best_move: Best move from this position (not stored anymore, kept for backward compatibility)
            best_next_state_hash: Hash of the best next state (resulting from best move)
            depth_to_terminal: Depth to terminal position
            is_terminal: Whether this is a terminal position
        """
        # Convert hash to string for database storage
        hash_str = str(state_hash)
        
        # Insert or update position
        self.conn.execute("""
            INSERT OR REPLACE INTO positions (state_hash, value, depth_to_terminal, is_terminal)
            VALUES (?, ?, ?, ?)
        """, [hash_str, value, depth_to_terminal, is_terminal])
        
        # Insert or update best next state hash if provided
        if best_next_state_hash is not None:
            next_state_hash_str = str(best_next_state_hash)
            
            self.conn.execute("""
                INSERT OR REPLACE INTO best_moves (state_hash, best_next_state_hash)
                VALUES (?, ?)
            """, [hash_str, next_state_hash_str])
        
        # Update cache
        self.in_memory_cache[hash_str] = {
            'value': value,
            'depth_to_terminal': depth_to_terminal,
            'is_terminal': is_terminal,
            'best_next_state_hash': best_next_state_hash
        }
    
    def build_tablebase(self, game, max_positions: int = 100000, 
                         max_random_plies: int = 100, batch_save: int = 10000,
                         show_progress: bool = True):
        """
        Build the endgame tablebase.
        
        Args:
            game: Game instance (must implement get_legal_moves, make_move, is_terminal, etc.)
            max_positions: Maximum number of positions to store
            max_random_plies: Maximum number of random moves to make
            batch_save: Save the tablebase after this many new positions
            show_progress: Whether to show a progress bar
        """
        positions_analyzed = 0
        progress_bar = None
        
        if show_progress:
            progress_bar = tqdm(total=max_positions, desc="Building tablebase")
        
        while positions_analyzed < max_positions:
            # Random playout to reach varied positions
            initial_state = game.clone()
            plies = 0
            
            # Make random moves until terminal state or max_random_plies reached
            while not game.is_terminal() and plies < max_random_plies:
                legal_moves = game.get_legal_moves()
                if not legal_moves:
                    break
                    
                move = random.choice(legal_moves)
                game.make_move(move)
                plies += 1
            
            # Start solving from this position backwards
            positions_from_solve = self._solve_position(game)
            positions_analyzed += positions_from_solve
            
            if show_progress:
                progress_bar.update(positions_from_solve)
            
            # Reset the game
            game = initial_state
            
            # Save periodically
            if positions_analyzed % batch_save < positions_from_solve:
                self.save()
                # Clear the in-memory cache to prevent memory growth
                self.in_memory_cache = {}
        
        if show_progress:
            progress_bar.close()
        
        # Final save
        self.save()
    
    def get_position_count(self) -> int:
        """Get the total number of positions in the tablebase."""
        result = self.conn.execute("SELECT COUNT(*) FROM positions").fetchone()
        return result[0] if result else 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the tablebase."""
        stats = {}
        
        # Total positions
        stats['total'] = self.get_position_count()
        
        # Count by value
        result = self.conn.execute("""
            SELECT 
                SUM(CASE WHEN value > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN value < 0 THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN value = 0 THEN 1 ELSE 0 END) as draws,
                MAX(depth_to_terminal) as max_depth
            FROM positions
        """).fetchone()
        
        if result:
            wins, losses, draws, max_depth = result
            stats['wins'] = wins or 0
            stats['losses'] = losses or 0
            stats['draws'] = draws or 0
            stats['max_depth'] = max_depth or 0
        
        return stats
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
    
    def _solve_position(self, game) -> int:
        """
        Recursively solve a position and its predecessors.
        
        Args:
            game: Game instance at current position
            
        Returns:
            Number of positions added to the tablebase
        """
        current_hash = game.hash()
        hash_str = str(current_hash)
        
        # If already in tablebase, return 0 (no new positions)
        result = self.conn.execute("SELECT 1 FROM positions WHERE state_hash = ?", [hash_str]).fetchone()
        if result:
            return 0
        
        positions_added = 1
        
        # If terminal, add with appropriate value
        if game.is_terminal():
            value = game.get_value()
            self.add_position(current_hash, value, None, None, 0, True)
            return positions_added
        
        # Get all legal moves
        legal_moves = game.get_legal_moves()
        
        # If no legal moves, this is a stalemate
        if not legal_moves:
            self.add_position(current_hash, 0.0, None, None, 0, True)
            return positions_added
        
        # Try all moves and find the best one
        best_move = None
        best_next_state_hash = None
        best_value = float('-inf') if game.is_first_player_turn() else float('inf')
        max_depth = 0
        
        for move in legal_moves:
            # Make move and get info
            game_clone = game.clone()
            game_clone.make_move(move)
            next_hash = game_clone.hash()
            next_hash_str = str(next_hash)
            
            # Recursive solve if not already in tablebase
            position_info = self.get_position_info(next_hash)
            if not position_info:
                positions_added += self._solve_position(game_clone)
                position_info = self.get_position_info(next_hash)
                if not position_info:
                    # This should not happen, but just in case
                    continue
            
            # Get value from tablebase
            move_value = position_info['value']
            move_depth = position_info['depth_to_terminal'] + 1
            
            # Update max_depth
            max_depth = max(max_depth, move_depth)
            
            # Update best move for first player (maximizing)
            if game.is_first_player_turn():
                if move_value > best_value:
                    best_value = move_value
                    best_move = move  # Store for debugging but don't save to DB
                    best_next_state_hash = next_hash_str  # Store string representation
            # Update best move for second player (minimizing)
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move  # Store for debugging but don't save to DB
                    best_next_state_hash = next_hash_str  # Store string representation
        
        # Add position to tablebase
        self.add_position(current_hash, best_value, None, best_next_state_hash, max_depth, False)
        
        return positions_added
    
    def get_best_move(self, game):
        """
        Get the best move for the current game state.
        
        This method looks up the current state in the tablebase, finds the best next state,
        and then determines which move leads to that state.
        
        Args:
            game: Current game state
            
        Returns:
            The best move or None if not found
        """
        current_hash = game.hash()
        current_hash_str = str(current_hash)
        
        position_info = self.get_position_info(current_hash)
        
        if not position_info or position_info.get('best_next_state_hash') is None:
            return None
        
        # Get the best next state hash
        best_next_state_hash = position_info['best_next_state_hash']
        
        # Find the move that leads to this state
        legal_moves = game.get_legal_moves()
        
        for move in legal_moves:
            game_clone = game.clone()
            game_clone.make_move(move)
            next_hash = game_clone.hash()
            next_hash_str = str(next_hash)
            
            if next_hash_str == best_next_state_hash:
                return move
            
        return None

    def build_complete_tablebase(self, game, show_progress: bool = True):
        """
        Build a complete tablebase by exhaustively exploring the game tree from the initial position.
        
        This is different from the random sampling approach in build_tablebase.
        It guarantees that all reachable positions from the initial state are included.
        
        Args:
            game: Game instance (must implement get_legal_moves, make_move, is_terminal, etc.)
            show_progress: Whether to show a progress bar
        """
        # Start from initial position
        initial_game = game.clone()
        
        # Use a stack (LIFO) for depth-first search
        position_stack = [initial_game]
        positions_analyzed = 0
        
        # Use a set to track already seen positions
        seen_positions = set()
        
        progress_bar = None
        if show_progress:
            # Start with an unknown total
            progress_bar = tqdm(desc="Building complete tablebase")
        
        print("Starting complete tablebase build from initial position...")
        print("This will explore all reachable positions.")
        
        while position_stack:
            # Get next position to analyze
            current_game = position_stack.pop()
            current_hash = current_game.hash()
            
            # Skip if already seen
            if current_hash in seen_positions:
                continue
            
            seen_positions.add(current_hash)
            
            # Analyze position
            self._solve_position(current_game)
            positions_analyzed += 1
            
            # Update progress
            if show_progress and positions_analyzed % 10 == 0:
                progress_bar.update(10)
                progress_bar.set_postfix({"positions": positions_analyzed})
            
            # Skip terminal positions for expansion
            if current_game.is_terminal():
                continue
            
            # Get all legal moves
            legal_moves = current_game.get_legal_moves()
            
            # Skip if no legal moves
            if not legal_moves:
                continue
            
            # Add child positions to stack
            for move in legal_moves:
                next_game = current_game.clone()
                next_game.make_move(move)
                position_stack.append(next_game)
            
            # Save periodically
            if positions_analyzed % 1000 == 0:
                self.save()
                # Clear the in-memory cache to prevent memory growth
                self.in_memory_cache = {}
        
        if show_progress:
            progress_bar.close()
        
        # Final save
        self.save()
        
        print(f"Complete tablebase built with {positions_analyzed} positions.")
        return positions_analyzed


# Gym-compatible environment interface
class GymGameWrapper:
    """
    Wrapper that provides a Gymnasium-compatible interface for abstract strategy games.
    
    This wrapper allows integration with various reinforcement learning algorithms
    by providing a standard interface compliant with the Gymnasium API.
    """
    
    def __init__(self, game):
        """
        Initialize the wrapper with a game instance.
        
        Args:
            game: Game instance that implements the required methods
        """
        self.game = game
        self.action_space_size = self._determine_action_space_size()
        
        # Observation space shape depends on the game implementation
        # This will need to be adjusted based on the specific game
        self.observation_shape = self._determine_observation_shape()
        
    def _determine_action_space_size(self):
        """Determine the size of the action space."""
        # This is a placeholder - needs to be implemented for specific games
        return len(self.game.get_all_possible_moves(self.game.is_first_player_turn()))
    
    def _determine_observation_shape(self):
        """Determine the shape of the observation space."""
        # This is a placeholder - needs to be implemented for specific games
        # For bitboard games, this might be the number of bitboards times the board dimensions
        bitboards = len(self.game.bm.bitboardManager)
        return (bitboards, self.game.bm.sizeI, self.game.bm.sizeJ)
    
    def reset(self, seed=None):
        """
        Reset the environment to initial state.
        
        Args:
            seed: Random seed
            
        Returns:
            Initial observation and info
        """
        if seed is not None:
            random.seed(seed)
            
        self.game.__init__()  # Reset the game
        return self._get_observation(), {}
    
    def _get_observation(self):
        """
        Convert game state to observation.
        
        Returns:
            Numpy array representation of the game state
        """
        # This is a placeholder - needs to be implemented for specific games
        # For bitboard games, we might create a 3D tensor with one plane per bitboard
        observation = np.zeros(self.observation_shape, dtype=np.int8)
        
        for i, (bitboard_id, bitboard) in enumerate(self.game.bm.bitboardManager.items()):
            for row in range(self.game.bm.sizeI):
                for col in range(self.game.bm.sizeJ):
                    if self.game.bm.isPieceSet(bitboard_id, row, col):
                        observation[i, row, col] = 1
                        
        return observation
    
    def step(self, action):
        """
        Take a step in the environment.
        
        Args:
            action: Action to take
            
        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        # Convert action index to game move
        legal_moves = self.game.get_all_possible_moves(self.game.is_first_player_turn())
        if action >= len(legal_moves):
            # Invalid action, penalize
            return self._get_observation(), -1.0, False, False, {"error": "Invalid action"}
        
        move = legal_moves[action]
        
        # Make the move
        self.game.make_move(move)
        
        # Check if the game is over
        terminated = self.game.is_over()
        truncated = False  # No time limit in abstract games
        
        # Determine reward
        reward = 0.0
        if terminated:
            if self.game.winner == '1':
                reward = 1.0  # First player wins
            elif self.game.winner == '2':
                reward = -1.0  # Second player wins
            # Draw is 0.0
        
        return self._get_observation(), reward, terminated, truncated, {}
    
    def render(self):
        """Render the current state of the game."""
        self.game.bm.showAllBitboard()
    
    def close(self):
        """Close the environment."""
        pass 