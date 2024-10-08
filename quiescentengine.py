from collections import deque
import logging
from parameters import *
from board import Board
from enginewithtt import TTengine as Engine
from copy import deepcopy
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

        winner = self.board.checkwin()
        if winner == 1 and self.player_at_turn == WHITE: return 1000
        if winner == 2 and self.player_at_turn == BLACK: return 1000


        if depth == 0:
            return self.quiescent_search(alpha, beta, max_depth = 2, zobrist = zobrist) 

        if ttvalue_packed is not None and tt_depth > 0:
            ttmove = (ttvalue_packed >> 12) & 0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0XF, ttvalue_packed & 0xF

            best_value, bestmove = self.move_negamax(self.player_at_turn,ttmove, alpha, beta, depth, zobrist), ttmove
            if best_value >= beta:
                self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                return best_value

        best_value = -1000000
                
        nullvalue = self.nullsearch(depth,alpha,beta,zobrist)
        if nullvalue is not None:
            return nullvalue
        
        for move in self.board.generate_moves(self.player_at_turn, sorted_moves=True):
            
            if ttmove is not None and move == ttmove: continue  
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
        initial_a, initial_b, best_move, zobrist, start = alpha, beta, None, board.zobrist_hash(self.player), time.time()
        if self.board.menace(self.player):
            print("MENACE")
            moves = {value: alpha  for value in board.generate_moves(self.player, sorted_moves=True, reverse = False)}
        else : moves = {value: alpha  for value in board.generate_moves(self.player, sorted_moves=True)}
        print(moves)
        # if only one move, return it
        if len(moves) == 1: return list(moves.keys())[0]

        for depth in range(1, max_depth):
            if self.timeup(start, max_time): break
            
            current_best_move, best_value, alpha, beta, beta_cutoff = None, initial_a, initial_a, initial_b, False
            print("DEPTH: ", depth)
            pprint.pprint(moves)
            current_moves = [move for move, _ in moves.items()] if depth == 1 else [move for move, _ in sorted(moves.items(), key=lambda item:item[1], reverse=True)]
            for move in current_moves:
                if beta_cutoff:     
                    moves[move] = initial_a
                    continue
                value = self.move_negamax(self.player,move, alpha, beta, depth, zobrist)
                moves[move] = value
                if value > best_value:
                    best_value, current_best_move = value, move
                alpha = max(alpha, best_value)
                if best_value >= beta:  
                    best_move, beta_cutoff = current_best_move, True
                    continue
                if self.timeup(start, max_time):
                    moves[move] = initial_a
                    continue
            best_move, self.depth = current_best_move, depth

        best_move = current_moves[0] if best_move is None and len(current_moves)>0 else best_move
        return best_move

        
    def quiescent_search(self, alpha, beta, max_depth = 2,zobrist = None):
        stand_pat = self.evaluation_function(self.player_at_turn)
        if max_depth == 0: 
            self.store_tt(zobrist, 0, stand_pat, (0,0,0,0), alpha, beta)
            return stand_pat
        if stand_pat >= beta: 
            self.store_tt(zobrist, 0, beta, (0,0,0,0), alpha, beta)
            return beta
        alpha = max(alpha, stand_pat)

        for move in self.board.generate_moves(self.player_at_turn,capture = True):
            self.board.move(self.player_at_turn,*move)
            self.player_at_turn ^= 3
            value = -self.quiescent_search(-beta, -alpha, max_depth - 1, self.board.zobrist_move(zobrist, self.player_at_turn, move))
            self.player_at_turn ^= 3
            self.board.undomove(self.player_at_turn,*move)
            alpha = max(alpha, value)
            if value >= beta:
                #self.store_tt(zobrist, 0, value, move, alpha, beta)
                return beta

        # opponent_pieces = self.board.black_pieces if self.player_at_turn == WHITE else self.board.white_pieces
        # opponent_pieces_row1 = len(opponent_pieces.intersection(ROW1 if self.player_at_turn == WHITE else ROW7))
        # opponent_pieces_row2 = len(opponent_pieces.intersection(ROW2 if self.player_at_turn == WHITE else ROW6))
        # if opponent_pieces_row1 != 0: # or opponent_pieces_row2 != 0:
        #     for move in self.board.generate_moves(self.player_at_turn):
        #         self.board.move(self.player_at_turn,*move)
        #         self.player_at_turn ^= 3
        #         value = -self.quiescent_search(-beta, -alpha, max_depth - 1, self.board.zobrist_move(zobrist, self.player_at_turn, move))
        #         self.player_at_turn ^= 3
        #         self.board.undomove(self.player_at_turn,*move)
        #         alpha = max(alpha, value)
        #         if value >= beta:
        #             self.store_tt(zobrist, 0, value, move, alpha, beta)
        #             return beta
        return alpha


    def nullsearch(self,depth,alpha,beta,zobrist):
        if self.null and depth > R:
            endgame_situation = len(self.board.white_pieces) < 5 or len(self.board.black_pieces) < 5
            critical_situation = len(self.board.white_pieces.intersection(ROW7)) > 0 or len(self.board.black_pieces.intersection(ROW1)) > 0
            if not endgame_situation and not critical_situation:
                self.null = False
                self.player_at_turn ^= 3  
                value = -self.negamax(depth - 1 - R , -beta, -beta +1, zobrist ^ self.board.zobrist_player[0] ^ self.board.zobrist_player[1])
                self.player_at_turn ^= 3
                self.null = True
                if value >= beta:
                    
                    return beta
                return None
                
