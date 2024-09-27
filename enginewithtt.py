import logging
import numpy as np
from board import Board
import sys
from parameters import *
import time 

logging.basicConfig(filename='engine.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TTengine():
    
    def __init__(self, board, player) -> None:
        self.board = board
        self.player = player
        self.player_at_turn = player
        self.tt = np.zeros((TTSIZE, 2), dtype=np.uint64)  # 64-bit entry: |depth (4)|flag (3)|sign (1)|value (40)|move (16)|
        self.hits = self.turn = self.nodes = 0

    def retrieve_tt(self, zobrist):
        entry = self.tt[int(zobrist) & TTMASK]
        return int(entry[1]) if entry[0] == zobrist else None

    def store_tt(self, zobrist, depth, value, move, alpha, beta):
        flag = LOWERBOUND if value >= beta else UPPERBOUND if value <= alpha else EXACT
        sign = 1 if value < 0 else 0
        value = abs(value)
        packed = (depth << 60) | (flag << 57) | (sign << 56) | (value << 16) | (move[0] << 12) | (move[1] << 8) | (move[2] << 4) | move[3]
        index = int(zobrist) & TTMASK
        self.tt[index] = [np.uint64(zobrist), np.uint64(packed)]

    def negamax(self, depth, alpha, beta, zobrist):
        self.nodes += 1
        ttmove = None
        olda = alpha
        ttvalue_packed = self.retrieve_tt(zobrist)

        if ttvalue_packed is not None:
            self.hits += 1
            tt_depth = (ttvalue_packed >> 60) & 0xF
            if tt_depth >= depth:
                tt_value = (ttvalue_packed >> 16) & 0xFFFFFFFFFF
                tt_value = -tt_value if (ttvalue_packed >> 56) & 0x1 else tt_value
                tt_flag = (ttvalue_packed >> 57) & 0b111
                if tt_flag == EXACT: return tt_value
                alpha, beta = (max(alpha, tt_value), beta) if tt_flag == LOWERBOUND else (alpha, min(beta, tt_value))
                if alpha >= beta: return tt_value

        if depth == 0:
            return self.evaluation_function(self.board, self.player_at_turn)        

        if ttvalue_packed is not None and tt_depth >= 0:
            ttmove = (ttvalue_packed >> 12) & 0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0XF, ttvalue_packed & 0xF
            self.board.move(self.player_at_turn, *ttmove)
            self.player_at_turn = 3 - self.player_at_turn
            zobrist_move = self.board.zobrist_move(zobrist, self.player_at_turn  , ttmove)
            best_value = -self.negamax(depth - 1, -beta, -alpha,zobrist_move)
            self.player_at_turn = 3 - self.player_at_turn
            self.board.undomove(self.player_at_turn, *ttmove)   
            bestmove = ttmove
            if best_value >= beta:
                self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                return best_value

        best_value = -10000

        for move in self.board.generate_moves(self.player_at_turn):
            
            if ttmove is not None and move == ttmove:
                continue
            self.board.move(self.player_at_turn, *move)
            self.player_at_turn = 3 - self.player_at_turn
            zobrist_move = self.board.zobrist_move(zobrist, self.player_at_turn  , move)
            value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
            self.player_at_turn = 3 - self.player_at_turn
            self.board.undomove(self.player_at_turn, *move)

            if value > best_value:
                best_value = value
                bestmove = move
                if best_value >= beta:
                    self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)

        return best_value
    
    def negamax_root(self, board, depth, alpha, beta):
        self.hits = self.nodes = 0
        self.turn += 1
        best_value, best_move = -100000, None
        zobrist = board.zobrist_hash(self.player)
        for move in board.generate_moves(self.player):
            board.move(self.player, *move)
            self.player_at_turn = 3 - self.player_at_turn
            zobrist_move = board.zobrist_move(zobrist, self.player_at_turn  , move)
            value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
            self.player_at_turn = 3 - self.player_at_turn
            board.undomove(self.player, *move)

            if value > best_value:
                best_value, best_move = value, move
            alpha = max(alpha, value)
            if alpha >= beta: break

        return best_move

    def negamax_iterative_deepening(self, board, max_depth, alpha, beta):
        self.hits = self.nodes = 0
        best_move = None
        zobrist = board.zobrist_hash(self.player)
        for depth in range(1, max_depth + 1):
            best_value, current_best_move = -1000000, None
            
            for move in board.generate_moves(self.player):
                board.move(self.player, *move)
                self.player_at_turn = 3 - self.player_at_turn
                zobrist_move = board.zobrist_move(zobrist, self.player_at_turn, move)
                value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
                self.player_at_turn = 3 - self.player_at_turn
                board.undomove(self.player, *move)

                if value > best_value:
                    best_value, current_best_move = value, move
                alpha = max(alpha, value)
                if alpha >= beta: break
            best_move = current_best_move

        return best_move
        

    def evaluation_function(self, board, player):
        score = 0

        def positional_score(pieces, opponent_pieces, is_white):
            positional_value = 0
            for row, col in pieces:
                if (is_white and row == 8) or (not is_white and row == 0):
                    positional_value += 100
                if (is_white and row == 7) or (not is_white and row == 1):
                    positional_value += 2 * POSITIONAL_BONUS
                if 3 <= col <= 5:
                    positional_value += CENTRAL_BONUS
                advancement = row if is_white else 8 - row
                positional_value += advancement * POSITIONAL_BONUS

            return positional_value
        
        is_white = (player == WHITE)

        player_pieces = board.white_pieces if is_white else board.black_pieces
        opponent_pieces = board.black_pieces if is_white else board.white_pieces
        score += (len(player_pieces) - len(opponent_pieces)) *  PIECE_BONUS
        score += positional_score(player_pieces, opponent_pieces, is_white)

        return score

if __name__ == "__main__":
    engine = TTengine(Board(), 1)
    move = engine.negamax_root(engine.board, 4, -10000, 10000)
    print(sys.getsizeof(engine.tt)/(1024*1024), "MB" ) 