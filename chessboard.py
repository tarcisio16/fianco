import numpy as np
from utils import init_table, compute_hash
from parameters import *

class Chessboard:
    # Movement and capture patterns
    MOVEMENT_DIRECTIONS_PLAYER1 = [(1, 0), (0, 1), (0, -1)]  # Down, Right, Left
    MOVEMENT_DIRECTIONS_PLAYER2 = [(-1, 0), (0, 1), (0, -1)]  # Up, Right, Left
    CAPTURE_PATTERNS_WHITE = [(2, 2), (2, -2)] # Diagonal captures
    CAPTURE_PATTERNS_BLACK = [(-2, 2), (-2, -2)] # Diagonal captures
    
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.initialize_pieces()
        self.player = 1
        self.legal_moves = set()
        self.capture = False
        self.table = init_table()

    def initialize_pieces(self):
        self.board[0, :] = WHITE_PIECE
        self.board[1, 1] = WHITE_PIECE
        self.board[1, 7] = WHITE_PIECE
        self.board[2, 2] = WHITE_PIECE
        self.board[2, 6] = WHITE_PIECE
        self.board[3, 3] = WHITE_PIECE
        self.board[3, 5] = WHITE_PIECE
        self.board[8, :] = BLACK_PIECE
        self.board[7, 1] = BLACK_PIECE
        self.board[7, 7] = BLACK_PIECE
        self.board[6, 2] = BLACK_PIECE
        self.board[6, 6] = BLACK_PIECE
        self.board[5, 3] = BLACK_PIECE
        self.board[5, 5] = BLACK_PIECE
        self.pl1 = set([(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,1),(1,7),(2,2),(2,6),(3,3),(3,5)])
        self.pl2 = set([(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8),(7,1),(7,7),(6,2),(6,6),(5,3),(5,5)])

    def move(self, player, movefrom, moveto):      
        self.legalmoves()

        move = (movefrom[0], movefrom[1], moveto[0], moveto[1])
        if move in self.legal_moves:
            if self.capture:
                mid_y = (movefrom[0] + moveto[0]) // 2
                mid_x = (movefrom[1] + moveto[1]) // 2
                self.board[mid_y, mid_x] = 0
                if player == 1:
                    self.pl2.remove((mid_y, mid_x))
                else:
                    self.pl1.remove((mid_y, mid_x))
                self.capture = False

            self.board[moveto[0], moveto[1]] = player
            self.board[movefrom[0], movefrom[1]] = 0

            if player == 1:
                self.pl1.remove((movefrom[0], movefrom[1]))
                self.pl1.add((moveto[0], moveto[1]))
            else:
                self.pl2.remove((movefrom[0], movefrom[1]))
                self.pl2.add((moveto[0], moveto[1]))

            self.player = 3 - self.player

    def legalmoves(self):
        self.legal_moves.clear()
        capture_moves = set()
        
        pieces = self.pl1 if self.player == 1 else self.pl2
        opponent = 2 if self.player == 1 else 1

        for (y, x) in pieces:
            capture_moves.update(self.check_captures(y, x, opponent))
            self.legal_moves.update(self.check_moves(y, x))

        if capture_moves:
            self.legal_moves = capture_moves
            self.capture = True
        else:
            self.capture = False

        return list(self.legal_moves)

    def check_captures(self, y, x, opponent):
        captures = set()
        capture_patterns = self.CAPTURE_PATTERNS_WHITE if opponent == 2 else self.CAPTURE_PATTERNS_BLACK
        for dy, dx in capture_patterns:
            ny, nx = y + dy, x + dx
            my, mx = y + dy // 2, x + dx // 2
            if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                if self.board[my, mx] == opponent and self.board[ny, nx] == 0:
                    captures.add((y, x, ny, nx))
        return captures

    def check_moves(self, y, x):
        moves = set()
        directions = self.MOVEMENT_DIRECTIONS_PLAYER1 if self.player == 1 else self.MOVEMENT_DIRECTIONS_PLAYER2
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE and self.board[ny, nx] == 0:
                moves.add((y, x, ny, nx))
        return moves
    
    def hash(self):
        return compute_hash(self.board, self.table, self.player)