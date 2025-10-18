from typing import List
from library.base_types import TetrominoGrid


class Tetromino:
    def __init__(self, grid_rotations: List[TetrominoGrid]):
        self.grid_rotations = grid_rotations  # List of possible rotations for the Tetromino
        self.rotation = 0  # Start with the first rotation state

    def width(self) -> int:
        return len(self.current_grid()[0])

    def height(self) -> int:
        return len(self.current_grid())

    def defined_rotations(self) -> int:
        return len(self.grid_rotations)  # get the number of rotation states associated with the given tetromino

    def set_rotation_i(self, rotation):
        self.rotation = rotation

    def current_rotation_i(self) -> int:
        return self.rotation % len(self.grid_rotations)  # returns the tetromino's current rotation state (e.g. 0, 1, 2)

    def current_grid(self) -> TetrominoGrid:
        return self.grid_rotations[self.rotation % len(
            self.grid_rotations)]  # retrieves the grid that represents the Tetromino’s current rotation state

    def rotate(self, backward=False) -> None:
        self.rotation += 1 if not backward else -1

