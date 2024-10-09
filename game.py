from board import Board
from quiescentengine import QuiescentEngine as Engine
import gc  # Garbage collection
import concurrent.futures
from collections import defaultdict

# Define feature sets for the agents
feature_sets = [
    {"FIANCO_BONUS": 4, "POSITIONAL_BONUS": 2, "SECONDLASTBONUS": 0, "THIRDANDCAPTURE_BONUS": 0, "PIECE_BONUS": 0},
    {'FIANCO_BONUS': 6, 'POSITIONAL_BONUS': 2, 'SECONDLASTBONUS': 0, 'THIRDANDCAPTURE_BONUS': 0, 'PIECE_BONUS': 0},
    {'FIANCO_BONUS': 4, 'POSITIONAL_BONUS': 3, 'SECONDLASTBONUS': 0, 'THIRDANDCAPTURE_BONUS': 0, 'PIECE_BONUS': 0},
    {'FIANCO_BONUS': 6, 'POSITIONAL_BONUS': 3, 'SECONDLASTBONUS': 0, 'THIRDANDCAPTURE_BONUS': 0, 'PIECE_BONUS': 0},
    {'FIANCO_BONUS': 4, 'POSITIONAL_BONUS': 4, 'SECONDLASTBONUS': 0, 'THIRDANDCAPTURE_BONUS': 0, 'PIECE_BONUS': 0},
    {'FIANCO_BONUS': 6, 'POSITIONAL_BONUS': 4, 'SECONDLASTBONUS': 0, 'THIRDANDCAPTURE_BONUS': 0, 'PIECE_BONUS': 0},
    {"FIANCO_BONUS": 1, "POSITIONAL_BONUS": 2, "SECONDLASTBONUS": 0, "THIRDANDCAPTURE_BONUS": 0, "PIECE_BONUS": 0}
]

# Dictionary to store move frequencies
move_frequencies = defaultdict(int)

def game(white_fs, black_fs):
    chessboard = Board()
    engine_white = Engine(chessboard, 1, white_fs, 24)  # White uses feature set
    engine_black = Engine(chessboard, 2, black_fs, 24)  # Black uses feature set
    moves = 0
    
    while True:
        try:
            if chessboard.player == 1:
                move = engine_white.negamax_iterative_deepening_root(chessboard, 7, -1000000, 1000000, 2.5)
            else:
                move = engine_black.negamax_iterative_deepening_root(chessboard, 7, -1000000, 1000000, 2.5)

            # Store the move in the move frequency dictionary
            move_frequencies[tuple(move)] += 1
            
            chessboard.move(chessboard.player, move[0], move[1], move[2], move[3])
            moves += 1
            
            winner = chessboard.checkwin()
            if winner != 0:
                print("Winner is", winner, "after", moves, "moves")
                return winner

            chessboard.player ^= 3  # Switch player
            
        except Exception as e:
            print("Error:", str(e))
            print("Winner is", 3 - chessboard.player, "after", moves, "moves")
            return 3 - chessboard.player

if __name__ == "__main__":
    total_agents = len(feature_sets)
    wins = [0] * total_agents  # Initialize wins for each agent

    # Each feature set plays against every other feature set, both as white and black
    for i in range(total_agents):
        for j in range(total_agents):
            if i != j:  # Ensure players are different
                print(f"Starting match between Agent {i + 1} (White) and Agent {j + 1} (Black)")

                # Parallel execution of the match
                with concurrent.futures.ProcessPoolExecutor(max_workers=7) as executor:
                    results = [executor.submit(game, feature_sets[i], feature_sets[j]) for _ in range(2)]  # 5 games

                    for future in concurrent.futures.as_completed(results):
                        winner = future.result()
                        wins[winner - 1] += 1  # Update win count for the winning agent
                        print(f"Game finished with winner: Player {winner}")

                gc.collect()  # Collect garbage

                # Now switch roles: Agent j as White and Agent i as Black
                print(f"Starting match between Agent {j + 1} (White) and Agent {i + 1} (Black)")

                with concurrent.futures.ProcessPoolExecutor(max_workers=7) as executor:
                    results = [executor.submit(game, feature_sets[j], feature_sets[i]) for _ in range(2)]  
                    

                    for future in concurrent.futures.as_completed(results):
                        winner = future.result()
                        wins[winner - 1] += 1  # Update win count for the winning agent
                        print(f"Game finished with winner: Player {winner}")

                gc.collect()  # Collect garbage

    # Open the text file in write mode
    with open("tournament_results.txt", "w") as file:
        # Print the overall results
        print("Tournament Results:", file=file)
        for index, count in enumerate(wins):
            print(f"Player {index + 1} wins: {count} times with feature set: {feature_sets[index]}", file=file)

        # Print move frequency data
        print("\nFrequent Moves:", file=file)
        sorted_moves = sorted(move_frequencies.items(), key=lambda x: x[1], reverse=True)
        for move, frequency in sorted_moves:
            print(f"Move {move} occurred {frequency} times", file=file)