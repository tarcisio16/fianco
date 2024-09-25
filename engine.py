from board import Board
from parameters import *
import numpy as np
from collections import deque
import sys
from copy import deepcopy
import logging

logging.basicConfig(filename='engine.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Engine:

    def __init__(self, board, player) -> None:
        self.board = board
        self.player = player
        self.principal_variation = deque(maxlen=MAX_QUEUE_SIZE)
        self.player_at_turn = player
        self.bestmove = None


    def evaluation_function(self,board, player):
        score = 0
        
        winner = board.checkwin()
        if winner == player: return 100000
        elif winner == 3 - player: return -100000

        def positional_score(pieces, opponent_pieces, is_white):
            
            positional_value = 0
            central_bonus, advancement_bonus = 2, 4
            for piece in pieces:
                row, col = piece
                if 3 <= row <= 5: positional_value += central_bonus
                if is_white: 
                    positional_value += (row) * advancement_bonus  # reward advancing towards row 8
                else: 
                    positional_value += (8 - row) * advancement_bonus
            
            # Penalize the opponent's advancement
            for piece in opponent_pieces:
                row, col = piece
                if is_white:
                    positional_value -= (8 - row)  # penalize opponent's advancement
                else:
                    positional_value -= row  # penalize opponent's advancement

            return positional_value

        # Adjust score for white
        if player == WHITE:
            score += (len(board.white_pieces) - len(board.black_pieces)) * 10  
            score += positional_score(board.white_pieces, board.black_pieces, is_white=True)

        # Adjust score for black
        else:
            score += (len(board.black_pieces) - len(board.white_pieces)) * 10  
            score += positional_score(board.black_pieces, board.white_pieces, is_white=False)

        return score

    def negamax_root(self, board, depth, alpha, beta):
        """Negamax root function to be called for the top-level search."""
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
            if value > best_value:
                best_value = value
            
                best_move = move
            alpha = max(alpha, value)  # Update alpha

            if alpha >= beta:
                break  # Beta cutoff, stop search

        return best_move  # Return the best move and its value


                        
        

