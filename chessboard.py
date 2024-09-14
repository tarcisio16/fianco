import numpy as np
from parameters import *
from collections import deque
import sys

class Chessboard:
    """ 
        Class to represent the state of the chessboard and game logic 

        Attributes:
        - white_pieces: Bitboard representing the positions of white pieces
        - black_pieces: Bitboard representing the positions of black pieces
        - empty_squares: Bitboard representing the empty squares
        - player: Current player's turn
        - legal_moves: Set of legal moves for the current player
        - previous: Deque to store the previous board states for undo functionality
        
    """
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
        self.empty_squares = (1 << (BOARD_SIZE * BOARD_SIZE)) - 1

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
        self.previous = deque(maxlen=MAX_HISTORY)
        
    def get_bitboard_position(self, y, x):
        return 1 << (y * BOARD_SIZE + x)

    def legalmoves(self):
        self.legal_moves.clear()
        capture_moves = set()
        directions = self.MOVEMENT_DIRECTIONS[self.player]
        capture_patterns = self.CAPTURE_PATTERNS[self.player]

        pieces = self.white_pieces if self.player == 1 else self.black_pieces
        opponent_pieces = self.black_pieces if self.player == 1 else self.white_pieces

        # Iterate over all pieces' bitboard
        while pieces:
            piece = pieces & -pieces  # Extract rightmost 1-bit
            pieces ^= piece  # Remove the bit from the bitboard

            piece_index = (piece.bit_length() - 1)  # Get the index of the bit
            y, x = divmod(piece_index, BOARD_SIZE)

            # Generate possible move and capture positions
            for dy, dx in directions:
                ny, nx = y + dy, x + dx
                if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                    move_pos = self.get_bitboard_position(ny, nx)
                    if self.empty_squares & move_pos:
                        self.legal_moves.add((y, x, ny, nx))

            for dy, dx in capture_patterns:
                ny, nx = y + dy, x + dx
                my, mx = y + dy // 2, x + dx // 2
                if 0 <= ny < BOARD_SIZE and 0 <= nx < BOARD_SIZE:
                    capture_pos = self.get_bitboard_position(ny, nx)
                    mid_pos = self.get_bitboard_position(my, mx)
                    if (opponent_pieces & mid_pos) and (self.empty_squares & capture_pos):
                        capture_moves.add((y, x, ny, nx))

        if capture_moves:
            self.legal_moves = capture_moves

    def undo(self):
        if self.previous:
            self.player ^= 3  # Switch back to the previous player

            # Retrieve the last bitboard differences
            white_diff, black_diff, empty_diff = self.previous.pop()

            # Apply the bitwise difference to reverse the board state
            self.white_pieces ^= white_diff
            self.black_pieces ^= black_diff
            self.empty_squares ^= empty_diff

            # Update legal moves after undo
            self.legalmoves()

    def move_no_check(self, player, y0, x0, y1, x1):
        white_initial, black_initial, empty_initial = self.white_pieces, self.black_pieces, self.empty_squares
        bit_pos_from, bit_pos_to = self.get_bitboard_position(y0, x0), self.get_bitboard_position(y1, x1)
        shift = bit_pos_from | bit_pos_to

        if player == 1:
            self.white_pieces ^= shift
        else:
            self.black_pieces ^= shift

        if abs(y1 - y0) == 2:
            mid_pos = self.get_bitboard_position((y0 + y1) // 2, (x0 + x1) // 2)
            if player == 1:
                self.black_pieces &= ~mid_pos
            else:
                self.white_pieces &= ~mid_pos
            self.empty_squares |= mid_pos

        self.empty_squares ^= shift
        self.previous.append((self.white_pieces ^ white_initial, self.black_pieces ^ black_initial, self.empty_squares ^ empty_initial))
        self.player ^= 3
        
    def check_winner(self):
        if self.white_pieces & 0x1FF000000:
            return 1
        if self.black_pieces & 0x1FF:
            return 2
        return 0
    def move(self, player, movefrom, moveto):
        bit_pos_from = self.get_bitboard_position(*movefrom)
        bit_pos_to = self.get_bitboard_position(*moveto)

        # Calculate initial state of bitboards before the move
        white_initial = self.white_pieces
        black_initial = self.black_pieces
        empty_initial = self.empty_squares

        # Perform the move (same as before)
        shift = bit_pos_from | bit_pos_to

        if (y0 := movefrom[0], x0 := movefrom[1], y1 := moveto[0], x1 := moveto[1]) in self.legal_moves:
            mid_y, mid_x = (y0 + y1) // 2, (x0 + x1) // 2
            if abs(y1 - y0) == 2:
                mid_pos = self.get_bitboard_position(mid_y, mid_x)

                if player == 1:
                    self.black_pieces ^= mid_pos  # Remove black piece
                else:
                    self.white_pieces ^= mid_pos  # Remove white piece

                self.empty_squares ^= mid_pos  # Update empty squares

            # Move the piece and update empty squares
            if player == 1:
                self.white_pieces ^= shift  # Move white piece
            else:
                self.black_pieces ^= shift  # Move black piece
            self.empty_squares ^= shift  # Update empty squares

            # Save the difference between the initial and final states of the bitboards
            white_diff = self.white_pieces ^ white_initial
            black_diff = self.black_pieces ^ black_initial
            empty_diff = self.empty_squares ^ empty_initial

            # Append the shifts to history for undo
            self.previous.append((white_diff, black_diff, empty_diff))

            # Switch player
            self.player ^= 3
            
            # Update legal moves
            self.legalmoves()

    def hash(self):
        return compute_hash(self.board, self.table, self.player)

    def get_piece_positions(self, player):
        bitboard = self.white_pieces if player == 1 else self.black_pieces
        positions = set()
        for bit in range(BOARD_SIZE ** 2):
            if bitboard & (1 << bit):
                y, x = divmod(bit, BOARD_SIZE)
                positions.add((y, x))
        return positions

    def display(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.white_pieces & self.get_bitboard_position(row, col):
                    print("W", end=" ")
                elif self.black_pieces & self.get_bitboard_position(row, col):
                    print("B", end=" ")
                else:
                    print(".", end=" ")
            print()
        print()

    def count_pieces(self, player):
        if player == 1:
            bitboard = self.white_pieces
        elif player == 2:
            bitboard = self.black_pieces
        else:
            raise ValueError("Invalid player number. Use 1 for white or 2 for black.")
    
        # Count the number of set bits in the bitboard
        return bin(bitboard).count('1')

    # def debug_script(self):
    #     print("white_pieces:", self.white_pieces)
    #     print("Size of white pieces:", sys.getsizeof(self.white_pieces), "bytes")
    #     print("Size of black pieces:", sys.getsizeof(self.black_pieces), "bytes")
    #     print("Dimensione in memoria di blank pieces:",sys.getsizeof(self.empty_squares), "bytes")
    #     print("dimensione in memoria di un array dei tre bitboard:", sys.getsizeof(np.array([self.white_pieces, self.black_pieces, self.empty_squares])), "bytes")
    #     print("Dimensione in memoria di player:", self.player.__sizeof__(), "bytes")
    #     print("legal_moves:", self.legal_moves)
    #     print("Dimensione in memoria di legal_moves:", self.legal_moves.__sizeof__(), "bytes")
    #     print("previous:", self.previous)
    #     print("Dimensione in memoria di previous:", self.previous.__sizeof__(), "bytes")