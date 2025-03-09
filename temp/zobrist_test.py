#!/usr/bin/env python
"""
Test script to demonstrate the Zobrist hashing inconsistency in the Hexapawn implementation.
"""
import sys
from pathlib import Path

# Add project root to path if running from temp directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from games.hexapawn import Hexapawn

# Fixed seed for consistent Zobrist hashing
FIXED_SEED = 42

def test_zobrist_hashing():
    """Test the consistency of Zobrist hashing across game instances."""
    print("TEST 1: Different instances without fixed seed")
    # -------------------------
    # Test 1: Different instances without fixed seed
    # -------------------------
    
    # Create first Hexapawn instance
    game1 = Hexapawn()
    
    # Get hash of initial position
    initial_hash1 = game1.hash()
    
    # Create second Hexapawn instance
    game2 = Hexapawn()
    
    # Get hash of initial position
    initial_hash2 = game2.hash()
    
    # Check if hashes are the same
    print("Hash test for two identical initial positions (without fixed seed):")
    print(f"Game 1 hash: {initial_hash1}")
    print(f"Game 2 hash: {initial_hash2}")
    print(f"Hashes are {'the same' if initial_hash1 == initial_hash2 else 'different'}")
    print()
    
    # -------------------------
    # Test 2: Different instances with fixed seed
    # -------------------------
    print("TEST 2: Different instances with fixed seed")
    
    # Create first Hexapawn instance with fixed seed
    game3 = Hexapawn(zobristSeed=FIXED_SEED)
    
    # Get hash of initial position
    initial_hash3 = game3.hash()
    
    # Create second Hexapawn instance with fixed seed
    game4 = Hexapawn(zobristSeed=FIXED_SEED)
    
    # Get hash of initial position
    initial_hash4 = game4.hash()
    
    # Check if hashes are the same
    print("Hash test for two identical initial positions (with fixed seed):")
    print(f"Game 3 hash: {initial_hash3}")
    print(f"Game 4 hash: {initial_hash4}")
    print(f"Hashes are {'the same' if initial_hash3 == initial_hash4 else 'different'}")
    print()
    
    # -------------------------
    # Test 3: Making moves with fixed seed
    # -------------------------
    print("TEST 3: Making moves with fixed seed")
    
    # Make the same move in both games
    test_move = ('1', 2, 0, 1, 0)  # Example move
    
    game3.make_move(test_move)
    game4.make_move(test_move)
    
    move1_hash3 = game3.hash()
    move1_hash4 = game4.hash()
    
    print("Hash test after the same move (with fixed seed):")
    print(f"Game 3 hash: {move1_hash3}")
    print(f"Game 4 hash: {move1_hash4}")
    print(f"Hashes are {'the same' if move1_hash3 == move1_hash4 else 'different'}")
    print()
    
    # -------------------------
    # Test 4: Cloning with fixed seed
    # -------------------------
    print("TEST 4: Cloning with fixed seed")
    
    # Clone one of the games
    game5 = game3.clone()
    clone_hash = game5.hash()
    
    print("Hash test with a cloned game (with fixed seed):")
    print(f"Original game hash: {move1_hash3}")
    print(f"Cloned game hash: {clone_hash}")
    print(f"Hashes are {'the same' if move1_hash3 == clone_hash else 'different'}")

if __name__ == "__main__":
    test_zobrist_hashing() 