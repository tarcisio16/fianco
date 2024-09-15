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
player1 = FiancoAI(chessboard, 1)
player2 = FiancoAI(chessboard, 2)
selected_piece = None
game_over = False
delay = 0  # Delay for AI thinking

# Draw the chess grid
def draw_grid():
    for x in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, MARGIN), (x, MARGIN + BOARD_SIZE * CELL_SIZE), 2)
    for y in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (MARGIN, y), (MARGIN + BOARD_SIZE * CELL_SIZE, y), 2)

# Draw the labels for grid coordinates and current player
def draw_labels():
    for i in range(BOARD_SIZE):
        screen.blit(font.render(LETTERS[i], True, BLACK), (i * CELL_SIZE + MARGIN, FONT_SIZE // 2))
        screen.blit(font.render(str(i + 1), True, BLACK), (10, MARGIN + i * CELL_SIZE))
    
    player_message = f"Player {chessboard.player}'s turn"
    screen.blit(font.render(player_message, True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 10))

# Draw player pieces on the grid
def draw_pieces():
    for pos in chessboard.get_piece_positions(1):
        pygame.draw.circle(screen, WHITE, 
                           (pos[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, pos[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 10)
    for pos in chessboard.get_piece_positions(2):
        pygame.draw.circle(screen, BLACK, 
                           (pos[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, pos[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 10)

def draw_piece_number():
    white_pieces = chessboard.count_pieces(1)
    black_pieces = chessboard.count_pieces(2)
    screen.blit(font.render(f"White: {white_pieces}", True, BLACK), (WIDTH - 10 * FONT_SIZE, HEIGHT - FONT_SIZE - 10))
    screen.blit(font.render(f"Black: {black_pieces}", True, BLACK), (WIDTH - 10 * FONT_SIZE, HEIGHT - 2 * FONT_SIZE - 10))

# Draw legal moves and selected piece highlights
def draw_moves():
    chessboard.legalmoves()
    legal_moves = chessboard.legal_moves
    if selected_piece:
        pygame.draw.circle(screen, (255, 0, 0), 
                           (selected_piece[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, selected_piece[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 10)
    for move in legal_moves:
        # move[2] and move[3] are the destination coordinates (y1, x1)
        pygame.draw.circle(screen, (0, 255, 0), 
                           (move[3] * CELL_SIZE + MARGIN + CELL_SIZE // 2, move[2] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 25)

# Get the grid cell based on mouse position
def get_cell_at_position(pos):
    x = (pos[0] - MARGIN) // CELL_SIZE
    y = (pos[1] - MARGIN) // CELL_SIZE
    if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
        return (y, x)
    return None

# Reset game to initial state
def reset_game():
    global chessboard, player2, selected_piece, game_over
    chessboard = Chessboard()
    player2 = FiancoAI(chessboard, 2)
    selected_piece = None
    game_over = False

# Check if the game has been won
def check_game_over():
    white_positions = chessboard.get_piece_positions(1)
    black_positions = chessboard.get_piece_positions(2)
    
    if any(piece[0] == BOARD_SIZE - 1 for piece in white_positions):
        return "Player 1 Wins!"
    if any(piece[0] == 0 for piece in black_positions):
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
        for key, (dy, dx) in move_directions[chessboard.player]:
            if keys[key]:
                x, y = selected_piece
                move_piece((y, x), (y + dy, x + dx))
                break

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                reset_game()
            elif event.key == pygame.K_u:
                chessboard.undo()
    
    # Player 1 (AI) move
    if chessboard.player == 1 and not game_over:
        y0, x0, y1, x1 = player1.get_move()
        if (y0, x0) and (y1, x1):
            chessboard.move(1, [y0, x0], [y1, x1])
        screen.blit(font.render("AI is thinking...", True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))
        pygame.display.flip()
        time.sleep(delay)
    
    # Player 2 (AI) move
    elif chessboard.player == 2 and not game_over:
        y0, x0, y1, x1 = player2.get_move()
        if (y0, x0) and (y1, x1):
            chessboard.move(2, [y0, x0], [y1, x1])
        screen.blit(font.render("AI is thinking...", True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))
        pygame.display.flip()
        time.sleep(delay)

    handle_input()

    # Drawing and updating screen
    screen.fill(GREY)
    draw_grid()
    draw_labels()
    draw_pieces()
    draw_moves()
    draw_piece_number()

    game_over_message = check_game_over()
    if game_over_message:
        screen.blit(font.render(game_over_message, True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))
        game_over = True

    pygame.display.flip()