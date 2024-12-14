import pygame

from random import randint

from utils import *
from graphics import *


pygame.init()
screen = pygame.display.set_mode((1280, 720))
#screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), pygame.FULLSCREEN)
pygame.display.set_caption("exercises")
clock = pygame.time.Clock()

SCREEN_COLOR = (0, 0, 0)
PADDING = 10
HEALTH_BAR_WIDTH = 58
HEALTH_BAR_HEIGHT = 7
BAR_COUNT = 25

# Define the directories
texture_directory = resource_path("Assets/Textures/")
script_directory = resource_path("Assets/Scripts/")


def handle_events():
    global running, player

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


# Load sprites
player_scale = round(screen.get_width() / 640, 2)
player = Entity("player_male.png", screen.get_width() / 2, screen.get_height() / 2, 32 * player_scale, 64 * player_scale, 100, 10, None, float("inf"))

skeleton = Entity("skeleton.png", 3 * screen.get_width() * 0.03, screen.get_height() * 0.15, 32 * player_scale, 64 * player_scale, 50, 10, None, float("inf"))

aetherion = Entity("aetherion.png", screen.get_width() * 0.45, screen.get_height() * 0.32222222222222224, 32 * player_scale, 64 * player_scale, 100, 10, None)

default_player = pygame.transform.scale(pygame.image.load(f"{texture_directory}player_male.png"), (32 * player_scale, 64 * player_scale))
ui = Sprite("ui.png", 0, 0 , screen.get_width() / 2, screen.get_width() / 32 * 9)

background = pygame.transform.scale(pygame.image.load(f"{texture_directory}c1a1_1.png").convert_alpha(), (screen.get_width(), screen.get_height()))
UI_WIDTH, UI_HEIGHT = 256, 144
player_size = (64, 64)

# Loading animations

swing_sword = extract_sprites(pygame.image.load(f"{texture_directory}sword_swing.png").convert_alpha(), 3, 2)
swing_sword = rescale(swing_sword, 64 * player_scale, 64 * player_scale)

draw_sword = extract_sprites(pygame.image.load(f"{texture_directory}sword_out.png").convert_alpha(), 3, 2)
draw_sword = rescale(draw_sword, 64 * player_scale, 64 * player_scale)

sheathe_sword = extract_sprites(pygame.image.load(f"{texture_directory}sword_in.png").convert_alpha(), 3, 2)
sheathe_sword = rescale(sheathe_sword, 64 * player_scale, 64 * player_scale)

sword_swing = Animation(swing_sword, 6)
sword_draw = Animation(draw_sword, 6, False)
sword_sheathe = Animation(sheathe_sword, 6, False)


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
health_bar_sheet = pygame.image.load(f"{texture_directory}health_bar.png").convert_alpha()
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


# Fonts
text_size = 50
font = pygame.font.Font(None, text_size)



dt = 0  # Delta time
screen.fill((255, 255, 255))


# Load dialogue
aetherion.text = Dialogue(None, f"{script_directory}aetherion_script.txt", 50)
player.text = Dialogue(None, f"{script_directory}player_script.txt", 50)


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
while running:

    handle_events()



    player_health_bar = Sprite(
    pygame.transform.scale(health_bars[hp_stage], (scaled_health_bar_width, scaled_health_bar_height)),
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
        player.pos.x = screen.get_width() * 0.63
        player.pos.y = screen.get_height() * 0.33

        aetherion.pos.x = screen.get_width() / 2 - aetherion.width / 2
        aetherion.pos.y = screen.get_height() / 2 - aetherion.height / 2

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
        # Get the player's and UI's rectangles
        player_rect = player.rect()
        ui_rect = ui.rect(True)

        # Check if player collides with UI on the x-axis (horizontal overlap)
        if player.pos.x <= ui.pos.x + ui.width:
            player.pos.x -= player.vel.x * dt

        # Check if player collides with UI on the y-axis (vertical overlap)
        if player.pos.y + 2 * PADDING <= ui.pos.y + ui.height:
            player.pos.y -= player.vel.y * dt


    # Handle sheathing animation
    if sheathing and not sword_sheathed:
        prev_frame = sword_sheathe.current_frame
        player.change_surface(sword_sheathe.update(dt))
        if sword_sheathe.finished:
            sheathing = False
            sword_sheathed = True
            sword_sheathe.reset()
            player.change_surface(default_player)

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


    skeleton_health_bar.pos = pygame.Vector2(skeleton.pos.x + skeleton.width / 2 - skeleton_health_bar.width / 2, skeleton.pos.y + skeleton.height + PADDING)
    player.connect_text()
    aetherion.connect_text()


    if skeleton.rect().collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0] and debounce >= 0.2:
        debounce = 0
        print("Skeleton clicked")

    if player.rect(True).colliderect(skeleton.rect()) and player.attacking and sword_swing.current_frame == 2:
        debounce = 0
        skeleton.take_damage(player.attack + randint(-5, 5))
        pygame.time.delay(int(round(dt * 1000, 0)))
               

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
        aetherion.change_surface(pygame.transform.scale(pygame.image.load("Assets/Textures/aetherion.png").convert_alpha(), (32 * player_scale, 64 * player_scale)))


    player.text.render(screen)
    aetherion.text.render(screen)
    

    if background_alpha == max_background_alpha:
        skeleton_health_bar.render(screen)
        skeleton.render(screen)
        player.render(screen)
        ui.render(screen)
        player_health_bar.render(screen)

    else:
        aetherion.change_surface(pygame.transform.scale(pygame.image.load("Assets/Textures/aetherion.png").convert_alpha(), (64 * player_scale, 128 * player_scale)))
        aetherion.render(screen)

    pygame.display.flip()

    # Update delta time
    dt = clock.tick(60) / 1000  # Convert to seconds

    elapsed_time += dt
    debounce += dt
    time_counter += dt




    skeleton.handle_life(dt)
    player.handle_life(dt)
    player.text.update(dt)
    aetherion.text.update(dt)

    print(f"Aetherion position: {aetherion.pos.x / screen.get_width()}, {aetherion.pos.y / screen.get_height()}")
    
pygame.quit()
   