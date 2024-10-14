import numpy as np

# Board Configuration
BOARD_SIZE = 9
BLACK = 2
WHITE = 1
WHITE_PIECE = WHITE
BLACK_PIECE = BLACK

# Screen and Grid Sizes
WIDTH = 1200
HEIGHT = 700
MARGIN = 70
GRID_SIZE = 500
CELL_SIZE = GRID_SIZE // 8
FONT_SIZE = 30
LETTERS = "ABCDEFGHI"

# Value Limits
MIN = 0
MAX = 2**64 - 1

# Number of Players
NUMBER_OF_PLAYERS = 2

# Random Seed
SEED = 420420

# Win Conditions (coordinates for winning rows)
WINNING_WHITES = (
    (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), 
    (8, 5), (8, 6), (8, 7), (8, 8)
)
WINNING_BLACK = (
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), 
    (0, 5), (0, 6), (0, 7), (0, 8)
)

# Specific Rows
ROW1 = (
    (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), 
    (1, 5), (1, 6), (1, 7), (1, 8)
)
ROW2 = (
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), 
    (2, 5), (2, 6), (2, 7), (2, 8)
)
ROW6 = (
    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), 
    (6, 5), (6, 6), (6, 7), (6, 8)
)
ROW7 = (
    (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), 
    (7, 5), (7, 6), (7, 7), (7, 8)
)

# Search Bounds
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

# Directions for Movement
LATERAL_DIRECTIONS = {(0, -1), (0, 1)}
FORWARD_DIRECTIONS = {WHITE: (1, 0), BLACK: (-1, 0)}
CAPTURED_PIECE_OFFSET = {
    WHITE: [(1, 1), (1, -1)],
    BLACK: [(-1, 1), (-1, -1)]
}

# Feature Set with Bonuses
feature_set1 = {
    "FIANCO_BONUS": 1,
    "POSITIONAL_BONUS": 2,
    "SECONDLASTBONUS": 10,
    "THIRDBONUS": 5
}

# Zobrist Hashing Initialization
np.random.seed(SEED)
ZOBRIST_ARRAY = np.random.randint(0, (2**63) - 1, size=(BOARD_SIZE, BOARD_SIZE, 2), dtype=np.uint64)
ZOBRIST_PLAYER = np.random.randint(0, (2**63) - 1, size=(2), dtype=np.uint64)

# Opening Book for Black (preset moves). Obtained naively from moves that caused the most beta cutoff  at the beginning with search deeper than in regular game.
OPENING_BOOK_BLACK = {
    (8, 0, 7, 0), (7, 0, 6, 0), (0, 4, 1, 4), (0, 7, 0, 8), (6, 6, 5, 6),
    (0, 2, 1, 2), (4, 0, 3, 0), (2, 2, 3, 2), (6, 2, 4, 4), (3, 5, 5, 3),
    (4, 5, 2, 7), (6, 6, 4, 4), (4, 3, 2, 1), (7, 3, 6, 3), (1, 2, 3, 0),
    (8, 6, 7, 6), (4, 3, 4, 4), (3, 3, 5, 5), (8, 8, 7, 8), (8, 3, 7, 3),
    (1, 4, 3, 6), (3, 3, 5, 1), (4, 3, 2, 5), (1, 6, 3, 8), (1, 6, 3, 4),
    (4, 5, 2, 3), (6, 2, 4, 0), (6, 1, 5, 1), (5, 6, 3, 8), (4, 3, 4, 2),
    (2, 1, 2, 2), (5, 8, 6, 8), (1, 2, 3, 4), (0, 1, 0, 2), (2, 1, 2, 0),
    (0, 1, 1, 1), (3, 5, 5, 7), (0, 7, 1, 7), (1, 0, 3, 2), (1, 8, 3, 6)
}

# Set of All Cells in the Board
ALL_CELLS = {(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)}