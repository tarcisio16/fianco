from parameters import *
from board import Board
from improvedengine import ImprovedEngine as Engine

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

        if depth == 0:
            return self.quiescent_search(1, alpha, beta, zobrist)        

        if ttvalue_packed is not None and tt_depth >= 0:
            ttmove = (ttvalue_packed >> 12) & 0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0XF, ttvalue_packed & 0xF
            self.board.move(self.player_at_turn, *ttmove)
            self.player_at_turn ^= 3
            zobrist_move = self.board.zobrist_move(zobrist, self.player_at_turn  , ttmove)          
            best_value = -self.negamax(depth - 1, -beta, -alpha,zobrist_move)
            self.player_at_turn ^= 3
            self.board.undomove(self.player_at_turn, *ttmove)   
            bestmove = ttmove
            if best_value >= beta:
                self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)
                return best_value

        best_value = -1000000

        # Search null move
        if self.null and depth > R:
            self.null = False
            self.player_at_turn ^= 3
            player = 1 if self.player_at_turn == WHITE else 0
            opponent = 1 - player
            zobrist_move  = zobrist ^ self.board.zobrist_player[0] ^ self.board.zobrist_player[1]
            value = -self.negamax(depth - 1 - R , -beta, -alpha, zobrist_move)
            self.player_at_turn ^= 3
            self.null = True
            if value >= beta:
                return beta
        

        for move in self.board.generate_moves(self.player_at_turn, sorted_moves=True):
            if ttmove is not None and move == ttmove:
                continue
            alpha = max(alpha, best_value)
            self.board.move(self.player_at_turn, *move)
            self.player_at_turn ^= 3
            zobrist_move = self.board.zobrist_move(zobrist, self.player_at_turn , move)
            value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
            self.player_at_turn ^= 3
            self.board.undomove(self.player_at_turn, *move)

            if value > best_value:
                best_value = value
                bestmove = move
                if best_value >= beta:
                    self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)

        return best_value
    
    def negamax_iterative_deepening_root(self, board, max_depth, alpha, beta, opening_book = None):

        # next turn
        self.next_turn()
        
        # variable definition
        depth = self.assign_depth(max_depth)
        best_move = None
        zobrist = board.zobrist_hash(self.player) 
        for depth in range(2, max_depth + 1):
            current_best_move, best_value = None, -1000000

            # # try transposition table move
            ttmove, olda, ttvalue_packed, tt_depth = None, alpha, self.retrieve_tt(zobrist), -1
            if ttvalue_packed is not None:
                tt_depth = (ttvalue_packed >> 60) & 0xF
                ttmove = (ttvalue_packed >> 12) & 0xF, (ttvalue_packed >> 8) & 0xF, (ttvalue_packed >> 4) & 0XF, ttvalue_packed & 0xF
                
                board.move(self.player, *ttmove)
                zobrist_move = board.zobrist_move(zobrist, self.player, ttmove)
                self.player_at_turn = 3 - self.player_at_turn
                best_value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
                self.player_at_turn = 3 - self.player_at_turn
                board.undomove(self.player, *ttmove)
                
                current_best_move = ttmove
                if best_value >= beta:
                    self.store_tt(zobrist, depth, best_value, current_best_move, olda, beta)
                    break

            for move in board.generate_moves(self.player, sorted_moves=True):
                if move == ttmove:
                    continue
                
                board.move(self.player, *move)
                self.player_at_turn = 3 - self.player_at_turn
                zobrist_move = board.zobrist_move(zobrist, self.player_at_turn, move)
                value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
                self.player_at_turn = 3 - self.player_at_turn
                board.undomove(self.player, *move)
                alpha = max(alpha, best_value)
                if value > best_value:
                    best_value, current_best_move = value, move
                
                if best_value >= beta:
                    best_move = current_best_move
                    storett = self.store_tt(zobrist, depth, best_value, current_best_move, olda, beta)
                    break
            best_move = current_best_move

        if best_move is None:
            print("Error is here")
        return best_move

    def quiescent_search(self, depth, alpha, beta, zobrist):
        best_value = self.board.evaluation_function(self.player_at_turn)
        if best_value >= beta: return beta
        alpha = max(alpha, best_value)

        for move in self.board.generate_moves(self.board.player, capture=True):
            self.board.move(self.board.player, *move)
            self.board.player = 3 - self.board.player
            zobrist_move = self.board.zobrist_move(zobrist, self.board.player, move)
            value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
            self.board.player = 3 - self.board.player
            self.board.undomove(self.board.player, *move)

            best_value = max(best_value, value)
            if best_value >= beta:
                break
            alpha = max(alpha, best_value)
        return best_value