from board import Board
from improvedengine import ImprovedEngine as Engine
import pickle
from collections import defaultdict
from parameters import *
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

def save_opening_book(opening_book, filename):
    """Save the opening book to a file using pickle."""
    with open(filename, 'wb') as file:
        pickle.dump(opening_book, file) 

def print_move_statistics(opening_book):
    """Print out the statistics of moves in the opening book."""
    for color, moves in opening_book.items():
        print(f"\n{color} Moves Statistics:")
        
        if not moves:
            print("  No moves recorded.")
            continue

        for zobrist_hash, move_list in moves.items():
            print(f"  Zobrist Hash: {zobrist_hash}")
            
            move_count = defaultdict(int)
            for turn, move in move_list:
                move_count[tuple(move)] += 1 
        
            for move, count in move_count.items():
                turns = [turn for turn, m in move_list if m == move]
                move_notation = f"({move[0]}, {move[1]}, {move[2]}, {move[3]})"
                print(f"    Move {move_notation} appeared {count} times at turns: {', '.join(map(str, turns))}")

            print("")

def simulate_game(game_id):
    """Simulate a single game and return the moves made by both players."""
    opening_moves = {"WHITE": [], "BLACK": []}
    board = Board()
    
    for turn in range(10):
        engine = Engine(board, 1)
        move = engine.negamax_iterative_deepening_root(board, 5, -1000000, 1000000)
        board.movecheck(board.player, move[0], move[1], move[2], move[3])
        print(board, f"\nPlayer 1 moved {move[0], move[1], move[2], move[3]}")
        if board.player == BLACK:
            opening_moves["WHITE"].append((board.zobrist_hash(board.player), (turn, move)))
        engine1 = Engine(board, 2)
        move1 = engine1.negamax_iterative_deepening_root(board, 6, -1000000, 1000000)
        board.movecheck(board.player, move1[0], move1[1], move1[2], move1[3])
        print(board, f"\nPlayer 2 moved {move1[0], move1[1], move1[2], move1[3]}")
        if board.player == WHITE:
            opening_moves["BLACK"].append((board.zobrist_hash(board.player), (turn, move1)))
    
    return opening_moves

if __name__ == "__main__":
    # Initialize the opening book
    opening_book = {
        "WHITE": {},
        "BLACK": {}
    }
    num_games = 40 

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(simulate_game, game_id): game_id for game_id in range(num_games)}
        
        for future in as_completed(futures):
            game_id = futures[future]
            try:
                game_moves = future.result()
                for color in ["WHITE", "BLACK"]:
                    for zobrist_hash, move in game_moves[color]:
                        opening_book[color].setdefault(zobrist_hash, []).append(move)
            except Exception as exc:
                print(f'Game {game_id} generated an exception: {exc}')

    save_opening_book(opening_book, 'opening_book.pkl')
    print_move_statistics(opening_book)