import pygame

from random import randint

from utils import *
from graphics import *
print(Sprite)  # Should return <class 'graphics.Sprite'>
print(CombatManager)  # Should return <class 'graphics.CombatManager'>

pygame.init()
#screen = pygame.display.set_mode((1280, 720))
screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h), pygame.FULLSCREEN)
pygame.display.set_caption("exercises")
clock = pygame.time.Clock()

SCREEN_COLOR = "cyan"
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
player = CombatManager("player_male.png", screen.get_width() / 2, screen.get_height() / 2, 32 * player_scale, 64 * player_scale, 100, 10)
skeleton = CombatManager("skeleton.png", 3 *screen.get_width() / 4, screen.get_height() / 4, 32 * player_scale, 64 * player_scale, 50, 10)

sword = Weapon("rusty_sword_v2.png", 0, 0, 32 * player_scale, 32 * player_scale, "Rusty Sword", 10)
ui = Sprite("ui.png", 0, 0 , screen.get_width() / 2, screen.get_width() / 32 * 9)

UI_WIDTH, UI_HEIGHT = 256, 144
player_size = (64, 64)

swing_sword = extract_sprites(pygame.image.load(f"{texture_directory}sword_swing.png").convert_alpha(), 3, 2)
swing_sword = rescale(swing_sword, 64 * player_scale, 64 * player_scale)

ui_scale_x = ui.width / UI_WIDTH
ui_scale_y = ui.height / UI_HEIGHT

# Health bar scaling
health_bar_original_width, health_bar_original_height = 58, 6
scaled_health_bar_width = int(health_bar_original_width * ui_scale_x)
scaled_health_bar_height = int(health_bar_original_height * ui_scale_y)

hp_stage = 24
health_bar_sheet = pygame.image.load(f"{texture_directory}health_bar.png").convert_alpha()
health_bars = extract_sprites(health_bar_sheet, 25, 1)
bars = []
for bar in health_bars:
    bars.append(crop_to_content(bar))

health_bars = bars
health_bars = health_bars[::-1]
health_bar = Sprite(
    pygame.transform.scale(health_bars[hp_stage], (scaled_health_bar_width, scaled_health_bar_height)),
    0, 0, scaled_health_bar_width, scaled_health_bar_height
)
health_bar.pos.x = int(22 * ui_scale_x)
health_bar.pos.y = int(4 * ui_scale_y)


# Fonts
text_size = 36
font = pygame.font.Font(None, text_size)

# Offsets
sword_offset = pygame.Vector2(24 * player.width / 32, player.height - 22 * player.height / 64 - sword.height)


dt = 0  # Delta time
screen.fill((255, 255, 255))


# Load dialogue
dialogue = read_file_to_list(f"{script_directory}script.txt")
current_line = 0
elapsed_time = 0
time_to_change = 3
debounce = 1
time_to_frame = 0

running = True
while running:

    handle_events()

    true_player_vel = (player.vel.x ** 2 + player.vel.y ** 2) ** 0.5

    # Read the next line
    text_line = dialogue[current_line]
    formatted_text = text_line.format(x=player.vel.x, y=player.vel.y)
    text = font.render(formatted_text, False, (0, 0, 0))
    text = Sprite(font.render(formatted_text, False, (0, 0, 0)), 0, 0, text.get_width(), text.get_height())

    health_bar = Sprite(
    pygame.transform.scale(health_bars[hp_stage], (scaled_health_bar_width, scaled_health_bar_height)),
    health_bar.pos.x, health_bar.pos.y, scaled_health_bar_width, scaled_health_bar_height
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

    if keys[pygame.K_LSHIFT]:
        speed = 3 * player.width


    if keys[pygame.K_w]:
        player.vel.y -= speed
    if keys[pygame.K_s]:
        player.vel.y += speed
    if keys[pygame.K_a]:
        player.vel.x -= speed
    if keys[pygame.K_d]:
        player.vel.x += speed

    # Update position and keep it within bounds
    for entity in [player, skeleton]:
        entity.pos += entity.vel * dt
        entity.cap(screen, entity == player, PADDING, text if entity == player else None)
    

    if player.rect().colliderect(ui.rect(True)):
        # Get the player's and UI's rectangles
        player_rect = player.rect()
        ui_rect = ui.rect(True)
        
        # Calculate the overlap distances on each side
        overlap_left = player_rect.right - ui_rect.left
        overlap_right = ui_rect.right - player_rect.left
        overlap_top = player_rect.bottom - ui_rect.top
        overlap_bottom = ui_rect.bottom - player_rect.top

        # Determine the minimum overlap direction
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        # Move the player back based on the direction of the smallest overlap
        if min_overlap == overlap_left:
            player.pos.x -= overlap_left  # Move left
        elif min_overlap == overlap_right:
            player.pos.x += overlap_right  # Move right
        elif min_overlap == overlap_top:
            player.pos.y -= overlap_top  # Move up
        elif min_overlap == overlap_bottom:
            player.pos.y += overlap_bottom  # Move down

        if player.vel.length() > 0:
            player.vel = player.vel.normalize()
            player.pos -= player.vel * min_overlap

    if pygame.mouse.get_pressed()[0] and not player.attacking:
        frame = 0
        player.attacking = True
        player = CombatManager(swing_sword[frame], player.pos.x, player.pos.y, 64 * player_scale, 64 * player_scale, player.hp, player.attack)
        time_to_frame = 1 / 6

    if player.attacking and time_to_frame <= 0:
        frame += 1
        if frame >= len(swing_sword):
            player.attacking = False
            frame = 0
        player = CombatManager(swing_sword[frame], player.pos.x, player.pos.y, 64 * player_scale, 64 * player_scale, player.hp, player.attack)
        time_to_frame = 1 / 6

    time_to_frame -= dt


    sword.pos = player.pos + sword_offset
    text.pos = pygame.Vector2(player.pos.x + player.width / 2 - text.width / 2, player.pos.y - text.height - PADDING)
    text.cap(screen, False)
    sword.cap(screen, PADDING=PADDING)

    if skeleton.rect().collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0] and debounce >= 0.2:
        debounce = 0
        print("Skeleton clicked")

    if sword.rect().colliderect(skeleton.rect()) and keys[pygame.K_SPACE] and debounce >= 0.5:
        debounce = 0
        skeleton.hp -= player.attack
        skeleton.calc_kb(dt, player, scale=4)
        player.calc_kb(dt, scale=2, direction="left")



    # Clear the screen and draw
    screen.fill(SCREEN_COLOR)


    player.render(screen)
    sword.render(screen)
    text.render(screen)
    ui.render(screen)

    skeleton.render(screen)
    health_bar.render(screen)
   
    pygame.display.flip()

    # Update delta time
    dt = clock.tick(60) / 1000  # Convert to seconds

    elapsed_time += dt
    debounce += dt


    if elapsed_time >= time_to_change:
        current_line = (current_line + 1) % len(dialogue)
        elapsed_time = 0


    if player.is_alive:
        hp_stage = player.calculate_percentage()

    else:
        player.time_remaining -= dt

        if player.time_remaining <= 0:
            player.hp = player.max_hp
            player.is_alive = True
    
    if skeleton.is_alive:
        skeleton_hp_stage = skeleton.calculate_percentage()

    else:
        skeleton.time_remaining -= dt

        if skeleton.time_remaining <= 0:
            skeleton.hp = skeleton.max_hp
            skeleton.is_alive = True
            skeleton.pos = pygame.Vector2(screen.get_width() / 2 - skeleton.width / 2, screen.get_height() / 2 - skeleton.height / 2)
            player.murder_count += 1
        
    
pygame.quit()
   