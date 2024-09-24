from board import Board
from parameters import *
import numpy as np
from collections import deque
import sys
from copy import deepcopy
import logging

logging.basicConfig(filename='engine.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


class Engine:

    def __init__(self, board, player) -> None:
        self.board = board
        self.player = player
        self.principal_variation = deque(maxlen=MAX_QUEUE_SIZE)
        self.player_at_turn = player
        self.tt = np.zeros((2**23,3), dtype=np.uint16)
        self.bestmove = None


    def evaluation_function(self, board, player):
        score = 0
        winner = board.checkwin()
        if winner == player:
            return 10000
        elif winner == 3 - player:
            return -10000

        if player == WHITE:
            score += (len(board.white_pieces) - len(board.black_pieces))*5
            for piece in board.white_pieces:
                score += piece[0] **2
            for piece in board.black_pieces:
                score -= 8 - piece[0]
        else:
            score += (len(board.black_pieces) - len(board.white_pieces))*5
            for piece in board.black_pieces:
                score += (8 - piece[0])** 2

            for piece in board.white_pieces:
                score -= piece[0]

        return score

    def negamax_root(self, board, depth, alpha, beta):
        """Negamax root function to be called for the top-level search."""
        values = []
        best_value = -sys.maxsize  # Initialize best value to negative infinity
        best_move = None
        board.legal_moves(self.player)  # Get the available legal moves
        legal_moves = deepcopy(board.legalmoves)  # Deepcopy the legal moves

        for move in legal_moves: 
            board.move(self.player,*move)  # Make the move
            self.player_at_turn = 3 - self.player_at_turn  # Switch player
            value = -self.negamax( depth - 1, -beta, -alpha)  # Recursively call negamax
            self.player_at_turn = 3 - self.player_at_turn  # Switch player
            board.undo(self.player)  # Undo the move
            values.append(value)  # Append the value to the values list
            if value > best_value:
                best_value = value
                best_move = move
                alpha = max(alpha, value)  # Update alpha

            if alpha >= beta:
                break  # Beta cutoff, stop search

        logging.debug("values: %s", values)
        return best_move  # Return the best move and its value



    def negamax(self,depth, alpha,beta):
        olda = alpha
        zobrist = self.board.zobrist_hash(self.player_at_turn)
        ttentry = self.retrieve_tt(zobrist)

        if ttentry is not None:
            ttflag, ttdepth, ttvalue = ttentry[1], ttentry[2] >> 2, ttentry[2] >> 7
            if ttdepth >= depth:
                if ttflag == EXACT: return ttvalue
                elif ttflag == LOWERBOUND: alpha = max(alpha, ttvalue)
                else: beta = min(beta, ttvalue)
                if alpha >= beta: return ttvalue
        if depth == 0:
            return self.evaluation_function(self.board,self.player_at_turn)

        best_value = -sys.maxsize
        self.board.legal_moves(self.player_at_turn)
        legal_moves = deepcopy(self.board.legalmoves)
        bestmove = None
        for move in legal_moves:
            alpha = max(alpha, best_value)
            self.board.move(self.player_at_turn, *move)
            self.player_at_turn = 3 - self.player_at_turn
            value = -self.negamax(depth - 1, -beta, -alpha)
            self.player_at_turn = 3 - self.player_at_turn
            self.board.undo(self.player_at_turn)
            if value > best_value:
                best_value = value
                bestmove = move
                if best_value >= beta:
                    break
        return best_value

    def retrieve_tt(self, zobrist):
        zobrist_index = zobrist & 0x7FFFFF
        zobrist_msb = zobrist >> 23
        entry = self.tt[zobrist_index]
        if entry[0] == zobrist_msb:
            pass
            x= 0
            return entry
        else:
            return None

    # def negamax(self, board, depth, alpha, beta):
        
    #     old_a = alpha
        
        

    #     ttvalue = self.ttretrieve(depth, alpha, beta)
    #     if ttvalue is not None:
    #         return ttvalue
    #     else:
    #         ttdepth = -1
    #         ttmove = (-1, 0, 0, 0)

    #     if depth == 0:
    #         return self.evaluation_function(board)

    #     if ttdepth >= 0:
    #         packed_move = np.uint16(self.tt[tt_index][2])
    #         y0, x0, y1, x1 = np.uint8(packed_move >> 12), np.uint8((packed_move >> 8) & 0b1111), np.uint8((packed_move >> 4) & 0b1111), np.uint8(packed_move & 0b1111)
    #         board.move(y0, x0, y1, x1)
    #         board.switch_player()
    #         value = -self.negamax(board, depth - 1, -beta, -alpha)
    #         board.undo()
    #         bestmove = (y0, x0, y1, x1)
    #         if value >= beta:
    #             if value <= old_a:
    #                 flag = 2
    #             elif value >= beta:
    #                 flag = 1
    #             else:
    #                 flag = 0
    #             ttflag, ttdepth, ttvalue = np.uint8(flag), np.uint8(depth), np.int16(value)
    #             packed_value = np.uint16(ttflag | (ttdepth << 2) | (ttvalue << 7))
    #             packed_move = np.uint16(y0 << 12 | x0 << 8 | y1 << 4 | x1)
    #             self.tt[tt_index][1] = packed_value
    #             self.tt[tt_index][2] = packed_move
    #             return value

    #     best_value = -sys.maxsize
    #     board.legal_moves()
    #     moves = deepcopy(board.legalmoves)
    #     for move in moves:
    #         y0, x0, y1, x1 = move
    #         if move != ttmove:
    #             board.move(y0, x0, y1, x1)
    #             board.switch_player()
    #             value = self.negamax(board, depth - 1, -beta, -alpha)
    #             if value is None:
    #                 print("None", move)
    #             else:
    #                 print(-value)
    #                 value = -value
    #             board.undo()
    #             if value > best_value:
    #                 best_value = value
    #                 if best_value >= beta:
    #                     zobrist = board.zobrist_hash()
    #                     if best_value <= old_a:
    #                         flag = 2
    #                     elif best_value >= beta:
    #                         flag = 1
    #                     else:
    #                         flag = 0
    #                     print("Flag:", flag, "Depth:", depth, "Value:", best_value, "Move:", move)
    #                     flag, depth, value = np.uint8(flag), np.uint8(depth), np.int16(best_value)
    #                     packed_value = np.uint16(flag | (depth << 2) | (value << 7))
    #                     packed_move = np.uint16(y0 << 12 | x0 << 8 | y1 << 4 | x1)
    #                     packed_index = np.uint16(zobrist >> 23)
    #                     zobrist_index = zobrist & 0x7FFFFF
    #                     self.tt[zobrist_index][0] = packed_index
    #                     self.tt[zobrist_index][1] = packed_value
    #                     self.tt[zobrist_index][2] = packed_move
    #                     return best_value
                        
        

if __name__ == "__main__":
    engine = Engine(Board(),1)
    engine.negamax_root(engine.board, 5, -sys.maxsize, sys.maxsize)

