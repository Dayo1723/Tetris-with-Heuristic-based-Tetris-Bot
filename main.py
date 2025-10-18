import pygame
from pygame.image import load
from library.timer import Timer
from library.ai_engine import AITetrisEngine
from library.constants import *
import sys
import os
from os import path
from library.tetrominos.block import Block

timers = {
    'horizontal move': Timer(MOVE_WAIT_TIME),
    'rotate': Timer(ROTATE_WAIT_TIME),
    'fast drop': Timer(FAST_DROP_WAIT_TIME),
    'toggle': Timer(TOGGLE_WAIT_TIME),
    'hard drop': Timer(HARD_DROP_COOLDOWN),
    'AI cooldown': Timer(200)
}

AI_mode = False

pygame.init()

engine = AITetrisEngine()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPHICS_DIR = os.path.join(BASE_DIR, "library/graphics")
font_path = os.path.join(GRAPHICS_DIR, "Retro Gaming.ttf")

font = pygame.font.Font(font_path, 25)

# Setup
screen = pygame.display.set_mode((TETRO_GRID_WIDTH, TETRO_GRID_HEIGHT))
pygame.display.set_caption('Heuristic Tetris Bot')
clock = pygame.time.Clock()

canvas = pygame.display.set_mode((TETRO_GRID_WIDTH + X_PADDING, TETRO_GRID_HEIGHT + Y_PADDING))
CANVAS_WIDTH = canvas.get_width()
CANVAS_HEIGHT = canvas.get_height()

shape_surfaces = {shape: load(path.join(GRAPHICS_DIR, f'{shape}.png')).convert_alpha() for shape in
                  shapes}

preview = pygame.Surface((CANVAS_WIDTH - TETRO_GRID_WIDTH - Y_PADDING / 2 - Y_PADDING, TETRO_GRID_HEIGHT / 4))
preview_rect = preview.get_rect(topright=(CANVAS_WIDTH - Y_PADDING / 2, Y_PADDING / 2))
score = pygame.Surface((CANVAS_WIDTH - TETRO_GRID_WIDTH - Y_PADDING / 2 - Y_PADDING, TETRO_GRID_HEIGHT / 4))
score_rect = preview.get_rect(topright=(CANVAS_WIDTH - Y_PADDING / 2, Y_PADDING / 2 + CELL_SIZE * 7.5))
border = pygame.Surface((TETRO_GRID_WIDTH, TETRO_GRID_HEIGHT))
border_rect = border.get_rect(topleft=(Y_PADDING / 2, Y_PADDING / 2))
info = pygame.Surface((CANVAS_WIDTH - TETRO_GRID_WIDTH - Y_PADDING / 2 - Y_PADDING, TETRO_GRID_HEIGHT / 4))
info_rect = info.get_rect(bottomright=(CANVAS_WIDTH - Y_PADDING / 2, CANVAS_HEIGHT - Y_PADDING / 2))


def score_constructor(pos, text):
    text_surface = font.render(f'{text[0]}: {text[1]}', True, 'black')
    text_rect = text_surface.get_rect(center=pos)
    score.blit(text_surface, text_rect)


def display_score(scr, level, lines):
    score.fill(WHITE)

    for i, text in enumerate([('Score', scr), ('Level', level), ('Lines', lines)]):
        x = score.get_width() / 2
        y = int(i) * score.get_height() / 3 + CELL_SIZE * 0.8
        score_constructor((x, y), text)

    canvas.blit(score, score_rect)
    pygame.draw.rect(canvas, BLACK, score_rect, 6)


def info_constructor(pos, text):
    text_surface = font.render(f'{text[0]}: {text[1]}', True, 'black')
    text_rect = text_surface.get_rect(center=pos)
    options_surface = font.render(f'OPTIONS', True, 'black').convert_alpha()
    options_rect = options_surface.get_rect(center=(info.get_width() / 2, 2 * info.get_height() / 3 + CELL_SIZE * 0.8))
    info.blit(options_surface, options_rect)
    info.blit(text_surface, text_rect)


def display_info():
    info.fill(WHITE)

    if AI_mode:
        ai = 'ON'
    else:
        ai = 'OFF'

    if engine.is_muted():
        mute = 'ON'
    else:
        mute = 'OFF'

    for i, text in enumerate([('AI mode', ai), ('Mute', mute)]):
        x = info.get_width() / 2
        y = int(i) * info.get_height() / 3 + CELL_SIZE * 0.8
        info_constructor((x, y), text)

    canvas.blit(info, info_rect)

    pygame.draw.rect(canvas, BLACK, info_rect, 6)


def display_next_piece(shape):
    preview.fill(WHITE)

    shape_surface = shape_surfaces[shape.name]

    # Define a scaling factor (e.g., 1.5 times the original size)
    scaling_factor = 2.2

    # Get original dimensions
    original_width, original_height = shape_surface.get_size()

    # Calculate new dimensions using the scaling factor
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)

    # Scale the image
    scaled_surface = pygame.transform.scale(shape_surface, (new_width, new_height))

    # Calculate position to center the image in the preview surface
    x = preview.get_width() // 2
    y = preview.get_height() // 2
    rect = scaled_surface.get_rect(center=(x, y))

    preview.blit(scaled_surface, rect)

    # Draw the preview surface onto the canvas
    canvas.blit(preview, preview_rect)

    pygame.draw.rect(canvas, BLACK, preview_rect, 6)


def render():
    screen.fill(BG)  # Clear screen
    grid = engine.dynamic_grid()

    # Draw grid cells
    for y_idx in range(GRID_HEIGHT_INVISIBLE, GRID_HEIGHT):
        for x_idx in range(GRID_WIDTH):
            block = grid[y_idx][x_idx]
            if isinstance(block, Block):  # Check if there's a Block instance
                block.rect.topleft = (x_idx * CELL_SIZE + Y_PADDING / 2,
                                      (y_idx - GRID_HEIGHT_INVISIBLE) * CELL_SIZE + Y_PADDING / 2)
                screen.blit(block.sprite, block.rect)
            else:
                pygame.draw.rect(screen, TBG,
                                 (x_idx * CELL_SIZE + Y_PADDING / 2,
                                  (y_idx - GRID_HEIGHT_INVISIBLE) * CELL_SIZE + Y_PADDING / 2,
                                  CELL_SIZE, CELL_SIZE))

    pygame.draw.line(screen, BLACK,
                     (Y_PADDING / 2, Y_PADDING / 2),
                     (Y_PADDING / 2 + TETRO_GRID_WIDTH, Y_PADDING / 2),
                     6)
    pygame.draw.line(screen, BLACK,
                     (Y_PADDING / 2, Y_PADDING / 2 + TETRO_GRID_HEIGHT),
                     (Y_PADDING / 2 + TETRO_GRID_WIDTH, Y_PADDING / 2 + TETRO_GRID_HEIGHT),
                     6)

    pygame.draw.line(screen, BLACK,
                     (Y_PADDING / 2, Y_PADDING / 2),
                     (Y_PADDING / 2, Y_PADDING / 2 + TETRO_GRID_HEIGHT),
                     6)
    pygame.draw.line(screen, BLACK,
                     (TETRO_GRID_WIDTH + Y_PADDING / 2, Y_PADDING / 2),
                     (TETRO_GRID_WIDTH + Y_PADDING / 2, Y_PADDING / 2 + TETRO_GRID_HEIGHT),
                     6)


def timer_update(timers):
    for timer in timers.values():
        timer.update()


def handle_input():
    global AI_mode

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                AI_mode = not AI_mode
            if event.key == pygame.K_SPACE:
                engine.harddrop()
            if event.key == pygame.K_r:
                engine.reset()
            if event.key == pygame.K_m:
                engine.mute_unmute()

    keys = pygame.key.get_pressed()

    if not timers['horizontal move'].active:
        if keys[pygame.K_LEFT]:
            engine.tetromino_left()
            timers['horizontal move'].activate()
        if keys[pygame.K_RIGHT]:
            engine.tetromino_right()
            timers['horizontal move'].activate()

    if not timers['fast drop'].active:
        if keys[pygame.K_DOWN]:
            engine.tetromino_down()
            timers['fast drop'].activate()

    if not timers['rotate'].active:
        if keys[pygame.K_UP]:
            engine.tetromino_rotate()
            timers['rotate'].activate()


def ai_play():
    if not engine.game_is_over:
        if not timers['AI cooldown'].active:
            r, x, y = engine.generate_best_move()
            engine.current_tetromino['tetro'].set_rotation_i(r)
            engine.current_tetromino['x'] = x
            engine.current_tetromino['y'] = y
            engine.harddrop()
            timers['AI cooldown'].activate()


def machine_mode_game_loop():
    global AI_mode

    while True:

        handle_input()

        if AI_mode:
            ai_play()
        elif engine.should_game_tick():
            engine.next_game_tick()

        timer_update(timers)

        render()

        display_next_piece(engine.next_tetromino)

        display_score(engine.game_score, engine.game_level, engine.game_lines_cleared)

        display_info()

        pygame.display.flip()


        clock.tick(60)


def machine_mode():
    machine_mode_game_loop()


if __name__ == "__main__":
    machine_mode()
