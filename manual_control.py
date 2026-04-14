import pygame

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Manual Control Mode")

# Creature stats
creature_pos = [width // 2, height // 2]
creature_size = 40
speed = 5  # How many pixels it moves per frame

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
        creature_pos[0] -= speed
    if keys[pygame.K_RIGHT]:
        creature_pos[0] += speed
    if keys[pygame.K_UP]:
        creature_pos[1] -= speed
    if keys[pygame.K_DOWN]:
        creature_pos[1] += speed

    # 3. Render
    screen.fill((30, 30, 30))
    
    # Draw the creature    
    pygame.draw.rect(screen, (0, 200, 255), (creature_pos[0], creature_pos[1], creature_size, creature_size))

    pygame.display.flip()
    
    # 4. Limit the speed (Important!)
    # Without this, it will move way too fast to see
    pygame.time.Clock().tick(60)

pygame.quit()
