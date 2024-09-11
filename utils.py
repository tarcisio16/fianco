import random

MIN = 0
MAX = 2**64 - 1  # Slightly optimized to avoid calling pow() every time
NUMBER_OF_PLAYERS = 2
BOARD_SIZE = 9
SEED = 420

# Use more Pythonic naming conventions
def random_int():
    random.seed(SEED)
    return random.randint(MIN, MAX)

# Initialize Zobrist Table
def init_table():
    return [[[random_int() for _ in range(BOARD_SIZE)] 
             for _ in range(BOARD_SIZE)] 
             for _ in range(NUMBER_OF_PLAYERS)]

# Optimized hash function
def compute_hash(board, zobrist_table, player):
    hash_value = 0
    
    # Combine the hash computation and lookup into one step
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece != 0:
                # Adjusted indexing for the player pieces
                hash_value ^= zobrist_table[piece - 1][i][j]
    
    # XOR player into the hash (XOR is fast and order-independent)
    hash_value ^= player
    
    return hash_value