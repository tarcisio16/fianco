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
font2 = pygame.font.SysFont(None, FONT_SIZE // 2)

# Initialize game state
chessboard = Chessboard()
selected_piece = None
game_over = False

def draw_grid():
    for x in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, MARGIN), (x, MARGIN + BOARD_SIZE * CELL_SIZE), 2)
    for y in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (MARGIN, y), (MARGIN + BOARD_SIZE * CELL_SIZE, y), 2)

def draw_labels():
    for i in range(BOARD_SIZE):
        screen.blit(font.render(LETTERS[i], True, BLACK), (i * CELL_SIZE + MARGIN, FONT_SIZE // 2))
        screen.blit(font2.render(str(i + 1), True, BLACK), (10, MARGIN + i * CELL_SIZE))

    player_message = f"Player {chessboard.player}'s turn"
    screen.blit(font.render(player_message, True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 10))
    
    memory_text = f"HASH: {bin(chessboard.compute_zobrist_hash())}"
    screen.blit(font.render(memory_text, True, BLACK), (  10, HEIGHT - 2 * FONT_SIZE - 10))
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

def draw_moves():
    chessboard.legalmoves()
    legal_moves = chessboard.legal_moves
    if selected_piece:
        pygame.draw.circle(screen, (255, 0, 0), 
                           (selected_piece[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, selected_piece[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 10)
    for move in legal_moves:
        pygame.draw.circle(screen, (0, 255, 0), 
                           (move[3] * CELL_SIZE + MARGIN + CELL_SIZE // 2, move[2] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 25)

def get_cell_at_position(pos):
    x = (pos[0] - MARGIN) // CELL_SIZE
    y = (pos[1] - MARGIN) // CELL_SIZE
    if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
        return (y, x)
    return None

def reset_game():
    global chessboard, selected_piece, game_over
    chessboard = Chessboard()
    selected_piece = None
    game_over = False

def check_game_over():
    global game_over
    white_positions = chessboard.get_piece_positions(1)
    black_positions = chessboard.get_piece_positions(2)
    
    if any(piece[0] == BOARD_SIZE - 1 for piece in white_positions):
        game_over = True
        return "Player 1 Wins!"
    if any(piece[0] == 0 for piece in black_positions):
        game_over = True
        return "Player 2 Wins!"
    return None

def move_piece(from_pos, to_pos):
    chessboard.move(chessboard.player, from_pos, to_pos)

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

def main_game_loop():
    global game_over, selected_piece
    
    while True:
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
                    elif cell in chessboard.get_piece_positions(chessboard.player):
                        selected_piece = cell
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    reset_game()
                if event.key == pygame.K_u:
                    chessboard.undo()


        handle_input()

        screen.fill(GREY)
        draw_grid()
        draw_labels()
        draw_pieces()
        draw_moves()
        #draw_piece_number()

        game_over_message = check_game_over()
        if game_over_message:
            screen.blit(font.render(game_over_message, True, BLACK), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))

        pygame.display.flip()

if __name__ == "__main__":
    main_game_loop()