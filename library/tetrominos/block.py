import pygame
from library.constants import *
import os

# Get the base directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPHICS_DIR = os.path.join(BASE_DIR, "..", "graphics")

# Use the relative path for each sprite
sprite_paths = {
    'L': os.path.join(GRAPHICS_DIR, "orange.png"),
    'O': os.path.join(GRAPHICS_DIR, "yellow.png"),
    'J': os.path.join(GRAPHICS_DIR, "dark_blue.png"),
    'I': os.path.join(GRAPHICS_DIR, "light_blue.png"),
    'Z': os.path.join(GRAPHICS_DIR, "red.png"),
    'S': os.path.join(GRAPHICS_DIR, "green.png"),
    'T': os.path.join(GRAPHICS_DIR, "magenta.png")
}


class Block:
    def __init__(self, shape_type):

        # Check if shape_type is valid
        if shape_type not in sprite_paths:
            raise ValueError(f"No sprite found for shape type '{shape_type}'")

        sprite_path = sprite_paths[shape_type]
        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (CELL_SIZE, CELL_SIZE))
        self.rect = self.sprite.get_rect()  # Initialize the rectangle for positioning




