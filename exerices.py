import pygame

from random import randint
from time import time_ns

from utils import path_correction, extract_sprites, rescale, flip
from graphics import Sprite, Animation, Dialogue, Entity, crop_to_content
from loader import load_json, json
from ai import make_move

to_prefix = "_internal\\"
pygame.init()
hw_screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

pygame.display.set_caption("exercises")
clock = pygame.time.Clock()

screen = pygame.surface.Surface((640, 360))

SCREEN_COLOR = (0, 0, 0)
PADDING = 10
HEALTH_BAR_WIDTH = 58
HEALTH_BAR_HEIGHT = 7
BAR_COUNT = 25

# Define the directories
def texture_directory():
   return path_correction("Assets\\Textures\\")
    
def script_directory():
    return path_correction("Assets\\Scripts\\")
    
def font_dir():
    return path_correction("Assets\\Fonts\\")
    
# Game states
running = True
current_level = ""
reading_speed = 16

def load_game(directory):
    global player, skeleton, aetherion, current_level

    data = load_json(path_correction(directory))

    for key, value in data.items():
        if key == "level":
            current_level = value

        elif key in Entity.entities.keys():
            current_entity = Entity.entities[key]
            current_entity.hp = value["hp"] if value["hp"] != "keep" else current_entity.hp
            current_entity.pos.x = value["x"] * screen.get_width()
            current_entity.pos.y = value["y"] * screen.get_height()

    load_background()
    

def save_game(directory):
    # Create a dictionary to store the game state
    game_state = {
        "level": current_level,
    }

    # Save entities' states
    for name, entity in Entity.entities.items():
        game_state[name] = {
            "hp": entity.hp,
            "x": entity.pos.x / screen.get_width(),
            "y": entity.pos.y / screen.get_height()
        }

    # Write the dictionary to a JSON file
    with open(path_correction(directory), "w", encoding="utf-8") as file:
        json.dump(game_state, file, ensure_ascii=False, indent=4)

def load_settings(directory):
    data = load_json(path_correction(directory))

    global reading_speed, hw_screen, refresh_rate

    res_x = 1280
    res_y = 720
    fullscreen = False
    refresh_rate = 60

    for key, value in data.items():
        if key == "reading_speed":
            reading_speed = value
        
        elif key == "fullscreen":
            if value:
                fullscreen = True
        
        elif key == "resolution":
            res_x, res_y = value["width"], value["height"]
        
        elif key == "fps":
            refresh_rate = value

    if fullscreen:
        hw_screen = pygame.display.set_mode((res_x, res_y), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
    else:
        hw_screen = pygame.display.set_mode((res_x, res_y))
            
def change_player_direction():
    global player, player_forward, player_backward, player_left, player_right
    if player.direction == "left":
        player.change_surface(player_left)
    elif player.direction == "right":
        player.change_surface(player_right)
    elif player.direction == "up":
        player.change_surface(player_backward)
    elif player.direction == "down":
        player.change_surface(player_forward)

def handle_events():
    global running, player

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

def load_background():
    global current_level, texture_directory, screen, background

    background = pygame.transform.scale(pygame.image.load(f"{texture_directory()}{current_level}.png").convert_alpha(), screen.get_size())

start_time = time_ns()

# Load sprites
player_scale = round(screen.get_width() / 640, 2)

player = Entity("player_male_fwd.png", screen.get_width() / 2, screen.get_height() / 2, 22 * player_scale, 64 * player_scale, 100, 10, None, float("inf"), "player", 1)

skeleton = Entity("skeleton.png", 3 * screen.get_width() * 0.03, screen.get_height() * 0.15, 32 * player_scale, 64 * player_scale, 50, 10, None, float("inf"), "skeleton")

zombie = Entity("zombie.png", 3 * screen.get_width() * 0.03, screen.get_height() * 0.15, 32 * player_scale, 64 * player_scale, 75, 15, None, float("inf"), "zombie")

aetherion = Entity("aetherion.png", screen.get_width() * 0.45, screen.get_height() * 0.32222222222222224, 32 * player_scale, 64 * player_scale, 100, 10, None, 0, "aetherion")

merchant = Entity("fem_merchant_sitting.png", 0, 0, 64 * player_scale, 64 * player_scale, 100, 0, None, float("inf"), "merchant")

player_forward = pygame.transform.scale(pygame.image.load(f"{texture_directory()}player_male_fwd.png"), (22 * player_scale, 64 * player_scale))
player_backward = pygame.transform.scale(pygame.image.load(f"{texture_directory()}player_male_bwd.png"), (22 * player_scale, 64 * player_scale))
player_left = pygame.transform.scale(pygame.transform.flip(pygame.image.load(f"{texture_directory()}player_male_sideways.png"), True, False), (15 * player_scale, 64 * player_scale))
player_right = pygame.transform.scale(pygame.image.load(f"{texture_directory()}player_male_sideways.png"), (15 * player_scale, 64 * player_scale))

ui = Sprite("ui.png", 0, 0 , screen.get_width() / 2, screen.get_width() / 32 * 9)


UI_WIDTH, UI_HEIGHT = 256, 144
player_size = (64, 64)

# Loading animations

swing_sword = extract_sprites(pygame.image.load(f"{texture_directory()}sword_swing.png").convert_alpha(), 3, 2)
swing_sword = rescale(swing_sword, 64 * player_scale, 64 * player_scale)

draw_sword = extract_sprites(pygame.image.load(f"{texture_directory()}sword_out.png").convert_alpha(), 3, 2)
draw_sword = rescale(draw_sword, 64 * player_scale, 64 * player_scale)

sheathe_sword = extract_sprites(pygame.image.load(f"{texture_directory()}sword_in.png").convert_alpha(), 3, 2)
sheathe_sword = rescale(sheathe_sword, 64 * player_scale, 64 * player_scale)

player_walk_fwd = extract_sprites(pygame.image.load(f"{texture_directory()}player_walk_fwd.png").convert_alpha(), 2, 3)
player_walk_fwd = rescale(player_walk_fwd, 22 * player_scale, 64 * player_scale)

player_walk_bwd = extract_sprites(pygame.image.load(f"{texture_directory()}player_walk_bwd.png").convert_alpha(), 2, 3)
player_walk_bwd = rescale(player_walk_bwd, 22 * player_scale, 64 * player_scale)

player_walk_sideways = extract_sprites(pygame.image.load(f"{texture_directory()}player_walk_sideways.png").convert_alpha(), 1, 2)
player_walk_sideways = rescale(player_walk_sideways, 15 * player_scale, 64 * player_scale)

sword_swing = Animation(swing_sword, 6)
sword_draw = Animation(draw_sword, 6, False)
sword_sheathe = Animation(sheathe_sword, 6, False)

player_walk_forward = Animation(player_walk_fwd, 4)
player_walk_backward = Animation(player_walk_bwd, 4)
player_walk_left = Animation(flip(player_walk_sideways, True, False), 4)
player_walk_right = Animation(player_walk_sideways, 4)



# UI scaling
ui_scale_x = ui.width / UI_WIDTH
ui_scale_y = ui.height / UI_HEIGHT

# Health bar scaling
health_bar_original_width, health_bar_original_height = 58, 6
hp_bar_outline_width, hp_bar_outline_height = 64, 21

scaled_hp_outline_width, scaled_hp_outline_height = int(hp_bar_outline_width * ui_scale_x), int(hp_bar_outline_height * ui_scale_y)
scaled_health_bar_width = int(health_bar_original_width * ui_scale_x)
scaled_health_bar_height = int(health_bar_original_height * ui_scale_y)

hp_stage = 24
health_bar_sheet = pygame.image.load(f"{texture_directory()}health_bar.png").convert_alpha()
health_bars = extract_sprites(health_bar_sheet, 25, 1)
bars = []
for bar in health_bars:
    bars.append(crop_to_content(bar, 58))

health_bars = bars
health_bars = health_bars[::-1]


player_health_bar = Sprite(
    pygame.transform.scale(health_bars[hp_stage], (scaled_health_bar_width, scaled_health_bar_height)),
    0, 0, scaled_health_bar_width, scaled_health_bar_height
)
player_health_bar.pos.x = int(22 * ui_scale_x)
player_health_bar.pos.y = int(4 * ui_scale_y)

skeleton_health_bar = Sprite(
    pygame.transform.scale(health_bars[hp_stage], (scaled_health_bar_width, scaled_health_bar_height)),
    0, 0, scaled_health_bar_width, scaled_health_bar_height
)

print(f"Time to load sprites: {time_ns() - start_time}ns ({round((time_ns() - start_time) / 1000000, 2)}ms)")

# Fonts
text_size = 12
comic_neue = f"{font_dir()}comic_neue.ttf"
font = pygame.font.Font(comic_neue, text_size)


dt = 0  # Delta time
screen.fill((255, 255, 255))


# Load dialogue
aetherion.text = Dialogue(comic_neue, f"{script_directory()}c1a1_1.txt", text_size)
player.text = Dialogue(comic_neue, f"{script_directory()}player_script.txt", text_size)


# Timers
elapsed_time = 0
time_to_change = 3
debounce = 1
time_to_frame = 0
time_since_attack = 0
frame = 0

time_counter = 0

# Default entities
entities = [player, skeleton, aetherion]
has_text = [player, aetherion]

# weird and random vars
sword_sheathed = True
sheathing = False

first_sprite_change = False
background_alpha = 0
aetherion_alpha = 255

max_background_alpha = 200

running = True


#load_game("savegame.json") # Uncomment this line to load the game state from the save file
load_settings("settings.json")
load_game("LevelData/c1a1_1.json")
load_background()

while running:

    start_time = time_ns()

    handle_events()

    player_health_bar = Sprite(
    pygame.transform.scale(health_bars[player.calculate_percentage()], (scaled_health_bar_width, scaled_health_bar_height)),
    player_health_bar.pos.x, player_health_bar.pos.y, scaled_health_bar_width, scaled_health_bar_height
    )

    skeleton_health_bar = Sprite(
    pygame.transform.scale(health_bars[skeleton.calculate_percentage()], (scaled_health_bar_width, scaled_health_bar_height)),
    skeleton_health_bar.pos.x, skeleton_health_bar.pos.y, scaled_health_bar_width, scaled_health_bar_height
    )

    # Deceleration
    player.vel.x = round(player.vel.x / 2, 0)
    player.vel.y = round(player.vel.y / 2, 0)

    skeleton.vel.x = round(skeleton.vel.x / 2, 0)
    skeleton.vel.y = round(skeleton.vel.y / 2, 0)

    speed_multiplier = 1

    # Handle input

    mouse_pos = pygame.mouse.get_pos()

    keys = pygame.key.get_pressed()

    speed = 1.5 * player.width
    
    if not sword_sheathed:
        speed = 0

    if background_alpha < max_background_alpha:
        speed = 0

    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player.vel.y -= speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player.vel.y += speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.vel.x -= speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.vel.x += speed

    # Update position and keep it within bounds
    for entity in entities:
        entity.pos += entity.vel * dt
        entity.cap(screen, entity == player, PADDING, entity.text if entity in has_text else None)
    

    if player.rect().colliderect(ui.rect(True)):
        overlap = player.rect().clip(ui.rect(True))
        player.pos.x += overlap.width
        player.pos.y += overlap.height

    # Handle sheathing animation
    if sheathing and not sword_sheathed:
        player.change_surface(sword_sheathe.update(dt))
        if sword_sheathe.finished:
            sheathing = False
            sword_sheathed = True
            sword_sheathe.reset()
            change_player_direction()

    # Start sheathing when space is released
    if not keys[pygame.K_SPACE] and not sword_sheathed and not sheathing:
        player.attacking = False
        player.started_attack = False
        sheathing = True
        sword_sheathe.reset()  # Ensure it starts from the first frame

    # Handle sword swinging
    if keys[pygame.K_SPACE] and player.attacking:
        player.change_surface(sword_swing.update(dt))

    # Handle sword drawing animation
    if keys[pygame.K_SPACE] and player.started_attack and not player.attacking:
        player.change_surface(sword_draw.update(dt))
        if sword_draw.finished:
            player.attacking = True
            sword_draw.reset()

    # Start drawing when space is pressed and sword is sheathed
    if keys[pygame.K_SPACE] and not player.started_attack and sword_sheathed:
        player.started_attack = True
        sword_sheathed = False
        sword_draw.reset()

    if keys[pygame.K_SPACE] and not aetherion.text.finished and debounce >= 0.2:
        aetherion.text.update(aetherion.text.timing)
        debounce = 0

    player.update_direction()
    if sword_sheathed:
        if player.direction == "left":
            player.change_surface(player_walk_left.update(dt))
            if player.vel.x == 0:
                player.change_surface(player_left)
        
        elif player.direction == "right":
            player.change_surface(player_walk_right.update(dt))
            if player.vel.x == 0:
                player.change_surface(player_right)

        elif player.direction == "up":
            player.change_surface(player_walk_backward.update(dt))  
            if player.vel.y == 0:
                player.change_surface(player_backward)
              
        elif player.direction == "down":
            player.change_surface(player_walk_forward.update(dt))
            if player.vel.y == 0:
                player.change_surface(player_forward)
        


    skeleton_health_bar.pos = pygame.Vector2(skeleton.pos.x + skeleton.width / 2 - skeleton_health_bar.width / 2, skeleton.pos.y + skeleton.height + PADDING)
    player.connect_text()
    aetherion.connect_text()

    if player.rect(True).colliderect(skeleton.rect()) and player.attacking and sword_swing.current_frame == 2:
        debounce = 0
        skeleton.take_damage(player.attack + randint(-5, 5))

    if player.rect().colliderect(merchant.rect()):
        player.take_damage(-10)

               

    # Clear the screen and draw
    screen.fill(SCREEN_COLOR)
    
    if aetherion.text.finished:
        background_alpha += 127.5 * dt
        background_alpha = min(background_alpha, max_background_alpha)
        background.set_alpha(background_alpha)

        aetherion_alpha -= 255 * (200 / 127.5) * dt
        aetherion_alpha = max(aetherion_alpha, 0)
        aetherion.alpha = aetherion_alpha

        screen.blit(background, (0, 0))
        SCREEN_COLOR = (0, SCREEN_COLOR[1] + 10 * dt, 0)
        if SCREEN_COLOR[1] > 10:
            SCREEN_COLOR = (0, 10, 0)

    if aetherion.text.finished and not first_sprite_change:
        first_sprite_change = True
        aetherion.change_surface(pygame.transform.scale(pygame.image.load(f"{texture_directory()}aetherion.png").convert_alpha(), (32 * player_scale, 64 * player_scale)))


    player.text.render(screen)
    aetherion.text.render(screen)
    

    if background_alpha == max_background_alpha:
        merchant.render(screen)
        skeleton_health_bar.render(screen)
        skeleton.render(screen)
        player.render(screen)
        ui.render(screen)
        player_health_bar.render(screen)
        

    else:
        aetherion.change_surface(pygame.transform.scale(pygame.image.load(f"{texture_directory()}aetherion.png").convert_alpha(), (64 * player_scale, 128 * player_scale)))
        aetherion.render(screen)


    hw_screen.blit(pygame.transform.scale(screen, hw_screen.get_size()), (0, 0))
    pygame.display.flip()

    # Update delta time
    dt = clock.tick(refresh_rate) / 1000  # Convert to seconds

    elapsed_time += dt
    debounce += dt
    time_counter += dt

    # Handle updates
    skeleton.handle_life(dt)
    player.handle_life(dt)
    player.text.update(dt)
    aetherion.text.update(dt)
    make_move(player, skeleton)

    if skeleton.is_alive and player.pos.x == 10:
        player.pos.x = 11

    if (not skeleton.is_alive) and player.pos.x == 10 and current_level == "c1a1_1":
        load_game("LevelData/c1a1_2.json")
        load_background()
        skeleton.aggro_range = 0.2 * screen.get_width()
        skeleton.is_alive = True

    elif (not skeleton.is_alive) and player.pos.x == 0.95 * screen.get_width() and current_level == "c1a1_2":
        player.pos.x = 11
        current_level = "c1a1_1"
        merchant.hp = -1
        load_background()
        skeleton.aggro_range = 0

    elif player.pos.y < 0.095 * screen.get_height() and current_level == "c1a1_2" and (not skeleton.is_alive) and player.hp > player.max_hp * 0.8:
        load_game("LevelData/c1a2_1.json")
        load_background()
        player.pos.y = 0.78 * screen.get_height()

    elif player.pos.y >= 0.7944444444444444 * screen.get_height() and current_level == "c1a2_1":
        current_level = "c1a1_2"
        load_background()
        player.pos.y = 0.1 * screen.get_height()

    #print(f"Time per frame: {time_ns() - start_time}ns ({round((time_ns() - start_time) / 1000000, 2)}ms)")
save_game("savegame.json")
pygame.quit()
   