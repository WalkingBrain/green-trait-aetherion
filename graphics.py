import pygame



class Sprite:
    def __init__(self, texture_name, x: int, y: int, width: int, height: int,texture_directory="assets/textures/"):
        if isinstance(texture_name, pygame.Surface):
            self.surface = texture_name
        else:
            self.surface = pygame.transform.scale(pygame.image.load(f"{texture_directory}{texture_name}"), (width, height))

        self.texture_name = texture_name

        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)

        self.width = width
        self.height = height

    def render(self, surface: pygame.Surface):
        if hasattr(self, "hp"):
            if self.hp <= 0:
                return None
            
        surface.blit(self.surface, self.pos)

    def rect(self, transparent: bool=False):
        if hasattr(self, "hp"):
            if self.hp <= 0:
                return pygame.Rect(0, 0, 0, 0)
        if not transparent:
            return pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        
        else:
            no_transparency = crop_to_content(self.surface)
            return pygame.Rect(self.pos.x, self.pos.y, no_transparency.get_width(), no_transparency.get_height())

    def cap(self, screen, has_text=False, PADDING=10, text=None):
        if text is None:
            has_text = False

        self.pos.x = max(PADDING, min(self.pos.x, screen.get_width() - self.width))
        self.pos.y = max(text.height + 2 * PADDING if has_text else PADDING, min(self.pos.y, screen.get_height() - self.height - PADDING))

    def handle_collision(self, others: list):

        collisions = [other for other, transparency in others if self.rect().colliderect(other.rect(transparency)) and self != other]
        return collisions



class CombatManager(Sprite):
    def __init__(self, texture_name, x: int, y: int, width: int, height: int, hp, attack, time_to_respawn=5):
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.inventory = []

        self.is_alive = True
        self.time_to_respawn = time_to_respawn
        self.time_remaining = 0
        self.murder_count = 0
        self.attacking = False

        super().__init__(texture_name, x, y, width, height)

    def calculate_percentage(self):
        if self.hp > 0:
            return int(self.hp / self.max_hp * 25) - 1
        
        else:
            self.is_alive = False
            self.time_remaining = self.time_to_respawn
            return 0
    
    def calc_kb(self, dt, attacker=None, scale=2, direction=None):
        if not direction and attacker:
            if attacker.pos.x > self.pos.x:
                direction = "left"
            elif attacker.pos.x < self.pos.x:
                direction = "right"

            else:
                direction = "right"

        
        match direction:
            case "left":
                self.vel.x -= scale * self.width / (dt)
            case "right":
                self.vel.x += scale * self.width / dt

        
class Weapon(Sprite):
    def __init__(self, texture_name, x: int, y: int, width: int, height: int, name: str, attack: int):
        self.name = name
        self.attack = attack

        super().__init__(texture_name, x, y, width, height)

    def calc_damage(self, user: CombatManager):
        return self.attack + user.attack
    

def crop_to_content(image):
    """
    Crops an image to its non-transparent content.
    :param image: A pygame.Surface with an alpha channel.
    :return: A new pygame.Surface cropped to the non-transparent pixels.
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

    # Crop the image to the bounding box
    cropped_image = image.subsurface(pygame.Rect(left, top, right - left, bottom - top)).copy()

    return cropped_image
