import collections
import pygame
import sys
from board import Board
from parameters import *
import time
from smartengine import SmartEngine as ImprovedEngine
import threading
from copy import deepcopy
import json

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
backgroundsearch = None
depth = 0
grid_labels = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
turn = 0

def defaultdict_in_json(defaultdict_obj, file_path):
    dict_con_chiavi_str = {str(k): v for k, v in defaultdict_obj.items()}
    with open(file_path, 'w') as file:
        json.dump(dict_con_chiavi_str, file, indent=4)


def init_grid_labels():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            cell_name = get_cell_name(row, col)
            text = font.render(cell_name, True, BLACK_COLOR)
            text_rect = text.get_rect(center=(MARGIN + col * CELL_SIZE + CELL_SIZE // 2, 
                                              MARGIN + row * CELL_SIZE + CELL_SIZE // 2))
            grid_labels[row][col] = (text, text_rect)

def draw_grid():
    for i in range(BOARD_SIZE + 1):
        pygame.draw.line(screen, BLACK_COLOR, (MARGIN + i * CELL_SIZE, MARGIN), 
                         (MARGIN + i * CELL_SIZE, MARGIN + BOARD_SIZE * CELL_SIZE), 2)
        pygame.draw.line(screen, BLACK_COLOR, (MARGIN, MARGIN + i * CELL_SIZE), 
                         (MARGIN + BOARD_SIZE * CELL_SIZE, MARGIN + i * CELL_SIZE), 2)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            text, text_rect = grid_labels[row][col]
            screen.blit(text, text_rect)

def show_last_moves():
    start, end = previous_moves[-1]
    pygame.draw.circle(screen, RED_COLOR, 
                        (start[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, start[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                        CELL_SIZE // 2 - 25)
    pygame.draw.circle(screen, RED_COLOR, 
                        (end[1] * CELL_SIZE + MARGIN + CELL_SIZE // 2, end[0] * CELL_SIZE + MARGIN + CELL_SIZE // 2), 
                        CELL_SIZE // 2 - 25)


def get_cell_name(row, col):
 
    column_letter = chr(ord('a') + col)
    row_number = 9 - row  
    return f"{column_letter}{row_number}"

def draw_labels():
    global total_nodes_visited, depth
    for i in range(BOARD_SIZE):
        screen.blit(font.render(LETTERS[i], True, BLACK_COLOR), (i * CELL_SIZE + MARGIN, FONT_SIZE  ))
        screen.blit(font2.render(str(i + 1), True, BLACK_COLOR), (10, MARGIN + i * CELL_SIZE))

    player_message = f"Player {chessboard.player}'s turn"
    screen.blit(font.render(player_message, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT - FONT_SIZE - 10))
    
    global engine

    nodes = f"Nodes  b/w: {engine.nodes}, {engine.nodes}"
    movetimes = f"Move times b/w: {round(sum(white_time),2)}, {round(sum(black_time),2)}"
    d = f"Depth: {depth}"
    nodes_visted = f"Nodes visited: {total_nodes_visited}"
    
    screen.blit(font.render(nodes, True, BLACK_COLOR), (WIDTH - 500 , HEIGHT - 1 * FONT_SIZE - 70))
    screen.blit(font.render(movetimes, True, BLACK_COLOR), (WIDTH -500 , HEIGHT - 2 * FONT_SIZE - 70))
    screen.blit(font.render(d, True, BLACK_COLOR), (WIDTH -500 , HEIGHT - 3 * FONT_SIZE - 70))
    screen.blit(font.render(nodes_visted, True, BLACK_COLOR), (WIDTH -500 , HEIGHT - 4 * FONT_SIZE - 70))

    

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
    legal_moves = chessboard.generate_moves_unordered(chessboard.player)
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
    chessboard.movecheck(chessboard.player, from_pos[0],from_pos[1], to_pos[0], to_pos[1])
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
    global game_over, selected_piece, engine, previous_moves, backgroundsearch, depth, total_nodes_visited, turn
    init_grid_labels()
    
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                defaultdict_in_json(engine.history_heuristic, 'historyheuristicexit.json')
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
            elif event.type == pygame.K_u:


                move = previous_moves.pop()
                chessboard.move(chessboard.player, move[1][0], move[1][1], move[0][0], move[0][1])
                
            elif chessboard.player == PLAYER and game_over == 0 :
                engine.threadkill = True
                if backgroundsearch is not None:
                    backgroundsearch.join()
                start = time.time()
                engine.board = chessboard
                move = engine.negamax_iterative_deepening_root(chessboard, 12, max_time=5)
                end = time.time()
                total_nodes_visited = engine.nodes
                depth = engine.depth
                white_time.append(end-start)
                try:
                    chessboard.move(chessboard.player, move[0], move[1], move[2], move[3])
                    previous_moves.append(((move[0], move[1]), (move[2], move[3])))
                    engine.board = deepcopy(chessboard)
                    engine.threadkill = False
                    engine.nodes = 0
                    backgroundsearch = threading.Thread(target=engine.negamax_background_id, args=(engine.board, 10, 3- engine.player)) 
                    backgroundsearch.start()
                except Exception as e:
                    print(e)
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
            defaultdict_in_json(engine.history_heuristic, 'historyheuristicfinal.json')
            screen.blit(font.render(game_over_message, True, BLACK_COLOR), (WIDTH // 2 - FONT_SIZE, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(5)

if __name__ == "__main__":
    main_game_loop()