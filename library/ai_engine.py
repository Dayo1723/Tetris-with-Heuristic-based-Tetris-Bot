from library.tetris_engine import TetrisEngine


class AITetrisEngine(TetrisEngine):
    def __init__(self):
        super().__init__()
        self.ls = 2  # line score
        self.hp = -3  # hole penalty
        self.bp = -0.5  # bumpiness penalty
        self.mhp = -0.6  # maximum height penalty
        self.ahp = -0.6  # aggregate height penalty
        self.wp = -0.15  # well penalty

    def calculate_bumpiness(self, grid):

        def column_height(x):
            # Return the height of the column at index x
            for y in range(self.height):
                if grid[y][x] != 0:
                    return self.height - y
            return 0

        bumpiness = 0
        for x in range(self.width - 1):
            h1 = column_height(x)
            h2 = column_height(x + 1)
            bumpiness += abs(h1 - h2)

        return bumpiness

    def calculate_holes(self, grid):
        holes = 0

        for x in range(self.width):
            hole_found = False  # Flag to detect holes after the first filled cell
            for y in range(self.height):
                if grid[y][x]:
                    hole_found = True  # A filled cell was found, now look for holes
                elif hole_found and not grid[y][x]:
                    holes += 1  # Empty cell below a filled cell, it's a hole

        return holes

    def calculate_line_clears(self, grid):
        lines_cleared = 0

        for y in range(self.height):
            if all(cell != 0 for cell in grid[y]):
                lines_cleared += 1

        return lines_cleared

    def calculate_aggregate_height(self, grid):
        aggregate_height = 0

        for x in range(self.width):
            column_height = 0
            for y in range(self.height):
                if grid[y][x] != 0:  # If there's a block in the column
                    column_height = self.height - y  # Calculate height from the bottom
                    break  # Stop once we find the highest block in the column
            aggregate_height += column_height

        return aggregate_height

    def calculate_max_height(self, grid):
        max_height = 0
        for x in range(self.width):
            for y in range(self.height):
                if grid[y][x] != 0:
                    max_height = max(max_height, self.height - y)
                    break

        return max_height

    def calculate_well_depth(self, grid):

        well_depth_score = 0

        for x in range(self.width):  # Iterate through each column
            depth = 0
            for y in range(self.height - 1, -1, -1):  # Iterate from bottom to top
                if grid[y][x] == 0:  # Empty cell
                    depth += 1
                else:  # Blocked cell
                    break

            well_depth_score += depth

        return well_depth_score

    def evaluate(self, grid):

        line_scr = self.ls * self.calculate_line_clears(grid)
        hole_pen = self.hp * self.calculate_holes(grid)
        bumpiness_pen = self.bp * self.calculate_bumpiness(grid)
        max_height_pen = self.mhp * self.calculate_max_height(grid)
        agg_h_pen = self.ahp * self.calculate_aggregate_height(grid)
        well_pen = self.wp * self.calculate_well_depth(grid)

        score = line_scr + bumpiness_pen + agg_h_pen + well_pen + max_height_pen + hole_pen

        return score

    def generate_best_move(self):

        evals = []

        original_x = self.current_tetromino['x']
        original_y = self.current_tetromino['y']
        original_rot_i = self.current_tetromino['tetro'].current_rotation_i()

        # Iterate over all possible rotations of the tetromino
        for rotation_count in range(self.current_tetromino['tetro'].defined_rotations()):

            # Set the tetromino to the current rotation
            self.current_tetromino['tetro'].set_rotation_i(rotation_count)

            # Try all positions moving left
            while self.ai_try_left():
                pass

            while self.ai_try_down():
                pass

            grid = self.dynamic_grid()
            array = [[1 if cell else 0 for cell in row] for row in grid]  # convert occupied cells in the array to 1s for simplicity

            # Append the game state along with rotation index and x-coordinate
            evals.append(
                (self.evaluate(array), rotation_count, self.current_tetromino['x'], self.current_tetromino['y']))

            # Reset y-position after dropping the piece
            self.current_tetromino['y'] = original_y

            # Try all positions moving right
            while self.ai_try_right():
                while self.ai_try_down():
                    pass

                grid = self.dynamic_grid()
                array = [[1 if cell else 0 for cell in row] for row in grid]

                # Append the game state along with rotation index and x-coordinate
                evals.append(
                    (self.evaluate(array), rotation_count, self.current_tetromino['x'], self.current_tetromino['y']))

                # Reset y-position after each right move and drop
                self.current_tetromino['y'] = original_y

            # Restore the original rotation and x position
            self.current_tetromino['tetro'].set_rotation_i(original_rot_i)
            self.current_tetromino['x'] = original_x

        best_eval = max(evals, key=lambda x: x[0])

        return best_eval[1], best_eval[2], best_eval[3]

    def ai_try_down(self):

        # Move the tetromino down.
        self.current_tetromino['y'] += 1

        # Check if the tetromino collides with the grid.
        if collides := self.does_current_tetromino_collide():
            # If there is a collision, move the tetromino back up to its original position.
            self.current_tetromino['y'] -= 1

        # Return True if there was no collision (the move was successful), otherwise return False.
        return not collides

    def ai_try_left(self):

        self.current_tetromino['x'] -= 1

        if collides := self.does_current_tetromino_collide():
            self.current_tetromino['x'] += 1

        return not collides

    def ai_try_right(self):

        self.current_tetromino['x'] += 1
        if collides := self.does_current_tetromino_collide():
            self.current_tetromino['x'] -= 1
        return not collides

    def ai_try_rotate(self):

        self.current_tetromino['tetro'].rotate()

        if collides := self.does_current_tetromino_collide():
            self.current_tetromino['tetro'].rotate(backward=True)

        return not collides





