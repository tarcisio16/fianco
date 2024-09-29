from enginewithtt import TTengine as Engine
import logging
from parameters import *
from board import Board
import logging

logging.basicConfig(filename='engine.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ImprovedEngine(Engine):
    def __init__(self, board, player) -> None:
        super().__init__(board, player)

    def negamax(self, depth, alpha, beta, zobrist):
        self.nodes += 1
        ttmove, olda, ttvalue_packed = None, alpha, self.retrieve_tt(zobrist)
        
        if ttvalue_packed is not None:
            self.hits += 1
            tt_depth = (ttvalue_packed >> 60) & 0xF
            if tt_depth >= depth: 
                tt_value = -(ttvalue_packed >> 16) & 0xFFFFFFFFFF if (ttvalue_packed >> 56) & 0x1 else (ttvalue_packed >> 16) & 0xFFFFFFFFFF
                tt_flag = (ttvalue_packed >> 57) & 0b111
                if tt_flag == EXACT: return tt_value
                alpha, beta = (max(alpha, tt_value), beta) if tt_flag == LOWERBOUND else (alpha, min(beta, tt_value))
                if alpha >= beta: return tt_value

        if depth == 0:
            self.evaluation += 1
            return self.board.evaluation_function(self.player_at_turn)        

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
        

        for move in self.board.generate_moves(self.player_at_turn, sorted_moves=True):
            
            if ttmove is not None and move == ttmove:
                continue
            self.board.move(self.player_at_turn, *move)
            self.player_at_turn ^= 3
            zobrist_move = self.board.zobrist_move(zobrist, self.player_at_turn  , move)
            value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
            self.player_at_turn ^= 3
            self.board.undomove(self.player_at_turn, *move)

            if value > best_value:
                best_value = value
                bestmove = move
                if best_value >= beta:
                    self.store_tt(zobrist, depth, best_value, bestmove, olda, beta)

        logging.debug(f"Depth: {depth}, Value: {best_value}, Alpha: {alpha}, Beta: {beta}")
        return best_value
    
    def negamax_iterative_deepening_root(self, board, max_depth, alpha, beta):
        self.next_turn()
        best_move = None
        zobrist = board.zobrist_hash(self.player)
        for depth in range(2, max_depth + 1):
            best_value, current_best_move = -1000000, None
            for move in board.generate_moves(self.player):
                logging.debug(f"Move: {move}, Player: {self.player}, Depth: {depth}")
                board.move(self.player, *move)
                self.player_at_turn ^= 3    
                zobrist_move = board.zobrist_move(zobrist, self.player_at_turn, move)
                value = -self.negamax(depth - 1, -beta, -alpha, zobrist_move)
                self.player_at_turn ^= 3
                board.undomove(self.player, *move)

                if value > best_value:
                    best_value, current_best_move = value, move
                alpha = max(alpha, value)
                if alpha >= beta: break
                logging.debug(f"Depth: {depth} Move: {move} Value: {value}, Alpha: {alpha}, Beta: {beta}")
            best_move = current_best_move

        return best_move

    
if __name__ == "__main__":
    # Create a new board object
    board = Board()

    # Create a new TTengine object
    engine = ImprovedEngine(board, player=WHITE)

    # Set the maximum depth for iterative deepening
    max_depth = 5

    # Perform iterative deepening search
    best_move = engine.negamax_iterative_deepening_root(board, max_depth, alpha=-1000000, beta=1000000)

    # Print the best move
    print("Best Move:", best_move)
