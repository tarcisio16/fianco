import numpy as np
from parameters import *
from collections import deque

class Board:

    def __init__(self):
        self.player = WHITE
        self.previous = deque(maxlen=MAX_QUEUE_SIZE)
        self.previous_capture = deque(maxlen=MAX_QUEUE_SIZE)
        self.legalmoves = set()
        self.capture = False
        self.white_pieces = set({(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,1),(1,7),(2,2),(2,6),(3,3),(3,5)})
        self.black_pieces = set({(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8),(7,1),(7,7),(6,2),(6,6),(5,3),(5,5)})
        np.random.seed(1604)
        self.zobrist = np.random.randint(0, (2**63) -1, size=(BOARD_SIZE, BOARD_SIZE, 2), dtype=np.uint64) 


    def __str__(self) -> str:
        board = np.full((BOARD_SIZE, BOARD_SIZE), '-', dtype=str)
        for y,x in self.white_pieces:
            board[y,x] = 'w'
        for y,x in self.black_pieces:
            board[y,x] = 'b'
        return str(board)

    def generate_moves(self,player):
        capture = False
        current_pieces = self.white_pieces if player == WHITE else self.black_pieces
        opponent_pieces = self.black_pieces if player == WHITE else self.white_pieces

        mov_dir = 1 if player == WHITE else -1

        for piece in current_pieces:
            y, x = piece
            for dy, dx in [(mov_dir, 1), (mov_dir, -1)]:
                if (y + dy, x + dx) in opponent_pieces:
                    jump_y, jump_x = y + 2 * dy, x + 2 * dx
                    if 0 <= jump_y < BOARD_SIZE and 0 <= jump_x < BOARD_SIZE and (jump_y, jump_x) not in current_pieces and (jump_y, jump_x) not in opponent_pieces:
                        capture = True
                        yield (y, x, jump_y, jump_x)

        for piece in current_pieces:
            y, x = piece
            if capture:
                break
            forward_y = y + mov_dir
            if 0 <= forward_y < BOARD_SIZE and (forward_y, x) not in current_pieces and (forward_y, x) not in opponent_pieces:
                yield (y, x, forward_y, x)

        for piece in current_pieces:
            y, x = piece
            if capture:
                break
            for dx in [-1, 1]:
                lateral_x = x + dx
                if 0 <= lateral_x < BOARD_SIZE and (y, lateral_x) not in current_pieces and (y, lateral_x) not in opponent_pieces:
                    yield (y, x, y, lateral_x)
    
    def legal_moves(self,player):
        self.legalmoves.clear()  # Clear previous legal moves
        self.capture = False  # Reset capture flag

        # Set the current player's pieces and the opponent's pieces
        current_pieces = self.white_pieces if player == WHITE else self.black_pieces
        opponent_pieces = self.black_pieces if player == WHITE else self.white_pieces

        # Move direction: White moves down the board, Black moves up
        move_dir = 1 if player == WHITE else -1

        for piece in current_pieces:
            y, x = piece

            # Check for captures (must jump over opponent diagonally)
            for dy, dx in [(move_dir, 1), (move_dir, -1)]:
                if (y + dy, x + dx) in opponent_pieces:  # Check if an opponent's piece is adjacent
                    jump_y, jump_x = y + 2 * dy, x + 2 * dx  # Calculate the jump position
                    if 0 <= jump_y < BOARD_SIZE and 0 <= jump_x < BOARD_SIZE and (jump_y, jump_x) not in current_pieces and (jump_y, jump_x) not in opponent_pieces:
                        self.capture = True
                        self.legalmoves.add((y, x, jump_y, jump_x))

        for piece in current_pieces:
            y, x = piece
            if self.capture:
                break
            forward_y = y + move_dir
            if 0 <= forward_y < BOARD_SIZE and (forward_y, x) not in current_pieces and (forward_y, x) not in opponent_pieces:
                self.legalmoves.add((y, x, forward_y, x))
            for dx in [-1, 1]:
                lateral_x = x + dx
                if 0 <= lateral_x < BOARD_SIZE and (y, lateral_x) not in current_pieces and (y, lateral_x) not in opponent_pieces:
                    self.legalmoves.add((y, x, y, lateral_x))

    def check_move(self,move):
        if move in self.legalmoves:
            return True
        return False

    def move(self,player, y1, x1, y2, x2):
        if player == WHITE:
            self.white_pieces.remove((y1, x1))
            self.white_pieces.add((y2, x2))
            if abs(y1 - y2) == 2:  # Capture move
                captured = ((y1 + y2) // 2, (x1 + x2) // 2)
                self.black_pieces.remove(captured)
                self.previous_capture.append(captured)
            else:
                self.previous_capture.append((-1, -1))  
        else:
            self.black_pieces.remove((y1, x1))
            self.black_pieces.add((y2, x2))
            if abs(y1 - y2) == 2:  # Capture move
                captured = ((y1 + y2) // 2, (x1 + x2) // 2)
                self.white_pieces.remove(captured)
                self.previous_capture.append(captured)
            else:
                self.previous_capture.append((-1, -1)) 

        self.previous.append((y1, x1, y2, x2))


    def undomove(self,player, y1, x1, y2, x2):
        if player == WHITE:
            self.white_pieces.remove((y2, x2))
            self.white_pieces.add((y1, x1))
            if abs(y1 - y2) == 2:
                captured = ((y1 + y2) // 2, (x1 + x2) // 2)
                self.black_pieces.add(captured)
        else:
            self.black_pieces.remove((y2, x2))
            self.black_pieces.add((y1, x1))
            if abs(y1 - y2) == 2:
                captured = ((y1 + y2) // 2, (x1 + x2) // 2)
                self.white_pieces.add(captured)

        self.previous.pop()

    def movecheck(self,player, y1,x1,y2,x2):
        move = (y1,x1,y2,x2)
        if self.check_move(move):
            self.move(player,y1,x1,y2,x2)
            self.player ^= 3

    def checkwin(self):
        if self.white_pieces.intersection(WINNING_WHITES) or len(self.black_pieces) == 0:
            return 1
        elif self.black_pieces.intersection(WINNING_BLACK) or len(self.white_pieces) == 0:
            return 2
        return 0

    def undo_check(self):
        if len(self.previous) == 0:
            return False
        else:
            self.player ^= 3
            self.undo(self.player)

    def undo(self,player):
        y1,x1,y2,x2 = self.previous.pop()
        y_,x_ = self.previous_capture.pop()
        if player == WHITE:
            self.white_pieces.remove((y2,x2))
            self.white_pieces.add((y1,x1))
            if y_ != -1:
                self.black_pieces.add((y_,x_))
        else:
            self.black_pieces.remove((y2,x2))
            self.black_pieces.add((y1,x1))
            if y_ != -1:
                self.white_pieces.add((y_,x_))

    def zobrist_hash(self, player):
        key = np.uint64(0)
        for y, x in self.white_pieces:
            key ^= self.zobrist[y, x, 0]  # Use the 0 index for white pieces
        for y, x in self.black_pieces:
            key ^= self.zobrist[y, x, 1]  # Use the 1 index for black pieces
        key ^= np.uint64(player)  # XOR the player to incluxde turn information
        return key




    





        
        