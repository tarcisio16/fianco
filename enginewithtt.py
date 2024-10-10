import numpy as np
from board import Board
from parameters import *
import time

class TTengine():
    
    def __init__(self, board, player,feature_set, transposition_table_size = 26) -> None:
        self.board = board
        self.player = player
        self.player_at_turn = player
        self.tt = np.zeros((2 ** transposition_table_size, 2), dtype=np.uint64)  # 64-bit entry: |depth (4)|flag (3)|sign (1)|value (40)|move (16)|
        self.hits = self.turn = self.nodes = self.depth = self.turn = 0
        self.mask = (1 << transposition_table_size) - 1 
        self.fiancobonus = feature_set["FIANCO_BONUS"]
        self.positionalbonus = feature_set["POSITIONAL_BONUS"]
        self.secondlastbonus = feature_set["SECONDLASTBONUS"]
        self.thirdbonus = feature_set["THIRDBONUS"]
        self.piecebonus = feature_set["PIECE_BONUS"]
        self.feature_set = feature_set
        

    def retrieve_tt(self, zobrist):
        entry = self.tt[int(zobrist) & self.mask]
        hash = entry[0]
        if hash == zobrist:
            return int(entry[1]) 
        return None

    def store_tt(self, zobrist, depth, value, move, alpha, beta):
        flag = LOWERBOUND if value >= beta else UPPERBOUND if value <= alpha else EXACT
        sign = 1 if value < 0 else 0
        value = abs(value)
        packed = (depth << 60) | (flag << 57) | (sign << 56) | (value << 16) | (move[0] << 12) | (move[1] << 8) | (move[2] << 4) | move[3]
        index = int(zobrist) & self.mask
        self.tt[index] = [np.uint64(zobrist), np.uint64(packed)]

    def next_turn(self):
        self.turn += 1
        self.hits = self.nodes = 0


    def move_negamax(self,player,move, alpha, beta, depth, zobrist):
        self.board.move(player,*move)
        self.player_at_turn  ^= 3
        value = -self.negamax(depth - 1, -beta, -alpha, self.board.zobrist_move(zobrist, self.player_at_turn, move))
        self.player_at_turn = player
        self.board.undomove(player,*move)
        return value

    def timeup(self, start, max_time):
        return time.time() - start > max_time
    
    def evaluation_function(self, player):
        positional_bonus = self.positionalbonus
        fianco_bonus = self.fiancobonus
        piece_bonus = self.piecebonus
        second_last_bonus = self.secondlastbonus
        board_size = BOARD_SIZE

        def calculate_score(pieces, is_white):
            score = 0
            for y, x in pieces:
                if is_white:
                    positional_score = (y + 1) * positional_bonus
                    if y == 7:
                        positional_score += second_last_bonus
                    if y == 6:
                        positional_score += self.thirdbonus
                else:
                    positional_score = (board_size - y) * positional_bonus
                    if y == 1:
                        positional_score += second_last_bonus
                    if y == 2:
                        positional_score += self.thirdbonus

                if x in (0, 8):
                    positional_score += fianco_bonus

                score += positional_score
            return score

        white_score = calculate_score(self.board.white_pieces, True) 
        black_score = calculate_score(self.board.black_pieces, False) 

        # Return the score difference based on the current player
        return white_score - black_score if player == WHITE else black_score - white_score

def getvalue(ttvalue_packed):
    return -((ttvalue_packed >> 16) & 0xFFFFFFFFFF) if (ttvalue_packed >> 56) & 0x1 else (ttvalue_packed >> 16) & 0xFFFFFFFFFF

