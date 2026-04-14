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


def reset_game():
    global food_list, my_creature
    food_list = []
    food_amnt = random.randint(3, 7)
    for i in range(food_amnt):
        new_food = Creature(random.uniform(0, width-10), random.uniform(0, height-10), 10, 7)
        food_list.append(new_food)
    my_creature = Creature(width // 2, height // 2, 40, 5)

# Call it once to start the game
reset_game()

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
    # Iterate backwards: from (length - 1) down to 0
    if len(food_list) > 0:
        for m in range(len(food_list) - 1, -1, -1):
            curr_x_diff = (food_list[m].x + (food_list[m].size // 2)) - (my_creature.x + (my_creature.size // 2))
            curr_y_diff = (food_list[m].y + (food_list[m].size // 2)) - (my_creature.y + (my_creature.size // 2))

            distance = math.sqrt(curr_x_diff**2 + curr_y_diff**2)
            
            # TIP: Use the 'distance' variable you just calculated! 
            # Checking if distance < 20 is more accurate than x/y diffs.
            if distance < (my_creature.size // 2): 
                food_list.pop(m)
        curr_prey_dist = 10000
        curr_prey = 0
        if len(food_list) > 0:
            for m in range(len(food_list)):
                curr_x_diff = (food_list[m].x + (food_list[m].size // 2)) - (my_creature.x + (my_creature.size // 2))
                curr_y_diff = (food_list[m].y + (food_list[m].size // 2)) - (my_creature.y + (my_creature.size // 2))

                distance = math.sqrt(curr_x_diff**2 + curr_y_diff**2)
                
                if distance < curr_prey_dist:
                    curr_prey_dist = distance
                    curr_prey = m 
            x_dif = (food_list[curr_prey].x + (food_list[curr_prey].size // 2)) - (my_creature.x + (my_creature.size // 2))
            y_dif = (food_list[curr_prey].y + (food_list[curr_prey].size // 2)) - (my_creature.y + (my_creature.size // 2))

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
    if len(food_list) > 0:
        for i in range(len(food_list)):
            pygame.draw.rect(screen, (0, 255, 0), (food_list[i].x, food_list[i].y, food_list[i].size, food_list[i].size))
    else:
        reset_game() 
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
