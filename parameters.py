import numpy as np

BOARD_SIZE = 9
BLACK= 2
WHITE = 1
WHITE_PIECE = 1
BLACK_PIECE = 2

# Screen and Grid Sizes
WIDTH, HEIGHT = 1200, 700
MARGIN = 70
GRID_SIZE = 500
CELL_SIZE = GRID_SIZE // 8
FONT_SIZE = 30
BOARD_SIZE = 9
LETTERS = "ABCDEFGHI"

# Value Limits
MIN = 0
MAX = 2**64 - 1

R = 2

# Number of Players
NUMBER_OF_PLAYERS = 2

# Random Seed
SEED = 420420
WINNING_WHITES = ((8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8))
WINNING_BLACK = ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8))

ROW7 = ((7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8))
ROW1 = ((1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8))
ROW2 = ((2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8))
ROW6 = ((6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8))

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


LATERAL_DIRECTIONS = {(0, -1), (0, 1)}
FORWARD_DIRECTIONS = {WHITE: (1, 0), BLACK: (-1, 0)}
CAPTURED_PIECE_OFFSET = {WHITE: [(1, 1), (1, -1)], BLACK: [(-1, 1), (-1, -1)]}

feature_set1 = {"FIANCO_BONUS": 1,
                "POSITIONAL_BONUS": 2,
                "SECONDLASTBONUS": 10,
                "THIRDBONUS": 5}

np.random.seed(420)
ZOBRIST_ARRAY = np.random.randint(0, (2**63) -1, size=(BOARD_SIZE, BOARD_SIZE, 2), dtype=np.uint64)
ZOBRIST_PLAYER = np.random.randint(0, (2**63) -1, size=(2), dtype=np.uint64)

OPENING_BOOK_BLACK = [[8,0,7,0],[6,6,5,6],[8,4,7,4],[8,8,7,8],[6,2,4,0],[7,8,5,6],[4,3,2,5],[8,6,7,6], [5,5,3,7]]