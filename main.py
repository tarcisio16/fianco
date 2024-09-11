import pygame
import sys
from chessboard import Chessboard
from fiancoai import FiancoAI
import time

# Initialize pygame and screen dimensions
pygame.init()
width, height = 700, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("FIANCO")

# Define game colors and dimensions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

TYPE_OF_GAME =  1 # 0: "human VS human" 
                   # 1: "ai VS ai" 
                   # 2: "ai vs human"
DELAY_AI = 0.2
margin = 70
grid_size = 500
cell_size = grid_size // 8
font_size = 30
font = pygame.font.SysFont(None, font_size)

# Initialize game state
chessboard = Chessboard()
player1 = FiancoAI(chessboard,1)
player2 = FiancoAI(chessboard,2)
selected_piece = None
game_over = False

# Draw the chess grid
def draw_grid():
    for x in range(margin, margin + grid_size + 1, cell_size):
        pygame.draw.line(screen, BLACK, (x, margin), (x, margin + grid_size), 2)
    for y in range(margin, margin + grid_size + 1, cell_size):
        pygame.draw.line(screen, BLACK, (margin, y), (margin + grid_size, y), 2)

# Draw the labels for grid coordinates and current player
def draw_labels():
    letters = "ABCDEFGHI"
    for i in range(9):
        screen.blit(font.render(letters[i], True, BLACK), (i * cell_size + margin, font_size // 2))
        screen.blit(font.render(str(i + 1), True, BLACK), (10, margin + i * cell_size))
    
    player_message = f"Player {chessboard.player}'s turn"
    screen.blit(font.render(player_message, True, BLACK), (width // 2 - font_size, height - font_size - 10))

# Draw player pieces on the grid
def draw_pieces():
    for white in chessboard.pl1:
        pygame.draw.circle(screen, WHITE, (white[1] * cell_size + margin, white[0] * cell_size + margin), cell_size // 2 - 10)
    for black in chessboard.pl2:
        pygame.draw.circle(screen, BLACK, (black[1] * cell_size + margin, black[0] * cell_size + margin), cell_size // 2 - 10)

# Draw legal moves and selected piece highlights
def draw_moves():
    chessboard.legalmoves()
    if selected_piece:
        pygame.draw.circle(screen, (255, 0, 0), (selected_piece[1] * cell_size + margin, selected_piece[0] * cell_size + margin), cell_size // 2 - 10)
    for move in chessboard.legal_moves:
        pygame.draw.circle(screen, (0, 255, 0), (move[3] * cell_size + margin, move[2] * cell_size + margin), cell_size // 2 - 25)

# Get the grid cell based on mouse position
def get_cell_at_position(pos):
    x = round(abs(pos[1] - margin) / cell_size)
    y = round(abs(pos[0] - margin) / cell_size)
    if 0 <= x <= 8 and 0 <= y <= 8:
        return (x, y)
    return None

# Reset game to initial state
def reset_game():
    global chessboard, selected_piece, game_over
    chessboard = Chessboard()
    selected_piece = None
    game_over = False

# Check if the game has been won
def check_game_over():
    global game_over
    for piece in chessboard.pl1:
        if piece[0] == 8:
            game_over = True
            return "Player 1 Wins!"
    for piece in chessboard.pl2:
        if piece[0] == 0:
            game_over = True
            return "Player 2 Wins!"
    return None

# Move a piece from one position to another
def move_piece(from_pos, to_pos):
    chessboard.move(chessboard.player, from_pos, to_pos)

# Handle user input for piece movement and resetting the game
def handle_input():
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_BACKSPACE]:  # Restart the game on Backspace
        reset_game()
        return

    if selected_piece:
        move_directions = {
            1: [(pygame.K_UP, (-1, 0)), (pygame.K_DOWN, (1, 0)), (pygame.K_LEFT, (0, -1)), (pygame.K_RIGHT, (0, 1))],
            2: [(pygame.K_w, (-1, 0)), (pygame.K_s, (1, 0)), (pygame.K_a, (0, -1)), (pygame.K_d, (0, 1))]
        }
        for key, (dx, dy) in move_directions[chessboard.player]:
            if keys[key]:
                x, y = selected_piece
                move_piece((x, y), (x + dx, y + dy))
                break

# Main game loop
while True:
    if TYPE_OF_GAME == 0:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    pos = pygame.mouse.get_pos()
                    cell = get_cell_at_position(pos)
                    if cell:
                        if selected_piece:
                            move_piece(selected_piece, cell)
                            selected_piece = None
                        elif chessboard.board[cell[0], cell[1]] == chessboard.player:
                            selected_piece = cell
    if TYPE_OF_GAME == 1:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        if not game_over:
            move_from, move_to = None, None
            if chessboard.player == 1:
                move_from, move_to = player1.get_move()
            else:
                move_from, move_to = player2.get_move()
            chessboard.move(chessboard.player, move_from, move_to)
        time.sleep(DELAY_AI)
                
    if TYPE_OF_GAME == 2:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and chessboard.player == 1:
                    pos = pygame.mouse.get_pos()
                    cell = get_cell_at_position(pos)
                    if cell:
                        if selected_piece:
                            move_piece(selected_piece, cell)
                            selected_piece = None
                        elif chessboard.board[cell[0], cell[1]] == chessboard.player:
                            selected_piece = cell
                elif not game_over and chessboard.player == 2:
                    move_from, move_to = player2.get_move()
                    chessboard.move(chessboard.player, move_from, move_to)
                    time.sleep(DELAY_AI)
 

    handle_input()

    screen.fill(GREY)
    draw_grid()
    draw_labels()
    draw_pieces()
    draw_moves()

    game_over_message = check_game_over()
    if game_over_message:
        screen.blit(font.render(game_over_message, True, BLACK), (width // 2 - font_size, height // 2))

    pygame.display.flip()