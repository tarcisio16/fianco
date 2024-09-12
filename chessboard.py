import numpy as np
from utils import init_table, compute_hash
from parameters import *
from collections import deque

class Chessboard:
    # Movement and capture patterns
    MOVEMENT_DIRECTIONS_PLAYER1 = [(1, 0), (0, 1), (0, -1)]  # Down, Right, Left
    MOVEMENT_DIRECTIONS_PLAYER2 = [(-1, 0), (0, 1), (0, -1)]  # Up, Right, Left
    CAPTURE_PATTERNS_WHITE = [(2, 2), (2, -2)] # Diagonal captures
    CAPTURE_PATTERNS_BLACK = [(-2, 2), (-2, -2)] # Diagonal captures
    
    def __init__(self):
        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        self.initialize_pieces()
        self.player = 1
        self.legal_moves = set()
        self.capture = False
        self.table = init_table()
        self.previous = deque(maxlen=MAX_HISTORY)
        self.previous_capture = deque(maxlen=MAX_HISTORY)

    def initialize_pieces(self):
        self.board[0, :] = WHITE_PIECE
        self.board[1, [1, 7]] = WHITE_PIECE  
        self.board[2, [2, 6]] = WHITE_PIECE
        self.board[3, [3, 5]] = WHITE_PIECE
        self.board[8, :] = BLACK_PIECE
        self.board[7, [1, 7]] = BLACK_PIECE
        self.board[6, [2, 6]] = BLACK_PIECE
        self.board[5, [3, 5]] = BLACK_PIECE
        self.pl1 = set([(0, i) for i in range(9)] + [(1, 1), (1, 7), (2, 2), (2, 6), (3, 3), (3, 5)])
        self.pl2 = set([(8, i) for i in range(9)] + [(7, 1), (7, 7), (6, 2), (6, 6), (5, 3), (5, 5)])

    def legal_moves_piece(self,  y, x):
        moves = -np.ones(6, dtype=np.int8)

        # Verifica a chi appartiene il pezzo e definisce le direzioni
        if self.board[y, x] == 1 and self.player == 1:
            opponent, forward_step, capture_step = 2, 1, 2
        elif self.board[y, x] == 2 and self.player == 2:
            opponent, forward_step, capture_step = 1, -1, -2
        else:
            return moves

        # Verifica le catture disponibili
        if self._check_capture(moves, y, x, opponent, forward_step, capture_step):
            return moves

        # Se nessuna cattura è disponibile, verifica i movimenti normali
        self._check_regular_moves(moves, y, x, forward_step)

        return moves

    def _check_capture(self, moves,  y,  x,  opponent, forward_step,  capture_step):
        """ Controlla e aggiunge eventuali catture alla lista delle mosse. """
        capture_found = False

        if 0 <= y + capture_step < BOARD_SIZE:
            # Diagonale destra
            if (0 <= x + capture_step < BOARD_SIZE and 
                self.board[y + forward_step, x + 1] == opponent and self.board[y + capture_step, x + capture_step] == 0):
                moves[0], moves[1] = y + capture_step, x + capture_step
                capture_found = True

            # Diagonale sinistra
            if (0 <= x - capture_step < BOARD_SIZE and 
                self.board[y + forward_step, x - 1] == opponent and self.board[y + capture_step, x - capture_step] == 0):
                if moves[0] != -1:
                    moves[2], moves[3] = y + capture_step, x - capture_step
                else:
                    moves[0], moves[1] = y + capture_step, x - capture_step
                capture_found = True

        return capture_found

    def _check_regular_moves(self, moves,  y,  x,  forward_step):
        """ Controlla e aggiunge i movimenti regolari alla lista delle mosse. """
        # Movimento avanti
        if 0 <= y + forward_step < BOARD_SIZE and self.board[y + forward_step, x] == 0:
            moves[0], moves[1] = y + forward_step, x

        # Movimento laterale destra
        if 0 <= x + 1 < BOARD_SIZE and self.board[y, x + 1] == 0:
            if moves[0] != -1:
                moves[2], moves[3] = y, x + 1
            else:
                moves[0], moves[1] = y, x + 1

        # Movimento laterale sinistra
        if 0 <= x - 1 < BOARD_SIZE and self.board[y, x - 1] == 0:
            if moves[0] != -1 and moves[2] != -1:
                moves[4], moves[5] = y, x - 1
            else:
                moves[2], moves[3] = y, x - 1 if moves[0] != -1 else y, x - 1
    
    def move(self, player, movefrom, moveto):
        y0, x0, y1, x1 = movefrom[0], movefrom[1], moveto[0], moveto[1]      
        self.legalmoves()

        if (y0, x0, y1, x1) in self.legal_moves:
            self.previous.append((y0, x0, y1, x1))
            if self.capture:
                mid_y = (y0+y1) // 2
                mid_x = (x0+x1) // 2
                self.previous_capture.append((mid_y, mid_x))
                self.board[mid_y, mid_x] = 0
                if player == 1:
                    self.pl2.remove((mid_y, mid_x))
                else:
                    self.pl1.remove((mid_y, mid_x))
                self.capture = False
            else:
                self.previous_capture.append((-1, -1))
            self.board[y1, x1] = player
            self.board[y0, x0] = 0

            if player == 1:
                self.pl1.remove((y0, x0))
                self.pl1.add((y1, x1))
            else:
                self.pl2.remove((y0, x0))
                self.pl2.add((y1, x1))

            self.player = 3 - self.player

            self.tocalculate = True

    def undo(self):
        if self.previous:
            # Retrieve the last move
            y0, x0, y1, x1 = self.previous.pop()
            mid_y, mid_x = self.previous_capture.pop()
            
            # Move the piece back to its original position
            self.board[y0, x0] = self.board[y1, x1]
            self.board[y1, x1] = 0  # Clear the position where the piece moved
            
            # Handle the captured piece restoration
            if mid_y != -1:  # If there was a capture
                # Restore the captured piece
                self.board[mid_y, mid_x] = 3 - self.board[y0, x0]  # Restore opponent's piece
                
                # Update piece sets (pl1, pl2)
                if self.board[mid_y, mid_x] == 1:
                    self.pl1.add((mid_y, mid_x))  # Restore piece to player 1's set
                else:
                    self.pl2.add((mid_y, mid_x))  # Restore piece to player 2's set
            
            # Update the current player’s piece set to reflect the move back
            if self.player == 2:
                self.pl1.add((y0, x0))
                self.pl1.discard((y1, x1))  # Remove from the destination
            else:
                self.pl2.add((y0, x0))
                self.pl2.discard((y1, x1))
            
            # Switch player back to the one who made the move
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