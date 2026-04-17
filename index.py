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
# Add a global counter
generation_count = 0
current_speed = 2
current_size = 10
chase_angle = 0 # Initialize this so the line doesn't crash on frame 1
fam_trees = [1,1,1]
pygame.display.set_caption("Manual Control Mode")

class Food:
    def __init__(self, x, y, size, type):
        self.x = x
        self.y = y
        self.size = size
        if type == "creature":
            self.qnty = 25
        else:
            self.qnty = 20
class Character:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

class Moving_Creature:

    def __init__(self, x, y, size, speed, vision, fam_tree, colour):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.view_w = vision[0] 
        self.view_h = vision[1]
        self.vision = vision
        self.random_move = 0.5  
        self.angle = 0
        self.hunger = 100
        self.metabolism = ((self.speed / 50) + (self.size / 50)**2 + (self.view_h + self.view_w) /1000)
        self.move_cost = 0.0005 * self.size
        self.greed = 1
        self.patience = 1
        self.alive = 1
        self.count = 0              # Moved from global
        self.new_amount_x = 0       # Moved from global
        self.new_amount_y = 0       # Moved from global
        self.chase_angle = 0
        self.family_tree = fam_tree
        self.hostility = 0
        self.colour = colour
        self.horny = 0.5
        self.baby_amount = 1
        self.repro_timer = 0
        
    def update_view(self, view_w, view_h):
        self.view_w = view_w
        self.view_h = view_h
    
    def update_specs(self, greed, patience, move_cost):
        self.greed = greed
        self.patience = patience
        self.move_cost = move_cost

    def tax_move(self, move):
        self.hunger -= move * self.move_cost *self.size
    def random_stats(self, stats):
        self.size = stats[0]
        self.speed = stats[1]
        self.vision = stats[2]
        self.view_w = self.vision[0] 
        self.view_h = self.vision[1] 

        self.greed = stats[3]
        self.patience = stats[4]
        self.horny = stats[5]
        self.hostility = stats[6]
        self.stats = stats[:]   # copy, not nested list
        self.metabolism = ((self.speed / 50) + (self.size / 50)**2 + (self.view_h + self.view_w) /1000)
        self.move_cost = 0.0005 * self.size

        #(size, speed, vision, greed, patience, horny, hostility)



def draw_rotated_ellipse(surface, color, center, w, h, angle):
    # 1. Make the surface slightly larger than the ellipse to allow for rotation
    padding = 2
    target_rect = pygame.Rect(0, 0, w * 2, h * 2)
    ellipse_surf = pygame.Surface((w * 2 + padding, h * 2 + padding), pygame.SRCALPHA)
    
    # 2. Draw the ellipse in the center of that surface
    pygame.draw.ellipse(ellipse_surf, color, target_rect, 1)
    
    # 3. Rotate (using -degrees because pygame rotations are counter-clockwise)
    rotated_surf = pygame.transform.rotate(ellipse_surf, -math.degrees(angle))
    
    # 4. CRITICAL: Re-center the new, larger surface onto the predator's center
    new_rect = rotated_surf.get_rect(center=center)
    surface.blit(rotated_surf, new_rect)


def checkColision(this_creature):
    for m in range(len(food_list) - 1, -1, -1):
        curr_x_diff = (food_list[m].x + (food_list[m].size // 2)) - cx
        curr_y_diff = (food_list[m].y + (food_list[m].size // 2)) - cy
        distance = math.sqrt(curr_x_diff**2 + curr_y_diff**2)
        if distance < (this_creature.size // 2): 
            this_creature.hunger += food_list[m].qnty
            if this_creature.hunger > 100:
                this_creature.hunger = 100
            food_list.pop(m)
    
    for other in predator_list:
        if other != this_creature:
            dx = other.x - this_creature.x
            dy = other.y - this_creature.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist < this_creature.size:
                if this_creature.size > other.size:
                    other.alive = 0
                    if this_creature.hunger < this_creature.greed *100:
                        predator_list.remove(other)
                        this_creature.hunger += 50
                    else:
                        new_food = Food(other.x, other.y, other.size, "creature")
                        food_list.append(new_food)
                        predator_list.remove(other)
                    

def hunt(this_creature):
    global cx, cy

    checkColision(this_creature)

    # Hunger + death
    if this_creature.hunger > 0:
        this_creature.hunger -= this_creature.metabolism
    else:
        this_creature.alive = 0
        fam_trees[this_creature.family_tree] -= 1
        new_food = Food(this_creature.x, this_creature.y, this_creature.size, "creature")
        food_list.append(new_food)
        predator_list.remove(this_creature)
        return cx, cy, 0

    # --- FIND TARGETS ---
    food_index = None
    creature_index = None

    if len(food_list) > 0:
        food_index = findPrey(this_creature, None, 10000)

    if len(predator_list) > 1 and this_creature.hostility > 0.67:
        creature_index = huntOtherCreature(this_creature, None, 10000)

    # --- DECIDE WHAT TO CHASE ---
    target = None

    if creature_index is not None:
        target = ("creature", creature_index)
    elif food_index is not None:
        target = ("food", food_index)

    # --- MOVE TOWARD TARGET ---
    if target is not None:
        if target[0] == "creature":
            prey = predator_list[target[1]]
        else:
            prey = food_list[target[1]]

        x_dif = (prey.x + prey.size // 2) - cx
        y_dif = (prey.y + prey.size // 2) - cy

        angle = math.atan2(y_dif, x_dif)
        this_creature.angle = angle

        updatePosition(
            this_creature,
            this_creature.speed * math.cos(angle),
            this_creature.speed * math.sin(angle)
        )

    else:
        moveRandom(this_creature, 1)

    checkBoundaries(this_creature)

    return cx, cy, 0          
                

                
    return cx, cy, count 
def huntOtherCreature(this_creature, curr_prey, curr_prey_dist):
    global cx, cy 
    
    best_dist = curr_prey_dist # Use a local variable to track the closest
    found_index = curr_prey      # This will store the index of the best food
    index = predator_list.index(this_creature)
    for m in range(len(predator_list)):
        if m != index:
            dx = (predator_list[m].x + (predator_list[m].size // 2)) - cx
            dy = (predator_list[m].y + (predator_list[m].size // 2)) - cy
                
        # Rotated Math Point Check
            cos_a = math.cos(-this_creature.angle)
            sin_a = math.sin(-this_creature.angle)
            rx = dx * cos_a - dy * sin_a
            ry = dx * sin_a + dy * cos_a
                        
        # Ellipse check
            if (rx**2 / this_creature.view_w**2) + (ry**2 / this_creature.view_h**2) <= 1:
                distance = math.sqrt(dx**2 + dy**2)
                if distance < best_dist:
                    best_dist = distance
                    found_index = m 
    return found_index
    
def updatePosition(this_creature, move_x, move_y): # Use the passed values
    this_creature.x += move_x
    this_creature.y += move_y
    distance = math.sqrt(move_x**2 + move_y**2)
    this_creature.tax_move(distance)


def findPrey(this_creature, curr_prey, curr_prey_distance):
    # We need cx, cy to do the math, and my_creature to see the angle/vision
    global cx, cy 
    
    best_dist = curr_prey_distance # Use a local variable to track the closest
    found_index = curr_prey      # This will store the index of the best food

    for m in range(len(food_list)):
        dx = (food_list[m].x + (food_list[m].size // 2)) - cx
        dy = (food_list[m].y + (food_list[m].size // 2)) - cy
                
        # Rotated Math Point Check
        cos_a = math.cos(-this_creature.angle)
        sin_a = math.sin(-this_creature.angle)
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
                        
        # Ellipse check
        if (rx**2 / this_creature.view_w**2) + (ry**2 / this_creature.view_h**2) <= 1:
            distance = math.sqrt(dx**2 + dy**2)
            if distance < best_dist:
                best_dist = distance
                found_index = m 
                
    return found_index

def moveRandom(this_creature, is_hungry):
    # Determine speed based on hunger state
    speed = this_creature.speed if is_hungry else this_creature.speed * this_creature.random_move
    
    if this_creature.count > 20:
        # Update the creature's own movement variables
        this_creature.new_amount_x = random.uniform(-1, 1) * speed
        this_creature.new_amount_y = random.uniform(-1, 1) * speed
        this_creature.angle = math.atan2(this_creature.new_amount_y, this_creature.new_amount_x)
        this_creature.count = 0
    else:
        this_creature.x += this_creature.new_amount_x
        this_creature.y += this_creature.new_amount_y
        this_creature.count += 1
        this_creature.chase_angle = this_creature.angle


def checkBoundaries(this_creature):
    if this_creature.x < 0: this_creature.x = 0
    if this_creature.y < 0: this_creature.y = 0
    if (this_creature.x + this_creature.size) > width: this_creature.x = width - this_creature.size
    if (this_creature.y + this_creature.size) > height: this_creature.y = height - this_creature.size

def randomizeStats(this_creature):
    stats_size = random.uniform(8,15)
    stats_speed = 70*(1/stats_size)
    stats_vision = [random.uniform(40, 100), random.uniform(40, 100)]
    stats_greed = random.uniform(0,1)
    stats_patience = random.uniform(40, 100)
    stats_horny = random.uniform(0,1)
    stats_hostility = random.uniform(0,1)
    
    stats = [stats_size, stats_speed, stats_vision, stats_greed, stats_patience, stats_horny, stats_hostility]
    this_creature.random_stats(stats) 

def reset_game(speed, size):
    global food_list, generation_count, predator_list, num_predators
    generation_count += 1
    food_list = []
    predator_list = []
    stats = []
    fam_trees = [1, 1, 1]
    for i in range(random.randint(26, 30)):
        new_food = Food(random.uniform(0, width-10), random.uniform(0, height-10), 3, "food")
        food_list.append(new_food)

    #(size, speed, vision, greed, patience, horny)
        #, x, y, size, speed, vision
    new_predator = Moving_Creature(width // 3, height // 2, size, speed, [60, 40], 0, (0, 0, 255))
    randomizeStats(new_predator)
    predator_list.append(new_predator)
    new_predator = Moving_Creature(width // 2, height // 1, size, speed, [50, 50], 1, (255, 0, 0))
    randomizeStats(new_predator)
    predator_list.append(new_predator)
    new_predator = Moving_Creature(10, 10, size, speed, [70, 30], 2, (255, 255, 0))
    randomizeStats(new_predator)
    predator_list.append(new_predator)
    

    # Return a creature with the new varied attributes
    return predator_list
def make_clone(this_creature):
    # 1. Copy parent's stats
    new_stats = this_creature.stats[:]

    # 2. Pick one stat to mutate
    change_index = random.randint(0, 6)

    # 3. Apply mutation
    if change_index == 0:  # size
        new_stats[0] += random.uniform(-1, 1)
        new_stats[0] = max(5, min(20, new_stats[0]))  # clamp

        # keep speed tied to size
        new_stats[1] = 70 / new_stats[0]

    elif change_index == 1:  # speed (optional if tied to size)
        new_stats[1] += random.uniform(-1, 1)
        new_stats[1] = max(0.1, min(10, new_stats[1]))

    elif change_index == 2:  # vision (this is a list)
        new_stats[2][0] += random.uniform(-10, 10)
        new_stats[2][1] += random.uniform(-10, 10)

        new_stats[2][0] = max(10, min(150, new_stats[2][0]))
        new_stats[2][1] = max(10, min(150, new_stats[2][1]))

    else:  # greed, patience, horny, hostility
        new_stats[change_index] += random.uniform(-0.1, 0.1)
        new_stats[change_index] = max(0, min(1, new_stats[change_index]))

    # 4. Create new creature
    new_predator = Moving_Creature(
        this_creature.x,
        this_creature.y,
        this_creature.size,
        this_creature.speed,
        this_creature.vision[:],  # copy vision list
        this_creature.family_tree,
        this_creature.colour
    )

    # 5. Apply mutated stats
    new_predator.random_stats(new_stats)

    # 6. Add to world
    predator_list.append(new_predator)
    fam_trees[this_creature.family_tree] += 1
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
    if tick >19:
        new_food = Food(random.uniform(0, width-10), random.uniform(0, height-10), 3, "food")
        food_list.append(new_food)
        tick = 0
    
    if len(predator_list) == 0:
        #Gen_testing_list.append(my_creature.score)

        
        # Re-initialize with new values
        fam_trees=[1,1, 1]
        predator_list = reset_game(current_speed, current_size)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  food_creature.x -= food_creature.speed
    if keys[pygame.K_RIGHT]: food_creature.x += food_creature.speed
    if keys[pygame.K_UP]:    food_creature.y -= food_creature.speed
    if keys[pygame.K_DOWN]:  food_creature.y += food_creature.speed

    for this_creature in predator_list:
        if this_creature.alive:
            this_creature.repro_timer += 1
            # Update center points for this specific creature
            cx, cy = this_creature.x + (this_creature.size // 2), this_creature.y + (this_creature.size // 2)
            # Pass the creature into hunt
            cx, cy, count = hunt(this_creature)

            if this_creature.hunger > ((1 - this_creature.horny) * 100):
                if this_creature.repro_timer > 120:  # 2 seconds at 60 FPS
                    if random.uniform(0,1) > 0.7:
                        for i in range(this_creature.baby_amount): 
                            make_clone(this_creature)
                            this_creature.hunger -= 30
                            this_creature.repro_timer = 0

    
    screen.fill((30, 30, 30))
    screen.fill((30, 30, 30))

    for predator in predator_list:
        pcx, pcy = predator.x + (predator.size // 2), predator.y + (predator.size // 2)
        if predator.alive:
            draw_rotated_ellipse(screen, (50, 50, 50), (pcx, pcy), predator.view_w, predator.view_h, predator.angle)
            pygame.draw.rect(screen, (predator.colour), (predator.x, predator.y, predator.size, predator.size))
            hunger_text = my_font.render(f"H: {int(predator.hunger)}", True, (255, 255, 255))
            screen.blit(hunger_text, (predator.x, predator.y - 30))
            
        else:
            pygame.draw.rect(screen, (255, 0, 0), (predator.x, predator.y, predator.size, predator.size))

    ui_x = 20
    ui_y = 20
    spacing = 40
    colour_list = [(0,0,255), (255, 0,0), (255, 255,0)]
    line_height = 35 
    for i, val in enumerate(fam_trees):
        # Convert whatever the value is (int, float, string) into text
        text_surf = my_font.render(str(val), True, (colour_list[i]))
        screen.blit(text_surf, (20, 50 + (i * line_height)))


    
    

    # 3. Blit (draw) to screen at (x, y) coordinates
    pygame.draw.rect(screen, (255, 200, 0), (food_creature.x, food_creature.y, food_creature.size, food_creature.size))
    for f in food_list:
        pygame.draw.rect(screen, (0, 255, 0), (f.x, f.y, f.size, f.size))
    gen_text = my_font.render(f"Gen: {generation_count}", True, (255, 255, 255))
    screen.blit(gen_text, (20, 20)) # Draw it below the hunger text
    
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
