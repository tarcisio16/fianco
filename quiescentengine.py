from collections import deque
import logging
from parameters import *
from board import Board
from enginewithtt import TTengine as Engine
from enginewithtt import getvalue
import sys
import time 
import pprint

feature_set1 = {"FIANCO_BONUS": 5,
                "POSITIONAL_BONUS": 5,
                "SECONDLASTBONUS": 3,
                "THIRDANDCAPTURE_BONUS": 10,
                 "PIECE_BONUS": 20}

class QuiescentEngine(Engine):

    def __init__(self,board,player,feature_set = feature_set1,  transposition_table_size = 26) -> None:
        super().__init__(board,player,feature_set, transposition_table_size)
        self.bestmoves = []
        self.null = False


    def negamax(self, depth, alpha, beta, zobrist):
        ttmove, olda, ttvalue_packed, self.nodes = None, alpha, self.retrieve_tt(zobrist), self.nodes + 1
            
        if ttvalue_packed is not None:
            tt_depth = (ttvalue_packed >> 60) & 0xF
            if tt_depth >= depth: 
                tt_value = getvalue(ttvalue_packed)
                tt_flag = (ttvalue_packed >> 57) & 0b111
                if tt_flag == EXACT: return tt_value
                alpha, beta = (max(alpha, tt_value), beta) if tt_flag == LOWERBOUND else (alpha, min(beta, tt_value))
                if alpha >= beta: return tt_value

        winner = self.board.checkwin()
        if winner == 1 and self.player_at_turn == WHITE: return 1000 + depth
        elif winner == 2 and self.player_at_turn == BLACK: return 1000 + depth


        if depth == 0:
            return self.quiescent_search(alpha, beta,zobrist = zobrist) 

        if ttvalue_packed is not None and tt_depth >= 0:
            
            ttmove = (ttvalue_packed >> 12) & 0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0XF, ttvalue_packed & 0xF
            if tt_depth > 0:
                best_value, bestmove = self.move_negamax(self.player_at_turn,ttmove, alpha, beta, depth, zobrist), ttmove
                alpha = max(alpha, best_value)
                if best_value >= beta:
                    self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                    return best_value
            else:
                best_value = getvalue(ttvalue_packed)
            

        best_value = -1000000
        
        for move in self.board.generate_moves(self.player_at_turn, sorted_moves=True):
            value = self.move_negamax(self.player_at_turn,move, alpha, beta, depth, zobrist)
            if value > best_value:
                best_value, bestmove = value, move
            alpha = max(alpha, best_value)
            if best_value >= beta:
                self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                break

        print(best_value)
        return best_value
    
    def negamax_iterative_deepening_root(self, board, max_depth, alpha = -1000000, beta= 1000000,max_time = 8):

        self.next_turn()
        initial_a, initial_b, best_move, zobrist, start = alpha, beta, None, board.zobrist_hash(self.player), time.time()
        if self.board.menace(self.player):
            moves = {value: alpha  for value in board.generate_moves(self.player, sorted_moves=True, reverse = False)}
        else : moves = {value: alpha  for value in board.generate_moves(self.player, sorted_moves=True)}  
        if len(moves) == 1: return list(moves.keys())[0]

        for depth in range(1, max_depth):
            if self.timeup(start, max_time): break
            
            current_best_move, best_value, alpha, beta, beta_cutoff = None, initial_a, initial_a, initial_b, False
            current_moves = [move for move, _ in moves.items()] if depth == 1 else [move for move, _ in sorted(moves.items(), key=lambda item:item[1], reverse=True)]
 
            for move in current_moves:
                value = self.move_negamax(self.player,move, alpha, beta, depth, zobrist)
                moves[move] = value
                if value > best_value:
                    best_value, current_best_move = value, move
                alpha = max(alpha, best_value)
                if best_value >= beta:  
                    best_move = current_best_move
                    continue
                if self.timeup(start, max_time):
                    break
            best_move, self.depth = current_best_move, depth

        best_move = current_moves[0] if best_move is None and len(current_moves)>0 else best_move
        return best_move

        
    def quiescent_search(self, alpha, beta, zobrist):
        score = self.evaluation_function(self.player_at_turn)
        if score >= beta: 
            self.store_tt(zobrist, 0, score, (0,0,0,0), alpha, beta)
            return score
        alpha = max(alpha, score)
        
        for move in self.board.generate_moves(self.player_at_turn,capture = True):
            self.board.move(self.player_at_turn,*move)
            self.player_at_turn ^= 3
            value = -self.quiescent_search(-beta, -alpha, self.board.zobrist_move(zobrist, self.player_at_turn, move))
            self.player_at_turn ^= 3
            self.board.undomove(self.player_at_turn,*move)
            score = max(score, value)
            if value >= beta:
                return beta
            alpha = max(alpha, value)
        return score


