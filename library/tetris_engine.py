import time
from random import shuffle
from library.tetrominos.imports import tetromino_list, wall_kick_offsets
from library.tetrominos.block import Block
import pygame
import os
from pygame import mixer
from random import choice
from library.constants import GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT_INVISIBLE

pygame.mixer.init()

# Get the base directory where the current file (tetris_engine.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the path to the sounds folder inside the library
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")

landing_sound_path = os.path.join(SOUNDS_DIR, "landing.wav")
clear_sound_path = os.path.join(SOUNDS_DIR, "clear.wav")
error_sound_path = os.path.join(SOUNDS_DIR, "error.wav")
game_over_sound_path = os.path.join(SOUNDS_DIR, "game_over.wav")
rotate_sound_path = os.path.join(SOUNDS_DIR, "whoosh.mp3")
level_up_sound_path = os.path.join(SOUNDS_DIR, "level_up.wav")


landing_sound = mixer.Sound(landing_sound_path)
clear_sound = mixer.Sound(clear_sound_path)
game_over_sound = mixer.Sound(game_over_sound_path)
rotate_sound = mixer.Sound(rotate_sound_path)
level_up_sound = mixer.Sound(level_up_sound_path)
error_sound = mixer.Sound(error_sound_path)
error_sound.set_volume(0.3)
landing_sound.set_volume(0.2)
clear_sound.set_volume(0.1)
game_over_sound.set_volume(0.3)
level_up_sound.set_volume(0.3)
rotate_sound.set_volume(0.3)

playlist = [os.path.join(SOUNDS_DIR, "song1.wav"),
            os.path.join(SOUNDS_DIR, "song2.wav"),
            os.path.join(SOUNDS_DIR, "song3.wav"),
            os.path.join(SOUNDS_DIR, "tetris_theme.wav")]

mixer.music.load(choice(playlist))


def ms_now():
    return int(time.time() * 1000)


class TetrisEngine:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.game_level: int = None
        self.muted = False
        self.reset(start=False)  # sets the initial game conditions

    def is_muted(self):
        return self.muted

    def mute_unmute(self):
        if not self.muted:
            error_sound.set_volume(0)
            landing_sound.set_volume(0)
            clear_sound.set_volume(0)
            game_over_sound.set_volume(0)
            rotate_sound.set_volume(0)
            mixer.music.set_volume(0)
            self.muted = True
        else:
            error_sound.set_volume(0.3)
            landing_sound.set_volume(0.2)
            clear_sound.set_volume(0.1)
            game_over_sound.set_volume(0.3)
            rotate_sound.set_volume(0.3)
            mixer.music.set_volume(0.3)
            self.muted = False

    def set_game_level(self, game_level: int):
        if self.game_level != game_level:
            level_up_sound.set_volume(0.3)
            level_up_sound.play()
            self.game_level = game_level

    def get_game_level(self) -> int:
        return self.game_level

    def reset(self,start=True):  # Resets the game state to its initial conditions, including the game grid, score, level, and tetrominos.
        self.grid = [[None for _ in range(self.width)]
                     for _ in range(self.height)]
        self.bag = []
        shuffle(self.bag)
        self.last_game_tick_ms = 0
        self.game_score = 0
        self.game_lines_cleared = 0
        self.game_level = 0
        self.set_game_level(self.game_level)  # initialise level and speed
        self.game_is_over = False
        self.current_tetromino = None
        self.next_tetromino = None
        self.set_next_tetromino()
        if not self.is_muted():
            mixer.music.play(-1)
            mixer.music.set_volume(0.3)
        if start:
            self.start()

    def start(self):  # Initialize the game timer by setting the current time in milliseconds.
        self.last_game_tick_ms = ms_now()

    def get_current_game_tick_ms_T(self):
        # Starting interval in milliseconds
        base_interval = 1000

        # Apply the level multiplier to reduce the interval
        level_multiplier = 0.9 ** self.get_game_level()

        # Calculate the current interval
        game_speed_ms = int(base_interval * level_multiplier)

        # Ensure the interval doesn't go below a minimum threshold (e.g., 100ms)
        min_interval = 100
        return max(game_speed_ms, min_interval)

    def should_game_tick(self):  # Checks if enough time has passed to trigger the next game tick.
        now = ms_now()
        return now - self.last_game_tick_ms >= self.get_current_game_tick_ms_T()

    def skip_game_tick(self):  # Update the last game tick time to the current time, skipping any pending ticks.
        self.last_game_tick_ms = ms_now()

    def next_game_tick(self):  # If the game is over, do nothing. Otherwise, update the last game tick time and move the tetromino down.
        if self.game_is_over:
            return

        self.last_game_tick_ms = ms_now()
        self.tetromino_down()  # Move the tetromino down without playing the move sound effect.

    def set_next_tetromino(self):  # uses the 7-bag algorithm/piece generating system
        if not self.game_is_over:

            # Refill and shuffle the bag if its empty
            if not self.bag:
                self.refill_and_shuffle_bag()

            # Set the current

            self.current_tetromino = {
                'tetro': self.bag.pop(0)(),
                'x': self.width // 2 - 1,
                'y': 1
            }
            if not self.bag:
                self.refill_and_shuffle_bag()
                self.next_tetromino = self.bag[0]()
            else:
                self.next_tetromino = self.bag[0]()

            if self.current_tetromino and self.does_current_tetromino_collide() and self.is_current_tetromino_in_spawn_area():
                self.game_is_over = True
                game_over_sound.play()
                mixer.music.stop()
                return

            # Skip the game tick to ensure no missed ticks after setting the new tetromino.
            self.skip_game_tick()

    def refill_and_shuffle_bag(self):
        self.bag = [tetromino_type for tetromino_type in tetromino_list]
        shuffle(self.bag)

    def unpack_current_tetromino(self):
        # Extract and return the tetromino instance and its position (x, y) from the current_tetromino dictionary.
        tetro = self.current_tetromino['tetro']
        tx = self.current_tetromino['x']
        ty = self.current_tetromino['y']
        return tetro, tx, ty

    def is_current_tetromino_in_spawn_area(self) -> bool:
        # Retrieve the current tetromino and its position on the grid.
        tetro, tx, ty = self.unpack_current_tetromino()
        # Get the grid representation of the current tetromino.
        tetro_grid = tetro.current_grid()

        # Iterate through each cell of the tetromino's grid.
        for y in range(tetro.height()):
            for x in range(tetro.width()):
                # Check if the cell is occupied and if the tetromino is in the spawn area (top GRID_HEIGHT_INVISIBLE rows).
                if tetro_grid[y][x] and ty < GRID_HEIGHT_INVISIBLE:
                    return True

        # If no occupied cells are in the spawn area, return False.
        return False

    def does_current_tetromino_collide(self) -> bool:
        # Checks if the current tetromino collides with the game grid or goes out of bounds.

        # Unpack the current tetromino and its position
        tetro, tx, ty = self.unpack_current_tetromino()
        tetro_grid = tetro.current_grid()

        # Iterate over each cell in the tetromino's grid
        for y in range(tetro.height()):
            for x in range(tetro.width()):

                # Calculate the absolute grid coordinates
                gx = tx + x
                gy = ty + y

                # Skip if the current cell of the tetromino is empty
                if not tetro_grid[y][x]:
                    continue

                # Check if the cell is out of grid bounds
                out_of_bounds = gx < 0 or gx >= self.width or gy < 0 or gy >= self.height

                # Check if the cell collides with an already occupied cell in the grid or is out of bounds
                if out_of_bounds or self.grid[gy][gx]:
                    return True  # Return True if collision detected

        return False  # Return False if no collision is detected

    def is_row_full(self, row: int) -> bool:
        # Checks if a specific row in the grid is completely filled with tetrominos.

        # Iterate over each column in the specified row
        for x in range(self.width):
            # If any cell in the row is empty
            if not self.grid[row][x]:
                return False  # Return False as the row is not full

        # Return True if all cells in the row are filled
        return True

    def remove_row(self, row: int):
        # Clears the specified row and shifts all rows above it down by one position.

        # Continue processing until all rows above the specified row are handled
        while row >= 0:
            # Iterate over each column in the current row
            for x in range(self.width):
                # Remove the content of the current cell by setting it to None
                self.grid[row][x] = None
                # If there is a row above the current row, move its content down
                if row - 1 >= 0:
                    self.grid[row][x] = self.grid[row - 1][x]
            # Move to the row above
            row -= 1

            clear_sound.play()

    def break_full_rows(self):
        # Scans the grid from bottom to top, clears any full rows, and shifts the rows above down.

        # Start from the bottom row
        y = self.height - 1

        # Counter for consecutive full rows
        lines_combo = 0

        while y >= 0:
            if self.is_row_full(y):  # Check if the row is full
                self.remove_row(y)  # Remove the full row
                lines_combo += 1  # Increment combo counter
            else:
                y -= 1  # Move to the next row
                if lines_combo > 0:
                    self.apply_lines_cleared(lines_combo)  # Update score and level
                    lines_combo = 0  # Reset combo counter

    def apply_lines_cleared(self, lines_cleared: int):
        self.game_score += self.calculate_break_rows_score(lines_cleared)
        self.game_lines_cleared += lines_cleared
        self.set_game_level(self.game_lines_cleared // 10)

    def calculate_break_rows_score(self, lines_combo: int) -> int:

        # Define the score multipliers for clearing 0 to 4 lines.
        lines_multiplier = [0, 40, 100, 300, 1200]  # 1 2 3 and 4

        # Return the score. Higher levels result in higher scores for the same number of lines cleared.
        return lines_multiplier[lines_combo] * (self.get_game_level() + 1)

    def lock_current_tetromino_into_grid(self):
        # This method locks the current tetromino into the main game grid, marking its cells as occupied by setting their color.

        # Unpack the current tetromino's properties: the tetromino object itself and its position on the grid (tx, ty).
        tetro, tx, ty = self.unpack_current_tetromino()

        # Get the current grid configuration of the tetromino.
        tetro_grid = tetro.current_grid()

        # Iterate through each cell in the tetromino's grid.
        for y in range(tetro.height()):
            for x in range(tetro.width()):
                # If the current cell in the tetromino's grid is occupied,
                # lock this cell into the main game grid at the corresponding position.
                if tetro_grid[y][x]:
                    self.grid[ty + y][tx + x] = Block(tetro.name)

        landing_sound.play()
        self.break_full_rows()  # Once the tetromino has been locked into the right position, clear any completed rows.

    def tetromino_down(self):
        if not self.game_is_over:

            # Skip the game tick to ensure this action is processed immediately.
            self.skip_game_tick()

            # Move the current tetromino down by increasing its y-coordinate.
            self.current_tetromino['y'] += 1

            # Check if the tetromino collides with the grid or other tetrominos.
            if collides := self.does_current_tetromino_collide():

                # Move the tetromino back up by decreasing its y-coordinate.
                self.current_tetromino['y'] -= 1

                self.lock_current_tetromino_into_grid()
                self.set_next_tetromino()

            # Return whether a collision occurred.
            return collides

    def tetromino_left(self):
        if not self.game_is_over:

            self.current_tetromino['x'] -= 1
            if collides := self.does_current_tetromino_collide():
                self.current_tetromino['x'] += 1
            return collides

    def tetromino_right(self):
        if not self.game_is_over:

            self.current_tetromino['x'] += 1
            if collides := self.does_current_tetromino_collide():
                self.current_tetromino['x'] -= 1

            return collides

    def tetromino_rotate(self):
        if not self.game_is_over:

            tetromino = self.current_tetromino['tetro']
            tetromino.rotate()  # rotates the current tetromino

            if collides := self.does_current_tetromino_collide():
                tetromino.rotate(backward=True)  # if it causes a collision, undo the rotation
                if not self.attempt_wall_kick(tetromino):  # now attempt to wall kick the piece
                    return collides  # return whether the wall kick failed (fail -> True, succeeded -> False)

            rotate_sound.play()

    def attempt_wall_kick(self, tetromino):

        # get the name of the current tetromino (e.g. 'L', 'Z')
        tetromino_type = tetromino.name

        # if the tetromino type is an 'O' piece, do not attempt to wall kick
        if tetromino_type == 'O':
            return False

        # get the rotation index of the current tetromino (0-3)
        rot_index = tetromino.current_rotation_i()

        if tetromino_type == 'I':
            wall_kick_data = wall_kick_offsets['I'][rot_index]  # get the wall kick data for the 'I' piece
        else:
            wall_kick_data = wall_kick_offsets['not I'][rot_index]  # get the wall kick data for the other pieces

        for offset in wall_kick_data:  # iterates through each offset in the wall kick data

            self.current_tetromino['x'] += offset[0]  # applies the x offset
            self.current_tetromino['y'] += offset[1]  # applies the y offset

            tetromino.rotate()  # rotate the tetromino in its new position

            if not self.does_current_tetromino_collide():  # if it doesn't collide, exit the algorithm.
                return True  # the tetromino has been wall-kicked successfully

            self.current_tetromino['tetro'].rotate(backward=True)  # the attempt has failed
            self.current_tetromino['x'] -= offset[0]  # return the tetromino to its original position
            self.current_tetromino['y'] -= offset[1]

        # if all offsets have been applied unsuccessfully, return False
        # this indicates that the wall kick attempt has failed
        return False

    def harddrop(self):
        if not self.game_is_over:
            while not self.tetromino_down():
                pass

    def dynamic_grid(self):

        # Create a copy of the grid to render, initializing with the current grid state.
        dynamic_grid = [[self.grid[i][j] for j in range(self.width)]
                       for i in range(self.height)]

        # Unpack the current tetromino to get its properties.
        tetro, tx, ty = self.unpack_current_tetromino()
        tetro_grid = tetro.current_grid()

        # If the game is not over, update the render grid with the current tetromino's positions.
        if not self.game_is_over:
            for y in range(tetro.height()):
                for x in range(tetro.width()):
                    gx = tx + x
                    gy = ty + y
                    if tetro_grid[y][x] and gx >= 0 and gy >= 0 and gx < self.width and gy < self.height:
                        dynamic_grid[gy][gx] = Block(tetro.name)

        return dynamic_grid
