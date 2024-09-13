import numpy as np
from utils import init_table, compute_hash
from parameters import *
from collections import deque

class Chessboard:
    # Movement and capture patterns
    MOVEMENT_DIRECTIONS = {
        1: [(1, 0), (0, 1), (0, -1)],  # Player 1: Down, Right, Left
        2: [(-1, 0), (0, 1), (0, -1)]  # Player 2: Up, Right, Left
    }
    CAPTURE_PATTERNS = {
        1: [(2, 2), (2, -2)],  # White: Diagonal captures
        2: [(-2, 2), (-2, -2)]  # Black: Diagonal captures
    }

    def __init__(self):
        self.white_pieces = 0
        self.black_pieces = 0
        self.empty_squares = (1 << (BOARD_SIZE * BOARD_SIZE)) - 1  # All squares initially empty

        # Initialize pieces
        for col in range(BOARD_SIZE):
            self.white_pieces |= self.get_bitboard_position(0, col)
            self.empty_squares &= ~self.get_bitboard_position(0, col)
            self.black_pieces |= self.get_bitboard_position(8, col)
            self.empty_squares &= ~self.get_bitboard_position(8, col)
        
        additional_white_positions = [(1, 1), (1, 7), (2, 2), (2, 6), (3, 3), (3, 5)]
        additional_black_positions = [(7, 1), (7, 7), (6, 2), (6, 6), (5, 3), (5, 5)]
        for pos in additional_white_positions:
            self.white_pieces |= self.get_bitboard_position(*pos)
            self.empty_squares &= ~self.get_bitboard_position(*pos)
        for pos in additional_black_positions:
            self.black_pieces |= self.get_bitboard_position(*pos)
            self.empty_squares &= ~self.get_bitboard_position(*pos)

        self.empty_squares &= ~(self.white_pieces | self.black_pieces)

        self.player = 1
        self.legal_moves = set(INITIAL_LEGAL_MOVES)
        self.capture = False
        self.table = init_table()
        self.previous = deque(maxlen=MAX_HISTORY)
        self.previous_capture = deque(maxlen=MAX_HISTORY)

    def get_bitboard_position(self, y, x):
        return 1 << (y * BOARD_SIZE + x)

    def move_no_check(self, player, movefrom, moveto):
        y0, x0, y1, x1 = movefrom[0], movefrom[1], moveto[0], moveto[1]
        bit_pos_from = self.get_bitboard_position(y0, x0)
        bit_pos_to = self.get_bitboard_position(y1, x1)

        if player == 1:
            self.white_pieces = (self.white_pieces & ~bit_pos_from) | bit_pos_to
        else:
            self.black_pieces = (self.black_pieces & ~bit_pos_from) | bit_pos_to

        if abs(y1 - y0) == 2:
            mid_y = (y0 + y1) // 2
            mid_x = (x0 + x1) // 2
            mid_pos = self.get_bitboard_position(mid_y, mid_x)
            if player == 1:
                self.black_pieces &= ~mid_pos
            else:
                self.white_pieces &= ~mid_pos
            self.empty_squares |= mid_pos
        else:
            self.previous_capture.append((-1, -1))

        self.empty_squares |= bit_pos_from
        self.empty_squares &= ~bit_pos_to

        self.player = 3 - self.player

    def move(self, player, movefrom, moveto):
        y0, x0, y1, x1 = movefrom[0], movefrom[1], moveto[0], moveto[1]
        bit_pos_from = self.get_bitboard_position(y0, x0)
        bit_pos_to = self.get_bitboard_position(y1, x1)

        print(f"Making move from {movefrom} to {moveto}")
        print(f"Bit positions: from={bit_pos_from:064b}, to={bit_pos_to:064b}")

        self.legalmoves()

        if (y0, x0, y1, x1) in self.legal_moves:
            self.previous.append((y0, x0, y1, x1))

            if self.capture:
                mid_y = (y0 + y1) // 2
                mid_x = (x0 + x1) // 2
                mid_pos = self.get_bitboard_position(mid_y, mid_x)
                if player == 1:
                    self.black_pieces &= ~mid_pos
                else:
                    self.white_pieces &= ~mid_pos
                self.empty_squares |= mid_pos
                self.capture = False
                self.previous_capture.append((mid_y, mid_x))
            else:
                self.previous_capture.append((-1, -1))

            if player == 1:
                self.white_pieces = (self.white_pieces & ~bit_pos_from) | bit_pos_to
            else:
                self.black_pieces = (self.black_pieces & ~bit_pos_from) | bit_pos_to

            self.empty_squares |= bit_pos_from
            self.empty_squares &= ~bit_pos_to

            self.player = 3 - self.player
            self.tocalculate = True

        print(f"Updated white pieces bitboard: {self.white_pieces:064b}")
        print(f"Updated black pieces bitboard: {self.black_pieces:064b}")
        print(f"Updated empty squares bitboard: {self.empty_squares:064b}")

    def legalmoves(self):
        self.legal_moves.clear()
        capture_moves = set()

        pieces = self.white_pieces if self.player == 1 else self.black_pieces
        opponent_pieces = self.black_pieces if self.player == 1 else self.white_pieces
        directions = self.MOVEMENT_DIRECTIONS[self.player]
        capture_patterns = self.CAPTURE_PATTERNS[self.player]

        for bit in range(BOARD_SIZE ** 2):
            if pieces & (1 << bit):
                y, x = divmod(bit, BOARD_SIZE)
                piece_capture_found = False

                for dy, dx in capture_patterns:
                    ny, nx = y + dy, x + dx
                    my, mx = y + dy // 2, x + dx // 2
                    if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                        capture_pos = self.get_bitboard_position(ny, nx)
                        mid_pos = self.get_bitboard_position(my, mx)
                        if opponent_pieces & mid_pos and self.empty_squares & capture_pos:
                            capture_moves.add((y, x, ny, nx))
                            piece_capture_found = True
                            break

                if not piece_capture_found:
                    for dy, dx in directions:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                            move_pos = self.get_bitboard_position(ny, nx)
                            if self.empty_squares & move_pos:
                                self.legal_moves.add((y, x, ny, nx))

        if capture_moves:
            self.legal_moves = capture_moves
            self.capture = True
        else:
            self.capture = False

        return list(self.legal_moves)

    def get_piece_positions(self, player):
        bitboard = self.white_pieces if player == 1 else self.black_pieces
        positions = set()
        for bit in range(BOARD_SIZE ** 2):
            if bitboard & (1 << bit):
                y, x = divmod(bit, BOARD_SIZE)
                positions.add((y, x))
        return positions

    def hash(self):
        return compute_hash(self.board, self.table, self.player)

    def undo(self):
        if self.previous and self.previous_capture:
            self.player = 3 - self.player
            y0, x0, y1, x1 = self.previous.pop()
            mid_y, mid_x = self.previous_capture.pop()
            bit_pos_from = self.get_bitboard_position(y0, x0)
            bit_pos_to = self.get_bitboard_position(y1, x1)

            if self.player == 1:
                self.white_pieces = (self.white_pieces | bit_pos_from) & ~bit_pos_to
            else:
                self.black_pieces = (self.black_pieces | bit_pos_from) & ~bit_pos_to

            self.empty_squares |= bit_pos_to
            self.empty_squares &= ~bit_pos_from

            if mid_y != -1:
                mid_pos = self.get_bitboard_position(mid_y, mid_x)
                if self.player == 1:
                    self.black_pieces |= mid_pos
                else:
                    self.white_pieces |= mid_pos
                self.empty_squares &= ~mid_pos