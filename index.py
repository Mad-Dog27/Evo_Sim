import pygame
import random
import math

pygame.init()
food_variable = random.uniform(0, 1)
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Manual Control Mode")

food_pos = [width * food_variable, height * food_variable]
food_size = 10

print(f"Spawned enemy with {food_pos} HP") 
# Creature stats
creature_pos = [width // 2, height // 2]
creature_size = 40
speed = 5  # How many pixels it moves per frame
food_speed = 7

running = True
while running:
    # 1. Check for Events (Input)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Continuous Key Press Check
    # This checks if a key is held down (smoother than tapping)
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
        food_pos[0] -= food_speed
    if keys[pygame.K_RIGHT]:
        food_pos[0] += food_speed
    if keys[pygame.K_UP]:
        food_pos[1] -= food_speed
    if keys[pygame.K_DOWN]:
        food_pos[1] += food_speed

    x_dif = (food_pos[0] + (food_size //2)) - (creature_pos[0] + (creature_size//2))
    y_dif = (food_pos[1] + (food_size //2)) - (creature_pos[1] + (creature_size//2))

    ratio = x_dif // y_dif
    chase_angle = math.atan2(y_dif, x_dif)
    x_speed = speed*math.cos(chase_angle)
    y_speed = speed*math.sin(chase_angle)

    creature_pos[0] += x_speed
    creature_pos[1] += y_speed
    # 3. Render
    screen.fill((30, 30, 30))
    
    # Draw the creature
    pygame.draw.rect(screen, (0, 200, 255), (creature_pos[0], creature_pos[1], creature_size, creature_size))

    pygame.draw.rect(screen, (0, 200, 255), (food_pos[0], food_pos[1], food_size, food_size))

    pygame.display.flip()
    
    # 4. Limit the speed (Important!)
    # Without this, it will move way too fast to see
    pygame.time.Clock().tick(60)

pygame.quit()
