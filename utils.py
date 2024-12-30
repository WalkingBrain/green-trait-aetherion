import pygame
import os
import sys
from pathlib import Path

def path_correction(path, to_prefix="_internal\\"):
    if Path(to_prefix + path).exists() and False:
        return resource_path(to_prefix + path)
    else:
        return path
    
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
    """
    Get the absolute path to a resource, works for development and PyInstaller.
    
    :param relative_path: Path to the resource (relative to the script or bundled app).
    :return: Absolute path to the resource.
    """
    # When running as a bundle (PyInstaller)
    if getattr(sys, '_MEIPASS', False):
        return os.path.join(sys._MEIPASS, relative_path)
    
    # When running as a script
    return os.path.join(os.path.abspath("."), relative_path)

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

def rescale(list_of_surfaces: list[pygame.Surface], new_width: int, new_height: int):
    return [pygame.transform.scale(surface, (new_width, new_height)) for surface in list_of_surfaces]

def flip(list_of_surfaces: list[pygame.Surface], horizontal: bool, vertical: bool):
    return [pygame.transform.flip(surface, horizontal, vertical) for surface in list_of_surfaces]

def clamp_velocity(velocity, max_speed):
    velocity.x = max(-max_speed, min(velocity.x, max_speed))
    velocity.y = max(-max_speed, min(velocity.y, max_speed))
    return velocity

