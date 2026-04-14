import pygame
import random
import math

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

food_amnt = random.randint(15, 20)
food_list = []
count = 0
new_amount_x = 0
new_amount_y = 0
chase_angle = 0 # Initialize this so the line doesn't crash on frame 1

pygame.display.set_caption("Manual Control Mode")

class Creature:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

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
        self.view_w = 350 
        self.view_h = 150      
        self.random_move = 0.5  
        self.turn_speed = turn_speed
        self.angle = 0

def draw_rotated_ellipse(surface, color, center, w, h, angle):
    target_rect = pygame.Rect(0, 0, w * 2, h * 2)
    ellipse_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA) # Keep SRCALPHA for transparency
    pygame.draw.ellipse(ellipse_surf, color, target_rect, 1)
    rotated_surf = pygame.transform.rotate(ellipse_surf, -math.degrees(angle))
    new_rect = rotated_surf.get_rect(center=center)
    surface.blit(rotated_surf, new_rect)

def reset_game():
    global food_list, my_creature
    food_list = []
    food_amnt = random.randint(26, 30) 
    for i in range(food_amnt):
        new_food = Creature(random.uniform(0, width-10), random.uniform(0, height-10), 10)
        food_list.append(new_food)
    my_creature = Moving_Creature(width // 2, height // 2, 40, 5, 0.5)

# Setup
food_creature = Character(random.uniform(0, 1) * width, random.uniform(0, 1) * height, 10, 7)
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

    cx, cy = my_creature.x + (my_creature.size // 2), my_creature.y + (my_creature.size // 2)

    if len(food_list) > 0:
        # Popping Loop
        for m in range(len(food_list) - 1, -1, -1):
            curr_x_diff = (food_list[m].x + (food_list[m].size // 2)) - cx
            curr_y_diff = (food_list[m].y + (food_list[m].size // 2)) - cy
            distance = math.sqrt(curr_x_diff**2 + curr_y_diff**2)
            if distance < (my_creature.size // 2): 
                food_list.pop(m)

        curr_prey_dist = 10000
        curr_prey = None

        if len(food_list) > 0:
            for m in range(len(food_list)):
                dx = (food_list[m].x + (food_list[m].size // 2)) - cx
                dy = (food_list[m].y + (food_list[m].size // 2)) - cy
                
                # Rotated Math Point Check
                cos_a = math.cos(-my_creature.angle)
                sin_a = math.sin(-my_creature.angle)
                rx = dx * cos_a - dy * sin_a
                ry = dx * sin_a + dy * cos_a
                
                if (rx**2 / my_creature.view_w**2) + (ry**2 / my_creature.view_h**2) <= 1:
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance < curr_prey_dist:
                        curr_prey_dist = distance
                        curr_prey = m 

            if curr_prey is not None:
                x_dif = (food_list[curr_prey].x + (food_list[curr_prey].size // 2)) - cx
                y_dif = (food_list[curr_prey].y + (food_list[curr_prey].size // 2)) - cy
                chase_angle = math.atan2(y_dif, x_dif)
                my_creature.angle = chase_angle 
                my_creature.x += my_creature.speed * math.cos(chase_angle)
                my_creature.y += my_creature.speed * math.sin(chase_angle)
            else:
                if count > 20:
                   new_amount_x = random.randint(-1,1)*my_creature.random_move*my_creature.speed
                   new_amount_y = random.randint(-1,1)*my_creature.random_move*my_creature.speed
                   my_creature.angle = math.atan2(new_amount_y, new_amount_x) # Point vision where moving
                   count = 0
                else:
                    my_creature.x += new_amount_x
                    my_creature.y += new_amount_y
                    count += 1
                    chase_angle = my_creature.angle
                
            # Reverted to your original IF boundaries
            if my_creature.x < 0: my_creature.x = 0
            if my_creature.y < 0: my_creature.y = 0
            if (my_creature.x + my_creature.size) > width: my_creature.x = width - my_creature.size
            if (my_creature.y + my_creature.size) > height: my_creature.y = height - my_creature.size

    screen.fill((30, 30, 30))
    draw_rotated_ellipse(screen, (50, 50, 50), (cx, cy), my_creature.view_w, my_creature.view_h, my_creature.angle)

    pygame.draw.rect(screen, (0, 200, 255), (my_creature.x, my_creature.y, my_creature.size, my_creature.size))
    
    line_length = 30
    end_x = cx + math.cos(chase_angle) * line_length
    end_y = cy + math.sin(chase_angle) * line_length
    pygame.draw.line(screen, (255, 255, 255), (cx, cy), (end_x, end_y), 3)

    pygame.draw.rect(screen, (255, 200, 0), (food_creature.x, food_creature.y, food_creature.size, food_creature.size))
    for f in food_list:
        pygame.draw.rect(screen, (0, 255, 0), (f.x, f.y, f.size, f.size))
    
    if len(food_list) == 0:
        reset_game() 

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
