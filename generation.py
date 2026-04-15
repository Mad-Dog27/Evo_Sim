import pygame
import random
import math

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
my_font = pygame.font.Font(None, 50)

food_amnt = random.randint(15, 20)
food_list = []
Gen_testing_list = []  
num_predators = 2
predator_list = []
count = 0
new_amount_x = 0
new_amount_y = 0
chase_angle = 0 # Initialize this so the line doesn't crash on frame 1

pygame.display.set_caption("Manual Control Mode")

class Food:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.qnty = 25

class Character:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

class Moving_Creature:
    def __init__(self, x, y, size, speed, turn_speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.view_w = 100 
        self.view_h = 100    
        self.random_move = 0.5  
        self.turn_speed = turn_speed
        self.angle = 0
        self.hunger = 100
        self.metabolism = (self.speed / 50) + (self.size / 50)**2 + (self.view_h + self.view_w) /1000
        self.alive = 1
        self.greed = 1
        self.score = 0
        self.patience = 0.8

    def update_view(self, view_w, view_h):
        self.view_w = view_w
        self.view_h = view_h

def draw_rotated_ellipse(surface, color, center, w, h, angle):
    target_rect = pygame.Rect(0, 0, w * 2, h * 2)
    ellipse_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA) # Keep SRCALPHA for transparency
    pygame.draw.ellipse(ellipse_surf, color, target_rect, 1)
    rotated_surf = pygame.transform.rotate(ellipse_surf, -math.degrees(angle))
    new_rect = rotated_surf.get_rect(center=center)
    surface.blit(rotated_surf, new_rect)

# Add a global counter
generation_count = 0
current_speed = 5
current_size = 40

def checkColision():
    for m in range(len(food_list) - 1, -1, -1):
        curr_x_diff = (food_list[m].x + (food_list[m].size // 2)) - cx
        curr_y_diff = (food_list[m].y + (food_list[m].size // 2)) - cy
        distance = math.sqrt(curr_x_diff**2 + curr_y_diff**2)
        if distance < (my_creature.size // 2): 
            my_creature.hunger += food_list[m].qnty
            if my_creature.hunger > 100:
                my_creature.hunger = 100
            food_list.pop(m)

def hunt():
    global count, new_amount_x, new_amount_y, chase_angle, cx, cy
    if len(food_list) > 0:
        
        checkColision()
        
        
        if my_creature.hunger > 0:
            my_creature.hunger -= my_creature.metabolism
        if my_creature.hunger <= 0:
            my_creature.alive = 0
        else:
            curr_prey_dist = 10000
            curr_prey = None

            if len(food_list) > 0:
                if my_creature.hunger < my_creature.greed *100:
                    curr_prey = findPrey(curr_prey,curr_prey_dist)
                    

                    if curr_prey is not None:
                        x_dif = (food_list[curr_prey].x + (food_list[curr_prey].size // 2)) - cx
                        y_dif = (food_list[curr_prey].y + (food_list[curr_prey].size // 2)) - cy
                        chase_angle = math.atan2(y_dif, x_dif)
                        my_creature.angle = chase_angle 
                        my_creature.x += my_creature.speed * math.cos(chase_angle)
                        my_creature.y += my_creature.speed * math.sin(chase_angle)
                    else:
                        if my_creature.patience > random.uniform(0,1):
                            moveRandom(count, chase_angle, 1)
                    
                        else:
                            moveRandom(count, chase_angle, 1)
                else:
                    moveRandom(count, chase_angle, 0)
                    
                        
                checkBoundaries()
                
    return cx, cy, count 

def findPrey(curr_prey, curr_prey_distance):
    # We need cx, cy to do the math, and my_creature to see the angle/vision
    global cx, cy 
    
    best_dist = curr_prey_distance # Use a local variable to track the closest
    found_index = curr_prey      # This will store the index of the best food

    for m in range(len(food_list)):
        dx = (food_list[m].x + (food_list[m].size // 2)) - cx
        dy = (food_list[m].y + (food_list[m].size // 2)) - cy
                
        # Rotated Math Point Check
        cos_a = math.cos(-my_creature.angle)
        sin_a = math.sin(-my_creature.angle)
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
                        
        # Ellipse check
        if (rx**2 / my_creature.view_w**2) + (ry**2 / my_creature.view_h**2) <= 1:
            distance = math.sqrt(dx**2 + dy**2)
            if distance < best_dist:
                best_dist = distance
                found_index = m 
                
    return found_index

def moveRandom(current_count, current_chase_angle, is_hungry):
    # We need global access to the 'random direction' variables
    global new_amount_x, new_amount_y, count, chase_angle
    if is_hungry:
        speed = my_creature.speed
    else:
        speed = my_creature.random_move * my_creature.speed
    if current_count > 20:
        # Choose a new random direction
        new_amount_x = random.uniform(-1, 1) * speed
        new_amount_y = random.uniform(-1, 1) * speed
        
        # Point the "vision" angle towards that new direction
        my_creature.angle = math.atan2(new_amount_y, new_amount_x)
        count = 0
    else:
        # Move based on the last chosen direction
        my_creature.x += new_amount_x
        my_creature.y += new_amount_y
        count += 1
        # Update the line direction to match current movement
        chase_angle = my_creature.angle


def checkBoundaries():
    if my_creature.x < 0: my_creature.x = 0
    if my_creature.y < 0: my_creature.y = 0
    if (my_creature.x + my_creature.size) > width: my_creature.x = width - my_creature.size
    if (my_creature.y + my_creature.size) > height: my_creature.y = height - my_creature.size

def reset_game(speed, size):
    global food_list, generation_count, predator_list, num_predators
    generation_count += 1
    food_list = []
    predator_list = []
    for i in range(random.randint(26, 30)):
        new_food = Food(random.uniform(0, width-10), random.uniform(0, height-10), 10)
        food_list.append(new_food)
    for i in range(num_predators):
        new_predator = Moving_Creature(width // 2, height // 2, size, speed, 0.5)
        predator_list.append(new_predator)
    # Return a creature with the new varied attributes
    return predator_list

# Setup
food_creature = Character(random.uniform(0, 1) * width, random.uniform(0, 1) * height, 10, 7)
predator_list = reset_game(current_speed, current_size)
running = True
tick = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Logic to reset when food is gone OR creature dies
    tick += 1
    if tick >30:
        new_food = Food(random.uniform(0, width-10), random.uniform(0, height-10), 10)
        food_list.append(new_food)
        tick = 0
    
    if my_creature.alive == 0:
        Gen_testing_list.append(my_creature.score)

        # Vary the attributes for the next run
        current_speed += 0.33      # Increase speed by 1 each time
        current_size -= 2       # Get smaller each time
        
        # Re-initialize with new values
        my_creature = reset_game(current_speed, current_size)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  food_creature.x -= food_creature.speed
    if keys[pygame.K_RIGHT]: food_creature.x += food_creature.speed
    if keys[pygame.K_UP]:    food_creature.y -= food_creature.speed
    if keys[pygame.K_DOWN]:  food_creature.y += food_creature.speed

    cx, cy = my_creature.x + (my_creature.size // 2), my_creature.y + (my_creature.size // 2)
    cx, cy, count = hunt()
    
    screen.fill((30, 30, 30))





    if my_creature.alive == 1:
        draw_rotated_ellipse(screen, (50, 50, 50), (cx, cy), my_creature.view_w, my_creature.view_h, my_creature.angle)
        pygame.draw.rect(screen, (0, 200, 255), (my_creature.x, my_creature.y, my_creature.size, my_creature.size))
        my_creature.score += 1
        line_length = 30
        end_x = cx + math.cos(chase_angle) * line_length
        end_y = cy + math.sin(chase_angle) * line_length
        pygame.draw.line(screen, (255, 255, 255), (cx, cy), (end_x, end_y), 3)
    else:
        pygame.draw.rect(screen, (255, 0, 0), (my_creature.x, my_creature.y, my_creature.size, my_creature.size))
    
    text_surface = my_font.render(f"Hunger: {int(my_creature.hunger)}", True, (255, 0,0))

    # 3. Blit (draw) to screen at (x, y) coordinates
    screen.blit(text_surface, (50, 50))
    pygame.draw.rect(screen, (255, 200, 0), (food_creature.x, food_creature.y, food_creature.size, food_creature.size))
    for f in food_list:
        pygame.draw.rect(screen, (0, 255, 0), (f.x, f.y, f.size, f.size))
    gen_text = my_font.render(f"Gen: {generation_count}", True, (255, 255, 255))
    screen.blit(gen_text, (50, 100)) # Draw it below the hunger text
    
    start_x, start_y = 600, 50 
    line_height = 30

# Loop through previous scores
    for i, score in enumerate(Gen_testing_list):
        # Render the text for each generation (e.g., "Gen 1: 5")
        score_text = my_font.render(f"Gen {i+1}: {int(score)}", True, (255, 255, 255))
        
        # Draw it on screen, moving down by 'line_height' for each new entry
        screen.blit(score_text, (start_x, start_y + (i * line_height)))
  

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
