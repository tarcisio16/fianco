import pygame
import sys
from chessboard import Chessboard
from fiancoai import FiancoAI
import time
from parameters import *

# Initialize pygame and screen dimensions
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FIANCO")
font = pygame.font.SysFont(None, FONT_SIZE)

# Initialize game state
chessboard = Chessboard()
player1,player2 = FiancoAI(chessboard,1), FiancoAI(chessboard,2)
selected_piece = None
game_over = False

# Draw the chess grid
def draw_grid():
    for x in range(MARGIN, MARGIN + GRID_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, MARGIN), (x, MARGIN + GRID_SIZE), 2)
    for y in range(MARGIN, MARGIN + GRID_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (MARGIN, y), (MARGIN + GRID_SIZE, y), 2)

# Draw the labels for grid coordinates and current player
def draw_labels():
    for i in range(9):
        screen.blit(font.render(LETTERS[i], True, BLACK), (i * CELL_SIZE + MARGIN, FONT_SIZE // 2))
        screen.blit(font.render(str(i + 1), True, BLACK), (10, MARGIN + i * CELL_SIZE))
    
    player_message = f"Player {chessboard.player}'s turn"
    screen.blit(font.render(player_message, True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 10))

# Draw player pieces on the grid
def draw_pieces():
    for white in chessboard.pl1:
        pygame.draw.circle(screen, WHITE, (white[1] * CELL_SIZE + MARGIN, white[0] * CELL_SIZE + MARGIN), CELL_SIZE // 2 - 10)
    for black in chessboard.pl2:
        pygame.draw.circle(screen, BLACK, (black[1] * CELL_SIZE + MARGIN, black[0] * CELL_SIZE + MARGIN), CELL_SIZE // 2 - 10)

# Draw legal moves and selected piece highlights
def draw_moves():
    chessboard.legalmoves()
    if selected_piece:
        pygame.draw.circle(screen, (255, 0, 0), (selected_piece[1] * CELL_SIZE + MARGIN, selected_piece[0] * CELL_SIZE + MARGIN), CELL_SIZE // 2 - 10)
    for move in chessboard.legal_moves:
        pygame.draw.circle(screen, (0, 255, 0), (move[3] * CELL_SIZE + MARGIN, move[2] * CELL_SIZE + MARGIN), CELL_SIZE // 2 - 25)

# Get the grid cell based on mouse position
def get_cell_at_position(pos):
    x = round(abs(pos[1] - MARGIN) / CELL_SIZE)
    y = round(abs(pos[0] - MARGIN) / CELL_SIZE)
    if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
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
        screen.blit(font.render(game_over_message, True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))

    pygame.display.flip()