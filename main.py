import collections
import pygame
import sys
from board import Board
from parameters import *
from collections import deque
from enginewithtt import TTengine 

WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREY = (200, 200, 200)

# Initialize pygame and screen dimensions
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FIANCO")
font = pygame.font.SysFont(None, FONT_SIZE)
font2 = pygame.font.SysFont(None, FONT_SIZE // 2)

# Initialize game state
chessboard = Board()
engine = TTengine(chessboard, 1)
engine1 = TTengine(chessboard, 2)
selected_piece = None
game_over = False
previous = deque(maxlen=MAX_HISTORY)
valuewhite, valueblack = 0, 0

def draw_grid():
    for x in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK_COLOR, (x, MARGIN), (x, MARGIN + BOARD_SIZE * CELL_SIZE), 2)
    for y in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK_COLOR, (MARGIN, y), (MARGIN + BOARD_SIZE * CELL_SIZE, y), 2)

def draw_labels():
    for i in range(BOARD_SIZE):
        screen.blit(font.render(LETTERS[i], True, BLACK_COLOR), (i * CELL_SIZE + MARGIN, FONT_SIZE // 2))
        screen.blit(font2.render(str(i + 1), True, BLACK_COLOR), (10, MARGIN + i * CELL_SIZE))

    player_message = f"Player {chessboard.player}'s turn"
    screen.blit(font.render(player_message, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 10))
    values = f"White: {valuewhite} Black: {valueblack}"
    screen.blit(font.render(values, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 40))

def draw_pieces():
    for pos in chessboard.white_pieces:
        pygame.draw.circle(screen, WHITE_COLOR, 
                           (pos[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, pos[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 10)
    for pos in chessboard.black_pieces:
        pygame.draw.circle(screen, BLACK_COLOR, 
                           (pos[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, pos[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                           CELL_SIZE // 2 - 10)

def draw_moves():
    legal_moves = list(chessboard.generate_moves(chessboard.player))
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
    return (y, x) if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE else None

def reset_game():
    global chessboard, selected_piece, game_over
    chessboard = Board()
    selected_piece = None
    game_over = False

def check_game_over():
    if chessboard.black_pieces.intersection(WINNING_BLACK):
        game_over = True
        return "Player 2 wins!"
    elif chessboard.white_pieces.intersection(WINNING_WHITES):
        game_over = True
        return "Player 1 wins!"
    return None

def move_piece(from_pos, to_pos):
    
    global previous, valuewhite, valueblack, chessboard
    print(from_pos, to_pos)
    print(from_pos[0], from_pos[1], to_pos[0], to_pos[1])
    if chessboard.movecheck(chessboard.player,from_pos[0], from_pos[1], to_pos[0], to_pos[1]):
        previous.append((from_pos[0], from_pos[1], to_pos[0], to_pos[1]))
        
        
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
                y, x = selected_piece
                move_piece((y, x), (y + dy, x + dx))
                break

def main_game_loop():
    global game_over, selected_piece, previous, valuewhite, valueblack
    
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
                        valuewhite = chessboard.evaluation_function(WHITE)
                        valueblack = chessboard.evaluation_function(BLACK)
                        
                        selected_piece = None
                    else:
                        selected_piece = cell
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    reset_game()
                if event.key == pygame.K_u:
                    if len(previous) == 0:
                        continue
                    move = previous.pop()
                    chessboard.undomove(3 - chessboard.player, move[:2], move[2:])
                    chessboard.player ^= 3

        handle_input()

        screen.fill(GREY)
        draw_grid()
        draw_labels()
        draw_pieces()
        draw_moves()

        game_over_message = check_game_over()
        if game_over_message:
            screen.blit(font.render(game_over_message, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))

        pygame.display.flip()

if __name__ == "__main__":
    main_game_loop()