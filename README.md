# Bitboard Endgame Tablebase

This project implements an endgame tablebase builder for abstract strategy games using a bitboard representation. It also provides a Gymnasium-compatible environment for reinforcement learning algorithms.

## Features

- Efficient bitboard representation for abstract strategy games
- Endgame tablebase builder that stores optimal moves in a DuckDB database
- Support for Hexapawn and Onitama games
- Gymnasium-compatible interface for reinforcement learning
- Interactive play against the tablebase AI

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/bitboard.git
cd bitboard
pip install -r requirements.txt
```

## Usage

### Building a Tablebase

To build an endgame tablebase for Hexapawn:

```bash
python main.py build hexapawn --max-positions 10000 --output hexapawn.pkl
```

For Onitama (warning: much larger state space):

```bash
python main.py build onitama --max-positions 100000 --output onitama.pkl
```

### Analyzing a Tablebase

To see statistics about a tablebase:

```bash
python main.py analyze hexapawn.pkl
```

### Playing Against the Tablebase

To play against the tablebase AI:

```bash
python main.py play hexapawn hexapawn.pkl
```

## How it Works

The endgame tablebase is built using the following approach:

1. Random moves are played until a terminal state is reached
2. The terminal state is evaluated (win, loss, or draw)
3. The algorithm backtracks one level and solves that subtree
4. Solved states are stored in a DuckDB database, including the best move
5. The process is repeated until the entire game tree is solved or a stopping condition is reached

The database schema includes:
- `positions` table: Stores position hashes, values, and metadata
- `best_moves` table: Stores best moves for each position

## Game Implementation

Games must implement the following methods to be compatible with the tablebase:

- `clone()`: Create a deep copy of the game state
- `is_terminal()`: Check if the game is over
- `get_value()`: Get the value of the current position (1.0 for win, -1.0 for loss, 0.0 for draw)
- `hash()`: Get a unique hash for the current position
- `get_legal_moves()`: Get all legal moves from the current position
- `make_move(move)`: Make a move on the board

## Gymnasium Integration

The `GymGameWrapper` class provides a Gymnasium-compatible interface for the games. This allows using the games with reinforcement learning algorithms from the Gymnasium ecosystem.

Example:

```python
from games.hexapawn import create_hexapawn_env

env = create_hexapawn_env()
observation, info = env.reset()

for _ in range(100):
    action = env.action_space.sample()  # take a random action
    observation, reward, terminated, truncated, info = env.step(action)
    
    if terminated or truncated:
        observation, info = env.reset()
```

## Testing

Run the test suite to verify the implementation:

```bash
python test_tablebase.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 