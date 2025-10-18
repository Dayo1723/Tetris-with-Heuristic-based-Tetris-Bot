from library.tetrominos.tetromino import Tetromino


class OTetromino(Tetromino):
    def __init__(self):
        self.name = 'O'
        super().__init__([
            [
                [1, 1],
                [1, 1]
            ]
        ])

