from collections import deque
import logging
from parameters import *
from board import Board
from enginewithtt import TTengine as Engine
from copy import deepcopy
import time 
from pprint import pprint
from collections import OrderedDict

R = 2


class QuiescentEngine(Engine):

    def __init__(self,board,player) -> None:
        super().__init__(board,player)
        self.bestmoves = []
        self.null = False
        self.evaluations = 0
        self.depth = 0


    def negamax(self, depth, alpha, beta, zobrist):
        self.nodes += 1
        ttmove, olda, ttvalue_packed = None, alpha, self.retrieve_tt(zobrist)
            
        if ttvalue_packed is not None:
            tt_depth = (ttvalue_packed >> 60) & 0xF
            if tt_depth >= depth: 
                tt_value = -(ttvalue_packed >> 16) & 0xFFFFFFFFFF if (ttvalue_packed >> 56) & 0x1 else (ttvalue_packed >> 16) & 0xFFFFFFFFFF
                tt_flag = (ttvalue_packed >> 57) & 0b111
                if tt_flag == EXACT: return tt_value
                alpha, beta = (max(alpha, tt_value), beta) if tt_flag == LOWERBOUND else (alpha, min(beta, tt_value))
                if alpha >= beta: return tt_value

        # forward pruning in victory case
        winner = self.board.checkwin()
        if winner == self.player_at_turn:   return 1000000
        elif winner == 3 - self.player_at_turn: return -1000000
        if depth == 0:
            #return self.quiescent_search(depth, alpha, beta, zobrist)
            return self.board.evaluation_function(self.player_at_turn)      

        if ttvalue_packed is not None and tt_depth >= 0:
            ttmove = (ttvalue_packed >> 12) & 0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0XF, ttvalue_packed & 0xF

            best_value = self.move_negamax(self.player_at_turn,ttmove, alpha, beta, depth, zobrist)     
            bestmove = ttmove
            if best_value >= beta:
                self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                return best_value

        best_value = -1000000

        move_number = 0
        
        # Search null move
        if self.null and depth > R:
            self.null = False
            self.player_at_turn ^= 3  
            value = -self.negamax(depth - 1 - R , -beta, -alpha, zobrist ^ self.board.zobrist_player[0] ^ self.board.zobrist_player[1])
            self.player_at_turn ^= 3
            self.null = True
            if value >= beta:
                return beta
        

        for move in self.board.generate_moves(self.player_at_turn, sorted_moves=True):
            
            if ttmove is not None and move == ttmove:
                continue  
            value = self.move_negamax(self.player_at_turn,move, alpha, beta, depth, zobrist)
            if value > best_value:
                best_value, bestmove = value, move
            alpha = max(alpha, best_value)
            if best_value >= beta:
                self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                break

        return best_value
    
    def negamax_iterative_deepening_root(self, board, max_depth, alpha = -1000000, beta= 1000000,max_time = 8):

        self.next_turn()
        
        initial_a, initial_b, best_move, zobrist = alpha, beta, None, board.zobrist_hash(self.player)
        moves = {value: -1000000 for value in board.generate_moves(self.player, sorted_moves=True)}
        start = time.time()
        if len(moves) == 1: 
            return list(moves.keys())[0]

        # Iterative deepening
        for depth in range(1, max_depth):

            # check if time is up
            if self.timeup(start, max_time): break
            
            current_best_move, best_value, alpha, beta, beta_cutoff = None, -1000000, initial_a, initial_b, False

            current_moves = moves 
            current_moves = [move for move, _ in moves.items()] if depth == 1 else [move for move, _ in sorted(moves.items(), key=lambda item:item[1], reverse=True)]

            print("moves:")
            pprint(moves)
            print("\ncurrent_moves:")
            pprint(current_moves)
            print("\nsorted_values:", sorted(moves.values(), reverse=True))
            pprint("beta: " + str(beta))    
                
            
            for move in current_moves:
                if beta_cutoff:     
                    moves[move] = -1000000
                    continue
                if time.time() - start > max_time: break
                value = self.move_negamax(self.player,move, alpha, beta, depth, zobrist)
                moves[move] = value
                if value > best_value:
                    best_value, current_best_move = value, move
                alpha = max(alpha, best_value)
                if best_value >= beta:  
                    best_move, beta_cutoff = current_best_move, True
                    continue
  

            best_move, self.depth = current_best_move, depth

        if best_move is None: best_move = current_moves[0]
        
        return best_move

    def move_negamax(self,player,move, alpha, beta, depth, zobrist):
        self.board.move(player,*move)
        self.player_at_turn = 3 - player
        value = -self.negamax(depth - 1, -beta, -alpha, self.board.zobrist_move(zobrist, self.player_at_turn, move))
        self.player_at_turn = player
        self.board.undomove(player,*move)
        return value
        
    def quiescent_search(self, depth, alpha, beta, zobrist, max_depth = 2):
        best_value = self.board.evaluation_function(self.player_at_turn)
        if max_depth == 0: return best_value
        if best_value >= beta: return beta
        alpha = max(alpha, best_value)

        pieces = self.board.white_pieces if self.player_at_turn == WHITE else self.board.black_pieces
        opponent_pieces = self.board.black_pieces if self.player_at_turn == WHITE else self.board.white_pieces
        
        pieces_row1, pieces_row2 = len(pieces.intersection(ROW1 if self.player_at_turn == WHITE else ROW7)), len(pieces.intersection(ROW2 if self.player_at_turn == WHITE else ROW6))
        opponent_pieces_row1, opponent_pieces_row2 = len(opponent_pieces.intersection(ROW1 if self.player_at_turn == WHITE else ROW7)), len(opponent_pieces.intersection(ROW2 if self.player_at_turn == WHITE else ROW6))
        bestmove = None
        
        if opponent_pieces_row1 != 0 or opponent_pieces_row2 != 0:
            for move in self.board.generate_moves(self.player_at_turn):
                zobrist_move = self.board.zobrist_move(zobrist, self.player_at_turn, move)
                value = - self.quiescent_search(depth - 1, alpha, beta, zobrist_move, max_depth -1)
                if best_value > value:
                    best_value, best_move = value, move
                alpha = max(alpha, value)
                if best_value >= beta:
                    self.store_tt(zobrist_move, depth, best_value, best_move, alpha, beta)
                    return beta
        return best_value

    def timeup(self, start, max_time):
        return time.time() - start > max_time
