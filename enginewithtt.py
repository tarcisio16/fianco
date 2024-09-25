from engine import Engine
from board import Board
import logging
import numpy as np
import sys 
from parameters import *


logging.basicConfig(filename='engine.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TTengine(Engine):

    
    def __init__(self, board, player) -> None:
        super().__init__(board, player)
        self.tt = np.zeros((2**23, 2), dtype=np.uint64)
        self.hits = 0
        # 64 BIT ENTRY
        # |4 BIT DEPTH| | 3 BIT FLAG |1 BIT SIGN | 40 BIT VALUE|16 BIT MOVE|

    def retrieve_tt(self, zobrist):
        zobrist_index = int(zobrist) & 0x7FFFFF
        if self.tt[zobrist_index][0] == zobrist:
            return self.tt[zobrist_index][1]
        else:
            return None

    def storett(self, zobrist, depth, value, bestmove, olda, beta):
        
        if value <= olda:
            flag = UPPERBOUND
        elif value >= beta:
            flag = LOWERBOUND
        else:
            flag = EXACT
        sign = 0
        if value < 0:
            value = abs(value)
            sign = 1
        
        zobrist_index = int(zobrist) & 0x7FFFFF
        packed = ((depth << 60) | (flag << 57) | (sign << 56) | (value << 16) | bestmove[0] << 12 | bestmove[1] << 8 | bestmove[2] << 4 | bestmove[3])
        self.tt[zobrist_index][0] = np.uint64(zobrist)
        self.tt[zobrist_index][1] = np.uint64(packed)

    def negamax(self, depth, alpha, beta):
        ttmove = None
        olda = alpha
        zobrist = self.board.zobrist_hash(self.player_at_turn)
        ttvalue_packed = self.retrieve_tt(zobrist)

        if ttvalue_packed is not None:
            logging.debug(f"TT Hit: {self.hits}")
            self.hits += 1
            ttvalue_packed = int(ttvalue_packed)  # Ensure we have an int for bitwise operations
            ttdepth = (ttvalue_packed >> 60) & 0xF
            ttflag = (ttvalue_packed >> 57) & 0b111
            ttsign = (ttvalue_packed >> 56) & 0x1
            ttvalue = ttvalue_packed >> 16 & 0xFFFFFFFFFF
            ttmove = (ttvalue_packed >> 12 ) &  0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0xF, ttvalue_packed & 0xF

            if ttsign == 1:
                ttvalue = -ttvalue

        if depth == 0 or self.board.checkwin():
            return super().evaluation_function(self.board, self.player_at_turn)        

        if ttvalue_packed is not None and ttdepth >= depth:
            ttmove = (ttvalue_packed >> 12) & 0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0XF, ttvalue_packed & 0xF
            self.board.move(self.player_at_turn, *ttmove)
            self.player_at_turn = 3 - self.player_at_turn
            ttvalue = -self.negamax(depth - 1, -beta, -alpha)
            self.player_at_turn = 3 - self.player_at_turn
            self.board.undo(self.player_at_turn)
            bestmove = ttmove
            if ttvalue >= beta:
                self.storett(zobrist, depth, ttvalue, bestmove, olda, beta)
                return ttvalue

        best_value = -10000

        for move in self.board.generate_moves(self.player_at_turn):
            if ttmove is not None and move == ttmove:
                continue
            self.board.move(self.player_at_turn, *move)
            self.player_at_turn = 3 - self.player_at_turn
            value = -self.negamax(depth - 1, -beta, -alpha)
            self.player_at_turn = 3 - self.player_at_turn
            self.board.undo(self.player_at_turn)

            if value > best_value:
                best_value = value
                bestmove = move
                alpha = max(alpha, value)

                if alpha >= beta:

                    zobrist = self.board.zobrist_hash(self.player_at_turn)
                    self.storett(zobrist, depth, best_value, bestmove, olda, beta)
                    break

        return best_value



if __name__ == "__main__":
    # Create a board object
    board = Board()

    # Create an engine object
    engine = TTengine(board, player=WHITE)
    # Call the negamax function with desired depth, alpha, and beta values
    best_value = engine.negamax(depth=5, alpha=-10000, beta=10000)
