import numpy as np
from board import Board
from parameters import *
import time

feature_set = {"FIANCO_BONUS": 10,
                "POSITIONAL_BONUS": 2,
                "SECONDLASTBONUS": 10,
                "THIRDANDCAPTURE_BONUS": 10,
                 "PIECE_BONUS": 5}
class TTengine():
    
    def __init__(self, board, player,feature_set, transposition_table_size = 26) -> None:
        self.board = board
        self.player = player
        self.turn = 0
        self.player_at_turn = player
        self.tt = np.zeros((2 ** transposition_table_size, 2), dtype=np.uint64)  # 64-bit entry: |depth (4)|flag (3)|sign (1)|value (40)|move (16)|
        self.hits = self.turn = self.nodes = 0
        self.evaluation = 0
        self.collisions = 0
        self.mask = (1 << transposition_table_size) - 1 
        self.depth = 0
        self.fiancobonus = feature_set["FIANCO_BONUS"]
        self.positionalbonus = feature_set["POSITIONAL_BONUS"]
        self.secondlastbonus = feature_set["SECONDLASTBONUS"]
        self.thirdandcapturebonus = feature_set["THIRDANDCAPTURE_BONUS"]
        self.piecebonus = feature_set["PIECE_BONUS"]
        self.feature_set = feature_set
        

    def retrieve_tt(self, zobrist):
        entry = self.tt[int(zobrist) & self.mask]
        hash = entry[0]
        if hash == zobrist:
            return int(entry[1]) 

        return None

    def store_tt(self, zobrist, depth, value, move, alpha, beta):
        flag = LOWERBOUND if value >= beta else UPPERBOUND if value <= alpha else EXACT
        sign = 1 if value < 0 else 0
        value = abs(value)
        packed = (depth << 60) | (flag << 57) | (sign << 56) | (value << 16) | (move[0] << 12) | (move[1] << 8) | (move[2] << 4) | move[3]
        index = int(zobrist) & self.mask
        self.tt[index] = [np.uint64(zobrist), np.uint64(packed)]

    def next_turn(self):
        self.turn += 1
        self.hits = self.nodes = 0


    def move_negamax(self,player,move, alpha, beta, depth, zobrist):
        self.board.move(player,*move)
        self.player_at_turn = 3 - player
        value = -self.negamax(depth - 1, -beta, -alpha, self.board.zobrist_move(zobrist, self.player_at_turn, move))
        self.player_at_turn = player
        self.board.undomove(player,*move)
        return value

    def timeup(self, start, max_time):
        return time.time() - start > max_time
    
    def evaluation_function(self, player):
        def calculate_score(pieces, is_white):
            score = 0
            for y, x in pieces:
                # Calculate base positional score
                positional_score = (y * self.positionalbonus) if is_white else ((BOARD_SIZE - y - 1) * self.positionalbonus)

                # Add specific bonuses
                if x in (0, 8):
                    positional_score += self.fiancobonus
                if y == (7 if is_white else 1):
                    positional_score += self.secondlastbonus    
                score += positional_score 
            return score

        
        white_score = calculate_score(self.board.white_pieces, True)
        white_score += self.piecebonus * len(self.board.white_pieces)
        black_score = calculate_score(self.board.black_pieces, False)
        black_score += self.piecebonus * len(self.board.black_pieces) 
        
        return white_score - black_score if player == WHITE else black_score - white_score

def getvalue(ttvalue_packed):
    return -((ttvalue_packed >> 16) & 0xFFFFFFFFFF) if (ttvalue_packed >> 56) & 0x1 else (ttvalue_packed >> 16) & 0xFFFFFFFFFF

def main():
    # Initialize the board
    board = Board()  # Assuming Board class is implemented correctly
    feature_set = {
        "FIANCO_BONUS": 5,
        "POSITIONAL_BONUS": 10,
        "SECONDLASTBONUS": 3,
        "THIRDANDCAPTURE_BONUS": 10,
        "PIECE_BONUS": 5
    }
    
    # Initialize the TT engine
    tt_engine = TTengine(board, WHITE, feature_set)

    # Example zobrist hash and move
    zobrist_hash = 0x123456789ABCDEF  # Example Zobrist hash
    depth = 15
    move = [4, 2, 5, 3]  # Example move (start_row, start_col, end_row, end_col)
    value = -500
    alpha = -100
    beta = 100
    
    # Test storing in the transposition table
    print(f"Inserting into TT: zobrist_hash={zobrist_hash}, depth={depth}, value={value}, move={move}")
    tt_engine.store_tt(zobrist_hash, depth, value, move, alpha, beta)

    # Test retrieving from the transposition table
    retrieved_entry = tt_engine.retrieve_tt(zobrist_hash)
    if retrieved_entry is not None:
        # Unpack the retrieved entry
        depth_stored = (retrieved_entry >> 60) & 0xF
        flag_stored = (retrieved_entry >> 57) & 0x7
        sign_stored = (retrieved_entry >> 56) & 0x1
        value_stored = (retrieved_entry >> 16) & 0xFFFFFFFFFF
        move_stored = [
            (retrieved_entry >> 12) & 0xF,
            (retrieved_entry >> 8) & 0xF,
            (retrieved_entry >> 4) & 0xF,
            retrieved_entry & 0xF
        ]
        value_stored = -(retrieved_entry >> 16) & 0xFFFFFFFFFF if (retrieved_entry >> 56) & 0x1 else (retrieved_entry >> 16) & 0xFFFFFFFFFF
        
        print(f"Retrieved from TT: zobrist_hash={zobrist_hash}, depth={depth_stored}, value={value_stored}, move={move_stored}")
    else:
        print("No entry found in TT.")

    # Check for TT hits and collisions
    print(f"TT Hits: {tt_engine.hits}, TT Collisions: {tt_engine.collisions}")

if __name__ == "__main__":
    main()