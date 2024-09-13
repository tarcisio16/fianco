
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

TYPE_OF_GAME =  0 # 0: "human VS human" 
                   # 1: "ai VS ai" 
                   # 2: "ai vs human"
DELAY_AI = 0.2

WIDTH, HEIGHT = 700, 700
MARGIN = 70
GRID_SIZE = 500
CELL_SIZE = GRID_SIZE // 8
FONT_SIZE = 30
BOARD_SIZE = 9
LETTERS = "ABCDEFGHI"

WHITE_PIECE = 1
BLACK_PIECE = 2

MAX_HISTORY = 30   # Maximum number of moves to store in history

INITIAL_LEGAL_MOVES = {(0, 6, 1, 6), (0, 8, 1, 8), (2, 6, 2, 5), (2, 2, 3, 2), (1, 1, 1, 2), (2, 6, 3, 6), (0, 3, 1, 3), (2, 2, 2, 3), (0, 5, 1, 5), (1, 7, 1, 6), (0, 0, 1, 0), (2, 6, 2, 7), (0, 4, 1, 4), (3, 3, 3, 2), (3, 5, 3, 4), (1, 7, 2, 7), (1, 1, 1, 0), (1, 7, 1, 8), (3, 3, 4, 3), (3, 5, 4, 5), (0, 2, 1, 2), (2, 2, 2, 1), (3, 3, 3, 4), (3, 5, 3, 6), (1, 1, 2, 1)}