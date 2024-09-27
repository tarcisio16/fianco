BOARD_SIZE = 9

BLACK= 2
WHITE = 1

MAX_QUEUE_SIZE = 40


# AI Settings
DELAY_AI = 1

# Screen and Grid Sizes
WIDTH, HEIGHT = 1000, 700
MARGIN = 70
GRID_SIZE = 500
CELL_SIZE = GRID_SIZE // 8

# Font and Board Sizes
FONT_SIZE = 30
BOARD_SIZE = 9
LETTERS = "ABCDEFGHI"

# Piece Types
WHITE_PIECE = 1
BLACK_PIECE = 2

# AI Best Value
BEST_VALUE = -100

# Move History
MAX_HISTORY = 30



# Value Limits
MIN = 0
MAX = 2**64 - 1

# Number of Players
NUMBER_OF_PLAYERS = 2

# Random Seed
SEED = 420

WINNING_WHITES = ((8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8))
WINNING_BLACK = ((0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8))

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

POSITIONAL_BONUS = 2
CENTRAL_BONUS = 1
PIECE_BONUS = 10