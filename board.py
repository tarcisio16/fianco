import numpy as np
from parameters import *
from collections import deque

LATERAL_DIRECTIONS = {(0, -1), (0, 1)}
FORWARD_DIRECTIONS = {WHITE: (1, 0), BLACK: (-1, 0)}
CAPTURED_PIECE_OFFSET = {WHITE: [(1, 1), (1, -1)], BLACK: [(-1, 1), (-1, -1)]}
ALL_SQUARES = set((y, x) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE))
        
FIANCO_BONUS = 8
POSITIONAL_BONUS = 5
SECONDLASTBONUS = 100
PIECE_BONUS = 20

class Board:

    def __init__(self):
        self.player = WHITE
        self.legalmoves = set()
        self.white_pieces = set({(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,1),(1,7),(2,2),(2,6),(3,3),(3,5)})
        self.black_pieces = set({(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8),(7,1),(7,7),(6,2),(6,6),(5,3),(5,5)})
        np.random.seed(42069)
        self.zobrist = np.random.randint(0, (2**63) -1, size=(BOARD_SIZE, BOARD_SIZE, 2), dtype=np.uint64) 
        self.zobrist_player = np.random.randint(0, (2**63) -1, size=(2), dtype=np.uint64)


    def generate_moves(self, player, sorted_moves=False, capture=False):
        if sorted_moves:
            current_pieces = sorted(self.white_pieces, key=lambda item: item[0], reverse=True) if player == WHITE else sorted(self.black_pieces, key=lambda item: item[0], reverse=True)
        else:
            current_pieces = self.white_pieces if player == WHITE else self.black_pieces
        opponent_pieces = self.black_pieces if player == WHITE else self.white_pieces
        
        for piece in current_pieces:
            for capture_offset in CAPTURED_PIECE_OFFSET[player]:
                captured_piece = add_tuples(piece, capture_offset)
                new_pos = add_tuples(piece, add_tuples(capture_offset, capture_offset))
                if 0 <= new_pos[0] < BOARD_SIZE and 0 <= new_pos[1] < BOARD_SIZE and captured_piece in opponent_pieces and  new_pos not in current_pieces and new_pos not in opponent_pieces:
                    capture = True
                    yield (*piece, *new_pos)

        if not capture:
            for piece in current_pieces:
                new_pos = add_tuples(piece, FORWARD_DIRECTIONS[player])
                if 0 <= new_pos[0] < BOARD_SIZE and new_pos not in current_pieces and new_pos not in opponent_pieces:
                    yield (*piece, *new_pos)
                for offset in LATERAL_DIRECTIONS:
                    new_pos = add_tuples(piece, offset)
                    if 0 <= new_pos[1] < BOARD_SIZE and new_pos not in current_pieces and new_pos not in opponent_pieces:
                        yield (*piece, *new_pos)

    def move(self,player, y1, x1, y2, x2):
        pieces = self.white_pieces if player == WHITE else self.black_pieces
        opponent_pieces = self.black_pieces if player == WHITE else self.white_pieces

        pieces.remove((y1, x1))
        pieces.add((y2, x2))
        if abs(y1 - y2) == 2:
            opponent_pieces.remove((((y1 + y2) // 2, (x1 + x2) // 2)))


    def undomove(self,player, y1, x1, y2, x2):
        pieces = self.white_pieces if player == WHITE else self.black_pieces
        opponent_pieces = self.black_pieces if player == WHITE else self.white_pieces
        pieces.remove((y2, x2))
        pieces.add((y1, x1))
        if abs(y1 - y2) == 2:
            captured = ((y1 + y2) // 2, (x1 + x2) // 2)
            opponent_pieces.add(captured)
                
    def checkwin(self):
        if self.white_pieces.intersection(WINNING_WHITES) or len(self.black_pieces) == 0:
            return 1
        elif self.black_pieces.intersection(WINNING_BLACK) or len(self.white_pieces) == 0:
            return 2
        return 0

    def zobrist_hash(self, player):
        key = np.uint64(0)
        for y, x in self.white_pieces:
            key ^= self.zobrist[y, x, 0]
        for y, x in self.black_pieces:
            key ^= self.zobrist[y, x, 1]
        key ^= self.zobrist_player[player - 1]
        return key

    def zobrist_move(self,zobrist,player,move):
        
        player = 1 if player == WHITE else 0
        opponent = 1 - player
        
        zobrist ^= self.zobrist_player[opponent]
        zobrist ^= self.zobrist_player[player]
        
        zobrist ^= self.zobrist[move[0], move[1], player]
        zobrist ^= self.zobrist[move[2], move[3], player]

        
        if abs(move[0] - move[2]) == 2:
            zobrist ^= self.zobrist[(move[0] + move[2]) // 2, (move[1] + move[3]) // 2, opponent]
        return zobrist

    def movecheck(self,player, y1,x1,y2,x2):
        move = (y1,x1,y2,x2)
        if move in list(self.generate_moves(self.player)):
            self.move(player,y1,x1,y2,x2)
            self.player ^= 3

    def __repr__(self) -> str:
        np_board = [["-" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for y, x in self.white_pieces:
            np_board[y][x] = "W"
        for y, x in self.black_pieces:
            np_board[y][x] = "B"
        return "\n".join(" ".join(row) for row in np_board)

    def can_capture(self, player, piece):
        for capture_offset in CAPTURED_PIECE_OFFSET[player]:
            captured_piece = add_tuples(piece, capture_offset)
            new_pos = add_tuples(piece, add_tuples(capture_offset, capture_offset))
            if 0 <= new_pos[0] < BOARD_SIZE and 0 <= new_pos[1] < BOARD_SIZE and captured_piece in self.black_pieces and new_pos not in self.white_pieces and new_pos not in self.black_pieces:
                return True
        return False
        
    def obstacles(self, player, piece,empty_squares):
        y,x = piece
        if x == 0:
            if player == WHITE:
                if y == 7:
                    return empty_squares.intersection({(8, 0), (8, 1)})
                if y == 6:
                    return empty_squares.intersection({(8, 0), (8, 1), (8, 2),(7,0),(7,1)})
                if y == 5:
                    return empty_squares.intersection({(8, 0), (8, 1), (8, 2),(8,3), (7,0),(7,1),(7,2),(6,0),(6,1)})
            if player == BLACK:
                if y == 1:
                    return empty_squares.intersection({(0, 0), (0, 1)})
                if y == 2:
                    return empty_squares.intersection({(0, 0), (0, 1), (0, 2),(1,0),(1,1)})
                if y == 3:
                    return empty_squares.intersection({(0, 0), (0, 1), (0, 2),(0,3), (1,0),(1,1),(1,2),(2,0),(2,1)})
        if x == 1:
            if player == WHITE:
                if y == 7:
                    return empty_squares.intersection({(8,0),(8, 1), (8, 2)})
                if y == 6:
                    return empty_squares.intersection({(8,0),(8, 1), (8, 2), (8, 3), (7,0), (7, 1), (7, 2)})
                if y == 5:
                    return empty_squares.intersection({(8,0),(8, 1), (8, 2), (8, 3), (8, 4), (7,0), (7, 1), (7, 2), (7, 3), (6,0), (6, 1), (6, 2)})
            if player == BLACK:
                if y == 1:
                    return empty_squares.intersection({(0, 0), (0, 1), (0, 2)})
                if y == 2:
                    return empty_squares.intersection({(0,0),(0, 1), (0, 2), (0, 3),(1,0),(1,1),(1,2)})
                if y == 3:
                    return empty_squares.intersection({(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)})
        if x == 2:
            if player == WHITE:
                if y == 7:
                    return empty_squares.intersection({(8,1),(8, 2), (8, 3)})
                if y == 6:
                    return empty_squares.intersection({(8,0),(8,1),(8, 2), (8, 3), (8, 4), (7,1), (7, 2), (7, 3)})
                if y == 5:
                    return empty_squares.intersection({(8,0),(8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (6, 1), (6, 2), (6, 3)})
            if player == BLACK:
                if y == 1:
                    return empty_squares.intersection({(0, 1), (0, 2), (0, 3)})
                if y == 2:
                    return empty_squares.intersection({(0,0),(0,1),(0, 2), (0, 3), (0, 4),(1,1),(1,2),(1,3)})
                if y == 3:
                    return empty_squares.intersection({(0,0),(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1,0), (1, 1), (1, 2), (1, 3),(1,4) ,(2,1), (2, 2), (2, 3)})
        if 2 < x < 6:
            if player == WHITE:
                if y == 7:
                    return empty_squares.intersection({(8, x), (8, x+1), (8, x-1)})
                if y == 6:
                    return empty_squares.intersection({(8, x), (8, x+1), (8, x-1), (8, x-2), (8, x+2), (7, x), (7, x+1), (7, x-1)})
                if y == 5:
                    return empty_squares.intersection({(8, x), (8, x+1), (8, x-1),(8,x-2), (8,x+2), (8,x-3), (8,x+3), (7, x), (7, x+1), (7, x-1), (7, x-2), (7, x+2), (6, x), (6, x+1), (6, x-1)})
            if player == BLACK:
                if y == 1:
                    return empty_squares.intersection({(0, x), (0, x+1), (0, x-1)})
                if y == 2:
                    return empty_squares.intersection({(0, x), (0, x+1), (0, x-1), (0, x-2), (0, x+2), (1, x), (1, x+1), (1, x-1)})
                if y == 3:
                    return empty_squares.intersection({(0, x), (0, x+1), (0, x-1),(0,x-2), (0,x+2), (0,x-3), (0,x+3), (1, x), (1, x+1), (1, x-1), (1, x-2), (1, x+2), (2, x), (2, x+1), (2, x-1)})
        if x == 7:
            if player == WHITE:
                if y == 7:
                    return empty_squares.intersection({(8,5),(8, 6), (8, 7)})
                if y == 6:
                    return empty_squares.intersection({(8,5),(8, 6), (8, 7), (8, 8), (7, 6), (7, 7), (7, 8)})
                if y == 5:
                    return empty_squares.intersection({((8,8),(8,7),(8,6),(8,5),(8,4),(7,8),(7,7),(7,6),(7,5),(6,8),(6,7),(6,6))})
            if player == BLACK:
                if y == 1:
                    return empty_squares.intersection({(0, 5), (0, 6), (0, 7)})
                if y == 2:
                    return empty_squares.intersection({(0, 5), (0, 6), (0, 7), (0, 8), (1, 6), (1, 7), (1, 8)})
                if y == 3:
                    return empty_squares.intersection({(0,4),(0, 5), (0, 6), (0, 7), (0, 8), (1,5),(1, 6), (1, 7), (1, 8), (2, 7), (2, 8), (2, 6)})

        if x == 6:
            if player == WHITE:
                if y == 7:
                    return empty_squares.intersection({(8,5),(8, 6), (8, 7)})
                if y == 6:
                    return empty_squares.intersection({(8,4),(8, 5), (8, 6), (8, 7), (8, 8), (7, 5), (7, 6), (7, 7)})
                if y == 5:
                    return empty_squares.intersection({(8,3),(8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (7, 4), (7, 5), (7, 6), (7, 7),(7,8), (6, 4), (6, 5), (6, 6)})
            if player == BLACK:
                if y == 1:
                    return empty_squares.intersection({(0, 4), (0, 5), (0, 6)})
                if y == 2:
                    return empty_squares.intersection({(0, 4), (0, 5), (0, 6), (0, 7), (1, 5), (1, 6), (1, 7)})
                if y == 3:
                    return empty_squares.intersection({(0,3),(0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, 5), (2, 6), (2, 7)})
        if x == 8:
            if player == WHITE:
                if y == 7:
                    return empty_squares.intersection({(8, 8), (8, 7)})
                if y == 6:
                    return empty_squares.intersection({(8, 8), (8, 7), (8, 6),(7,8),(7,7)})
                if y == 5:
                    return empty_squares.intersection({(8, 8), (8, 7), (8, 6),(8,5), (7,8),(7,7),(7,6),(6,8),(6,7)})
            if player == BLACK:
                if y == 1:
                    return empty_squares.intersection({(0, 8), (0, 7)})
                if y == 2:
                    return empty_squares.intersection({(0, 8), (0, 7), (0, 6),(1,8),(1,7)})
                if y == 3:
                    return empty_squares.intersection({(0, 8), (0, 7), (0, 6),(0,5), (1,8),(1,7),(1,6),(2,8),(2,7)})

    def evaluation_function(self, player):
        empty_squares = ALL_SQUARES - self.white_pieces - self.black_pieces
        white_score = sum(
            y * POSITIONAL_BONUS + (FIANCO_BONUS if x in (0, 8) else 0) + (1000000 if y == 8 else 0) + (SECONDLASTBONUS if y == 7 else 0) + (FIANCO_BONUS // 2 if x in (1, 7) else 0) #+ 1000000 if not self.obstacles(WHITE, (y, x), empty_squares) else 0
            for y, x in self.white_pieces
        )
        black_score = sum(
            (BOARD_SIZE - y - 1) * POSITIONAL_BONUS + (FIANCO_BONUS if x in (0, 8) else 0) + (1000000 if y == 0 else 0) + (SECONDLASTBONUS if y == 1 else 0) + (FIANCO_BONUS // 2 if x in (1, 7) else 0) #+ 1000000 if not self.obstacles(BLACK, (y, x), empty_squares) else 0
            for y, x in self.black_pieces
        )

        return white_score - black_score if player == WHITE else black_score - white_score

    

def add_tuples(t1, t2):
    return (t1[0] + t2[0], t1[1] + t2[1])
