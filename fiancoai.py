from chessboard import Chessboard
import random

class FiancoAI:
    def __init__(self, chessboard, color):
        self.chessboard = chessboard
        self.color = color
    
    def get_move(self):
        return self.random_move()[0], self.random_move()[1]
        
    def random_move(self):
        # Ensure that legalmoves() returns a list of moves
        moves = self.chessboard.legalmoves()  
        if moves:
            # Pick a random move
            move = random.choice(moves)
            # Convert move to a format with start and end positions agitis lists
            move_from = (move[0], move[1])
            move_to = (move[2], move[3])
            return move_from, move_to
        else:
            # Return None if no moves are available
            return None
