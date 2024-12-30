from graphics import Entity
from utils import clamp_velocity


def move_towards(player, enemy):
  
    difference = player.pos - enemy.pos
    speed = 1.5 * enemy.width  # Adjust speed as needed
    output_vel = difference.normalize() * speed
    output_vel.x = round(output_vel.x)
    output_vel.y = round(output_vel.y)
    return output_vel

def run_away(player, enemy):

    # Calculate the direction vector away from the player
    direction = enemy.pos - player.pos
    
    # Normalize the direction vector and scale it to a desired speed
    speed = 1.5 * enemy.width  # Adjust speed as needed
    run_velocity = direction.normalize() * speed

    # Round the velocity for consistency
    run_velocity.x = round(run_velocity.x)
    run_velocity.y = round(run_velocity.y)

    return run_velocity

def make_move(player: Entity, enemy: Entity):
    player_center = player.pos + player.size // 2
    enemy_center = enemy.pos + enemy.size // 2
    distance = ((player_center.x - enemy_center.x) ** 2 + (player_center.y - enemy_center.y) ** 2) ** 0.5
 
    if enemy.hp > player.attack and distance <= enemy.aggro_range and distance * 2 > enemy.aggro_range:
        enemy.vel = move_towards(player, enemy)  # Correct velocity update
        enemy.attacking = True
    
    if enemy.hp > player.attack and distance * 2 <= enemy.aggro_range and enemy.attacking:
        enemy.started_attack = True
    
    elif enemy.hp < player.attack or (distance * 2 < enemy.aggro_range and not enemy.attacking):
        enemy.vel = run_away(player, enemy)
        enemy.started_attack = False
    
    if enemy.started_attack:
        enemy.vel += move_towards(player, enemy)
        enemy.vel = clamp_velocity(enemy.vel, 3 * enemy.width)
    
    if enemy.rect().colliderect(player.rect()):
        difference = player.pos - enemy.pos
        if enemy.vel.dot(difference) > 0:  # Check if moving toward the player
            player.take_damage(enemy.attack)
            enemy.started_attack = False
            enemy.vel = 2 * run_away(player, enemy)
            enemy.attacking = False
