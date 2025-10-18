from library.tetrominos.I import ITetromino
from library.tetrominos.J import JTetromino
from library.tetrominos.L import LTetromino
from library.tetrominos.T import TTetromino
from library.tetrominos.O import OTetromino
from library.tetrominos.Z import ZTetromino
from library.tetrominos.S import STetromino


tetromino_list = [
    ITetromino,
    JTetromino,
    LTetromino,
    TTetromino,
    OTetromino,
    ZTetromino,
    STetromino
]  # List of Tetromino classes representing each type of Tetromino in the game.

tetromino_map = {
    'I': ITetromino,
    'J': JTetromino,
    'L': LTetromino,
    'T': TTetromino,
    'O': OTetromino,
    'Z': ZTetromino,
    'S': STetromino
}  # Dictionary mapping Tetromino type identifiers to their respective Tetromino classes.
# Useful for retrieving the class of a Tetromino type by its identifier (e.g., 'I', 'J', etc.).

wall_kick_offsets = {
    'I': [
        [(-2, 0), (1, 0), (-2, -1), (1, 2)],  # 0 -> 1 (rotation index)
        [(-1, 0), (2, 0), (-1, 2), (2, -1)],  # 1 -> 2
        [(2, 0), (-1, 0), (2, 1), (-1, -2)],  # 2 -> 3
        [(1, 0), (-2, 0), (1, -2), (-2, 1)]   # 3 -> 0
    ],
    'not I': [
        [(-1, 0), (-1, 1), (0, -2), (-1, -2)],  # 0 -> 1
        [(1, 0), (1, -1), (0, 2), (1, 2)],  # 1 -> 2
        [(1, 0), (1, 1), (0, -2), (1, -2)],  # 2 -> 3
        [(-1, 0), (-1, -1), (0, 2), (-1, 2)]   # 3 -> 0
    ]
}
