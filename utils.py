import pygame
import os
import sys

def read_file_to_list(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read all lines and strip whitespace from each
            lines = [line.strip() for line in file.readlines()]
        return lines
    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def extract_sprites(sheet, rows, columns):
    """
    Extracts individual sprites from a grid-like sprite sheet.

    Args:
        sheet (pygame.Surface): The sprite sheet image.
        rows (int): Number of rows in the sprite sheet.
        columns (int): Number of columns in the sprite sheet.

    Returns:
        list[pygame.Surface]: A list of extracted sprite surfaces.
    """
    sprites = []
    sprite_width = sheet.get_width() // columns
    sprite_height = sheet.get_height() // rows

    for row in range(rows):
        for col in range(columns):
            rect = pygame.Rect(col * sprite_width, row * sprite_height, sprite_width, sprite_height)
            sprites.append(sheet.subsurface(rect))

    return sprites

def rescale(list_of_surfaces, new_width, new_height):
    return [pygame.transform.scale(surface, (new_width, new_height)) for surface in list_of_surfaces]
