from board import Board
from quiescentengine import ImprovedEngine as Engine

if __name__ == "__main__":

    for game in range(20):
        
        board = Board()
        engine = Engine(board, 1)
        engine1 = Engine(board, 2)
        print(board)
        while True:
            move = engine.negamax_iterative_deepening_root(board, 5, -1000000, 1000000)
            board.move(board.player, move[0], move[1], move[2], move[3])
            board.player = 3 - board.player
            print(board)
            if board.checkwin():
                print("Player 1 wins!")
                break
            move1 = input("Enter move: ").split()
            board.move(board.player, move1[0], move1[1], move1[2], move1[3])
            print(board)
            if board.checkwin():
                print("Player 2 wins!")
                break
            board.player = 3 - board.player 