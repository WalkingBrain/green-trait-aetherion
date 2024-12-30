import pygame
from utils import read_file_to_list, path_correction

class Sprite:
    def __init__(self, texture_name, x: int, y: int, width: int, height: int, alpha=255, texture_directory=path_correction("assets/textures/")):
        if isinstance(texture_name, pygame.Surface):
            self.surface = texture_name
        else:
            self.surface = pygame.transform.scale(pygame.image.load(f"{texture_directory}{texture_name}"), (width, height))

        
        self.texture_name = texture_name

        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)

        self.width = width
        self.height = height
        self.size = pygame.Vector2(width, height)

        self.alpha = alpha
        self.hidden = False

    def render(self, surface: pygame.Surface):
        if self.hidden:
            return None
        if hasattr(self, "hp"):
            if self.hp <= 0:
                return None
        
        self.surface.set_alpha(self.alpha)
        surface.blit(self.surface, self.pos)

    def rect(self, transparent: bool=True):
        if hasattr(self, "hp"):
            if self.hp <= 0:
                return pygame.Rect(0, 0, 0, 0)
        if not transparent:
            return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        
        else:
            no_transparency = crop_to_content(self.surface)
            return pygame.Rect(self.pos.x, self.pos.y, no_transparency.get_width(), no_transparency.get_height())

    def cap(self, screen, has_text=False, PADDING=10, text=None):
        if text is None or text.height == 0:
            has_text = False

        self.pos.x = max(PADDING, min(self.pos.x, screen.get_width() - self.width))
        self.pos.y = max(text.height + 2 * PADDING if has_text else PADDING, min(self.pos.y, screen.get_height() - self.height - PADDING))

    def handle_collision(self, others: list):
        collisions = []
        for other, transparency in others:
            if self.rect().colliderect(other.rect(transparency)) and self != other and not (self.hidden or other.hidden):
                collisions.append(other)
        return collisions

    def change_surface(self, texture_name, texture_directory="assets/textures/"):
        if isinstance(texture_name, pygame.Surface):
            self.surface = texture_name
        else:
            self.surface = pygame.transform.scale(pygame.image.load(f"{texture_directory}{texture_name}"), (self.width, self.height))

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()


class Dialogue:
    def __init__(self, font: pygame.font, file_path, size, reading_speed=16, color=(255, 255, 255), pos=pygame.Vector2(0, 0)):

        self.file_path = file_path
        self.font_size = size
        self.font = pygame.font.Font(font, size)
        self.dialogue = read_file_to_list(file_path)
        self.line = 0
        self.text = self.dialogue[self.line]

        self.reading_speed = reading_speed
        self.timing = len(self.text) / self.reading_speed if self.text else 3
        self.time_since_last_line = 0

        self.surface = self.font.render(self.text, False, color)
        self.color = color

        self.pos = pos

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

        self.finished = False

    def update(self, dt, repeating=False):
        self.time_since_last_line += dt
        
        if self.time_since_last_line >= self.timing:
            self.time_since_last_line -= self.timing
            self.line = (self.line + 1) % len(self.dialogue) if repeating else self.line + 1

            if self.line < len(self.dialogue):
                self.text = self.dialogue[self.line]
                self.timing = len(self.text.replace(" ", "")) / self.reading_speed if self.text else 3
            
            else:
                self.text = ""
                self.finished = True

            self.surface = self.font.render(self.text, False, self.color)
            self.width = self.surface.get_width()
            self.height = self.surface.get_height()

    def render(self, surface: pygame.Surface):

        surface.blit(self.surface, self.pos)

class Entity(Sprite):

    entities = {}

    def __init__(self, texture_name, x: int, y: int, width: int, height: int, hp, attack, text: Dialogue, time_to_respawn: float=5.0, id="", invincibility_delay=0.5, alpha=255, aggro_range=0):

        self.max_hp = hp
        self.hp = hp
        self.attack = attack

        self.inventory = []

        self.is_alive = True
        self.time_to_respawn = time_to_respawn
        self.time_remaining = time_to_respawn

        self.murder_count = 0

        self.attacking = False
        self.started_attack = False
        self.aggro_range = aggro_range

        self.invincibility_delay = invincibility_delay
        self.time_since_last_hit = invincibility_delay

        self.text = text
        self.target = None

        self.id = id if id else f"entity_{len(Entity.entities)}"
        self.direction = 0 # 0 = right, 1 = up, 2 = left, 3 = down

        Entity.entities[self.id] = self

        super().__init__(texture_name, x, y, width, height, alpha)
   

    def calculate_percentage(self):
        if self.hp > 0 and self.hp <= self.max_hp:
            return int(self.hp / self.max_hp * 25) - 1
        
        elif self.hp <= 0:
            return 0
        
        else:
            return 24
    
    def update_direction(self):
        if self.vel.y > 0:
            self.direction = "down"
        
        elif self.vel.y < 0:
            self.direction = "up"
            
        if self.vel.x > 0:
            self.direction = "right"
        
        elif self.vel.x < 0:
            self.direction = "left"

    def handle_life(self, dt):
        if self.hp <= 0 and self.is_alive:
            self.is_alive = False
            self.hp = -1
            self.time_remaining = self.time_to_respawn
        
        elif not self.is_alive:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.is_alive = True
                self.hp = self.max_hp

        self.time_since_last_hit += dt

        if self.vel.y > 0:
            self.direction = "down"
        
        elif self.vel.y < 0:
            self.direction = "up"

            

        if self.vel.x > 0:
            self.direction = "right"
        
        elif self.vel.x < 0:
            self.direction = "left"

    def take_damage(self, damage):
        if self.time_since_last_hit >= self.invincibility_delay:
            self.hp -= damage
            self.time_since_last_hit = 0       

    def connect_text(self, padding=10):
        self.text.pos.x = self.pos.x + self.width / 2 - self.text.width / 2
        self.text.pos.y = self.pos.y - self.text.height - padding


class Weapon(Sprite):
    def __init__(self, texture_name, x: int, y: int, width: int, height: int, name: str, attack: int):
        self.name = name
        self.attack = attack

        super().__init__(texture_name, x, y, width, height)

    def calc_damage(self, user: Entity):
        return self.attack + user.attack
    

class Animation:
    def __init__(self, frames: list[pygame.Surface], fps: int, loop=True):
        """
        Initialize the animation.
        :param frames: A list of pygame.Surface objects representing frames.
        :param fps: Frames per second for the animation.
        :param loop: If True, the animation will loop. Otherwise, it will play once.
        """
        self.frames = frames
        self.fps = fps
        self.loop = loop

        self.time_between_frames = 1 / self.fps
        self.current_frame = 0
        self.current_time = 0
        self.finished = False  # Indicates if a non-looping animation has finished

    def update(self, dt: float):
        """
        Updates the animation and returns the current frame
        :param dt: Delta time since the last update
        :return: The current frame (pygame.Surface)
        """
        if self.finished:  # Return the last frame if animation has ended
            return self.frames[-1]

        self.current_time += dt
        if self.current_time >= self.time_between_frames:
            self.current_time -= self.time_between_frames  # Preserve leftover time
            self.current_frame += 1

            # Handle looping or stopping at the end
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

        return self.frames[self.current_frame]

    def reset(self):
        """
        Resets the animation to its first frame and clears the finished flag.
        """
        self.current_frame = 0
        self.current_time = 0
        self.finished = False




def crop_to_content(image, max_x=0, max_y=0):
    """
    Crops an image to its non-transparent content, with a maximum size defined by max_x and max_y.
    :param image: A pygame.Surface with an alpha channel.
    :param max_x: Maximum width for the crop (0 for no limit).
    :param max_y: Maximum height for the crop (0 for no limit).
    :return: A new pygame.Surface cropped to the non-transparent pixels, within max_x and max_y.
    """
    # Get the width and height of the image
    width, height = image.get_size()

    # Extract the alpha channel as a 2D array
    alpha_array = pygame.surfarray.array_alpha(image)

    # Find the bounding box of non-transparent pixels
    rows = alpha_array.any(axis=0)  # Check each row for non-zero alpha
    cols = alpha_array.any(axis=1)  # Check each column for non-zero alpha

    # Get the bounds (top, bottom, left, right)
    if rows.any():  # Ensure there are non-transparent pixels
        top = rows.argmax()
        bottom = height - rows[::-1].argmax()
    else:
        top, bottom = 0, height

    if cols.any():  # Ensure there are non-transparent pixels
        left = cols.argmax()
        right = width - cols[::-1].argmax()
    else:
        left, right = 0, width

    # Calculate the size of the crop
    crop_width = right - left
    crop_height = bottom - top

    # Apply maximum size constraints
    if max_x > 0:
        crop_width = max(crop_width, max_x)
    if max_y > 0:
        crop_height = max(crop_height, max_y)

    # Ensure the right and bottom coordinates are within the new cropped size
    right = left + crop_width
    bottom = top + crop_height

    # Crop the image to the bounding box with max_x and max_y limits
    cropped_image = image.subsurface(pygame.Rect(left, top, right - left, bottom - top)).copy()

    return cropped_image
