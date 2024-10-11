from board import Board
from quiescentengine import QuiescentEngine as Engine
import logging
from parameters import *
from enginewithtt import getvalue


class SmartEngine(Engine):
    def __init__(self, board, player, feature_set = feature_set1, transposition_table_size=26):
        super().__init__(board, player, feature_set, transposition_table_size)
        self.threadkill = False
        self.backboard = None 
        

    def negamax_background_id(self, board, max_depth,player, alpha = -1000000, beta= 1000000, window = 1):

        self.player_at_turn = player
        initial_a, initial_b, zobrist = alpha, beta, self.board.zobrist_hash(player)

        generated_moves = self.order_moves(list(self.board.generate_moves(player)))
        moves = {value: alpha  for value in generated_moves}
        for depth in range(1, max_depth):

            best_value, alpha, beta = initial_a, initial_a, initial_b
            current_moves = [move for move, _ in moves.items()] if depth == 1 else [move for move, _ in sorted(moves.items(), key=lambda item:item[1], reverse=True)]

            
            for move, i in zip(current_moves, range(len(current_moves))):
                if self.threadkill: 
                    self.threadkill = False
                    self.player_at_turn = 3 - player
                    return
                value = self.move_negamax(player,move, alpha, beta, depth, zobrist)
                moves[move] = value
                if value > best_value:
                    best_value = value
                alpha = max(alpha, best_value)
                if best_value >= beta:  
                    break
        self.player_at_turn = 3 - player

 