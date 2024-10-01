from collections import deque
import logging
from parameters import *
from board import Board
from enginewithtt import TTengine as Engine
from copy import deepcopy
import time 

R = 2


class QuiescentEngine(Engine):

    def __init__(self,board,player) -> None:
        super().__init__(board,player)
        self.bestmoves = []
        self.null = True
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

        winner = self.board.checkwin()
        if winner == self.player_at_turn:
            return 1000000
        elif winner == 3 - self.player_at_turn:
            return -1000000
        
        if depth == 0:
            return self.board.evaluation_function(self.player_at_turn)
            #return self.quiescent_search(1, alpha, beta, zobrist)        

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
            alpha = max(alpha, best_value)
            value = self.move_negamax(self.player_at_turn,move, alpha, beta, depth, zobrist)

            if value > best_value:
                best_value = value
                bestmove = move
                if best_value >= beta:
                    self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                    break

        return best_value
    
    def negamax_iterative_deepening_root(self, board, max_depth, alpha, beta,max_time = 12):

        # next turn
        self.next_turn()
        #variables
        initial_a, initial_b, bestmoves = alpha, beta, deque()
        zobrist = board.zobrist_hash(self.player) 
        moves = list(board.generate_moves(self.player, sorted_moves=True))
        best_move = None
        best_value_all = -1000000
        start = time.time()
        #iterative deepening
        for depth in range(1, max_depth):
        
            current_best_move, best_value, alpha, beta, new_best_moves = best_move, -1000000, initial_a, initial_b, deque()
            if time.time() - start > max_time:
                self.depth = depth
                break
            print("Searching at depth", depth)
            for move in bestmoves: #best move from previous iteration

                value = self.move_negamax(self.player,move, alpha, beta, depth, zobrist)

                # update best value 
                if value > best_value:
                    best_value, current_best_move = value, move
                    new_best_moves.appendleft(move)
                    
                alpha = max(alpha, best_value)
                if best_value >= beta:  
                    logging.debug(f"TT cut-off at depth {depth}, value {best_value}, alpha {alpha}, beta {beta}")
                    best_move = current_best_move
                    break
                
            for move in moves:
                if move in bestmoves: continue
                value = self.move_negamax(self.player,move, alpha, beta, depth, zobrist)
                # update best value 
                if value > best_value:
                    best_value = value
                    current_best_move = move
                    new_best_moves.appendleft(move)
                alpha = max(alpha, best_value)
                if best_value >= beta:
                    best_move = current_best_move
                    logging.debug(f"TT cut-off at depth {depth}, value {best_value}, alpha {alpha}, beta {beta}")
                    break
            best_move = current_best_move
            bestmoves = new_best_moves
            print("Best move at depth", depth, best_move)
            self.depth = max_depth

        if best_move is None:
            best_move = moves[0]
        
        return best_move

    def move_negamax(self,player,move, alpha, beta, depth, zobrist):
        self.board.move(player,*move)
        self.player_at_turn = 3 - player
        value = -self.negamax(depth - 1, -beta, -alpha, self.board.zobrist_move(zobrist, self.player_at_turn, move))
        self.player_at_turn = player
        self.board.undomove(player,*move)
        return value
        

    def quiescent_search(self, depth, alpha, beta, zobrist):
        best_value = self.board.evaluation_function(self.player_at_turn)
        if best_value >= beta: return beta
        alpha = max(alpha, best_value)

        for move in self.board.generate_moves(self.board.player, capture=True):
            self.board.move(self.board.player, *move)
            self.board.player = 3 - self.board.player
            value = -self.negamax(depth - 1, -beta, -alpha, self.board.zobrist_move(zobrist, self.board.player, move))
            self.board.player = 3 - self.board.player
            self.board.undomove(self.board.player, *move)

            best_value = max(best_value, value)
            if best_value >= beta:
                break
            alpha = max(alpha, best_value)
        return best_value