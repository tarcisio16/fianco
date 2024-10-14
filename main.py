import pygame
import sys
from board import Board
import traceback
from parameters import *
import time
from quiescentengine import QuiescentEngine as ImprovedEngine

WHITE_COLOR = (255, 255, 255)
BLACK_COLOR = (0, 0, 0)
GREY = (200, 200, 200)
RED_COLOR = (255, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FIANCO")
font = pygame.font.SysFont(None, FONT_SIZE)
font2 = pygame.font.SysFont(None, FONT_SIZE // 2)
clock = pygame.time.Clock()

PLAYER = BLACK
chessboard = Board()
engine = ImprovedEngine(chessboard, PLAYER, transposition_table_size=28)
selected_piece = None
game_over = False
black_time = []
white_time = []
previous_moves = []
total_nodes_visited = 0
total_hits = 0



def draw_grid():
    for x in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK_COLOR, (x, MARGIN), (x, MARGIN + BOARD_SIZE * CELL_SIZE), 2)
    for y in range(MARGIN, MARGIN + BOARD_SIZE * CELL_SIZE + 1, CELL_SIZE):
        pygame.draw.line(screen, BLACK_COLOR, (MARGIN, y), (MARGIN + BOARD_SIZE * CELL_SIZE, y), 2)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            cell_name = get_cell_name(row, col)
            text = font.render(cell_name, True, BLACK_COLOR)  #
            text_rect = text.get_rect(center=(MARGIN + col * CELL_SIZE + CELL_SIZE // 2, 
                                                MARGIN + row * CELL_SIZE + CELL_SIZE // 2)) 
            screen.blit(text, text_rect)  

def get_cell_name(row, col):
    column_letter = chr(ord('a') + col)  
    row_number = 9 - row  
    return f"{column_letter}{row_number}"
def draw_labels():
    for i in range(BOARD_SIZE):
        screen.blit(font.render(LETTERS[i], True, BLACK_COLOR), (i * CELL_SIZE + MARGIN, FONT_SIZE  ))
        screen.blit(font2.render(str(i + 1), True, BLACK_COLOR), (10, MARGIN + i * CELL_SIZE))

    player_message = f"Player {chessboard.player}'s turn"
    screen.blit(font.render(player_message, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 10))

    global engine
    valueblack = engine.evaluation_function(WHITE)
    valuewhite= -valueblack
    values = f"White: {valuewhite} Black: {valueblack}"
    screen.blit(font.render(values, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 40))

    nodes = f"Nodes  b/w: {engine.nodes}, {engine.nodes}"
    movetimes = f"Move times b/w: {round(sum(white_time),2)}, {round(sum(black_time),2)}"
    depth = f"Depth: {engine.depth}"
    
    screen.blit(font.render(nodes, True, BLACK_COLOR), (WIDTH - 500 , HEIGHT - 2 * FONT_SIZE - 70))
    screen.blit(font.render(movetimes, True, BLACK_COLOR), (WIDTH -500 , HEIGHT - 3 * FONT_SIZE - 70))
    screen.blit(font.render(depth, True, BLACK_COLOR), (WIDTH -500 , HEIGHT - 6 * FONT_SIZE - 70))

def show_last_moves():
    start, end = previous_moves[-1]
    pygame.draw.circle(screen, RED_COLOR, 
                        (start[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, start[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                        CELL_SIZE // 2 - 25)
    pygame.draw.circle(screen, RED_COLOR, 
                        (end[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, end[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                        CELL_SIZE // 2 - 25)
    

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
    engine = ImprovedEngine(chessboard, 2)
    selected_piece = None
    game_over = False

def check_game_over():
    return chessboard.checkwin()

def move_piece(from_pos, to_pos):
    if chessboard.movecheck(chessboard.player, from_pos[0],from_pos[1], to_pos[0], to_pos[1]):
        previous_moves.append((from_pos, to_pos))

def handle_input():
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_BACKSPACE]:  
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
    global game_over, selected_piece, engine, previous_moves
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and chessboard.player == 3 - PLAYER:
                pos = pygame.mouse.get_pos()
                cell = get_cell_at_position(pos)
                if cell:
                    if selected_piece:
                        move_piece(selected_piece, cell)
                        selected_piece = None
                    else:
                        selected_piece = cell
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    reset_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                move = previous_moves.pop()
                chessboard.undomove(3- chessboard.player,*move[0],*move[1])
                chessboard.player ^= 3  
                
                
                    

            elif chessboard.player == PLAYER and game_over == 0 :
                start = time.time()
                move = engine.negamax_iterative_deepening_root(chessboard, 12, max_time=9)
                end = time.time()
                white_time.append(end-start)
                try:
                    chessboard.move(chessboard.player, move[0], move[1], move[2], move[3])
                    previous_moves.append(((move[0], move[1]), (move[2], move[3])))
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    pygame.quit()
                    sys.exit()
                
                chessboard.player ^= 3
        handle_input()

        screen.fill(GREY)
        draw_labels()
        draw_pieces()
        draw_grid()
        if previous_moves:
            show_last_moves()
        draw_moves()


        game_over_message = check_game_over()
        if game_over_message:
            screen.blit(font.render(game_over_message, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main_game_loop()