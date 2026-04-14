import pygame
import random
import math

pygame.init()
my_food_variable = random.uniform(0, 1)
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

food_amnt = random.randint(3, 7)
food_variables = []
food_list = []

pygame.display.set_caption("Manual Control Mode")

# --- THE CLASS ---
class Creature:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

for i in range(food_amnt):
    food_variable_x = random.uniform(0, 1)
    food_variable_y = random.uniform(0, 1)

    new_food = Creature(width * food_variable_x, height * food_variable_y, 10, 7)
    food_list.append(new_food)
# Create the instance
my_creature = Creature(width // 2, height // 2, 40, 5)

food_creature = Creature(width * my_food_variable, height * my_food_variable, 10, 7)
food_pos = [food_creature.x, food_creature.y]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  food_creature.x -= food_creature.speed
    if keys[pygame.K_RIGHT]: food_creature.x += food_creature.speed
    if keys[pygame.K_UP]:    food_creature.y -= food_creature.speed
    if keys[pygame.K_DOWN]:  food_creature.y += food_creature.speed

    # Adjusting logic to use my_creature.x and my_creature.y
    x_dif = (food_creature.x + (food_creature.size // 2)) - (my_creature.x + (my_creature.size // 2))
    y_dif = (food_creature.y + (food_creature.size // 2)) - (my_creature.y + (my_creature.size // 2))

    chase_angle = math.atan2(y_dif, x_dif)
    my_creature.x += my_creature.speed * math.cos(chase_angle)
    my_creature.y += my_creature.speed * math.sin(chase_angle)

    # Boundaries
    if my_creature.x < 0: my_creature.x = 0
    if my_creature.y < 0: my_creature.y = 0
    if (my_creature.x + my_creature.size) > width: my_creature.x = width - my_creature.size
    if (my_creature.y + my_creature.size) > height: my_creature.y = height - my_creature.size

    screen.fill((30, 30, 30))
    
    # Render using class attributes
    pygame.draw.rect(screen, (0, 200, 255), (my_creature.x, my_creature.y, my_creature.size, my_creature.size))
    pygame.draw.rect(screen, (255, 200, 0), (food_creature.x, food_creature.y, food_creature.size, food_creature.size))
    
        # 1. Find the center of the creature
    center_x = my_creature.x + (my_creature.size // 2)
    center_y = my_creature.y + (my_creature.size // 2)

    # 2. Calculate the end of the line (length of 30 pixels)
    line_length = 30
    end_x = center_x + math.cos(chase_angle) * line_length
    end_y = center_y + math.sin(chase_angle) * line_length

    # 3. Draw the line (White color)
    pygame.draw.line(screen, (255, 255, 255), (center_x, center_y), (end_x, end_y), 3)

    for i in range(food_amnt):
        pygame.draw.rect(screen, (0, 255, 0), (food_list[i].x, food_list[i].y, food_list[i].size, food_list[i].size))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
