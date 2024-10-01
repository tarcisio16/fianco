import logging
import numpy as np
from board import Board
import sys
from parameters import *
import time

logging.basicConfig(filename='engine.log', filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


TTSIZE = 2**27
TTMASK = 0x7FFFFFF
class TTengine():
    
    def __init__(self, board, player) -> None:
        self.board = board
        self.player = player
        self.turn = 0
        self.player_at_turn = player
        self.tt = np.zeros((TTSIZE, 2), dtype=np.uint64)  # 64-bit entry: |depth (4)|flag (3)|sign (1)|value (40)|move (16)|
        self.hits = self.turn = self.nodes = 0
        self.evaluation = 0
        self.collisions = 0

    def retrieve_tt(self, zobrist):
        entry = self.tt[int(zobrist) & TTMASK]
        hash = entry[0]
        if hash != 0:
            if hash == zobrist:
                self.hits += 1
                return int(entry[1]) 
            self.collisions += 1
        return None

    def store_tt(self, zobrist, depth, value, move, alpha, beta):
        flag = LOWERBOUND if value >= beta else UPPERBOUND if value <= alpha else EXACT
        sign = 1 if value < 0 else 0
        value = abs(value)
        packed = (depth << 60) | (flag << 57) | (sign << 56) | (value << 16) | (move[0] << 12) | (move[1] << 8) | (move[2] << 4) | move[3]
        index = int(zobrist) & TTMASK
        self.tt[index] = [np.uint64(zobrist), np.uint64(packed)]

    def next_turn(self):
        self.turn += 1
        self.hits = self.nodes = 0



