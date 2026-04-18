import pygame
import random
import math
import numpy as np
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
my_font = pygame.font.Font(None, 50)
selected_creature = None
food_amnt = random.randint(15, 20)
food_list = []
Gen_testing_list = []  
num_predators = 2
predator_list = []
count = 0
# Add a global counter
generation_count = 0
current_speed = .1
current_size = 10
chase_angle = 0 # Initialize this so the line doesn't crash on frame 1
init_fam_amount = 4
init_pop = 5
fam_trees = np.ones(init_pop) * init_fam_amount
colour_list = []

diet_types = ["herbivore", "omnivore", "carnivore"]
pygame.display.set_caption("Manual Control Mode")


class Tile:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        
        # ecosystem stats
        self.food_regen = random.uniform(0.1, 1.0)
        self.fertility = random.uniform(0.1, 1.0)
        self.roughness = random.uniform(0, 1)

tile_size = 20
cols = width // tile_size
rows = height // tile_size

grid = []

for y in range(rows):
    row = []
    for x in range(cols):
        row.append(Tile(x * tile_size, y * tile_size, tile_size))
    grid.append(row)


class Food:
    def __init__(self, x, y, size, type):
        self.x = x
        self.y = y
        self.size = size
        self.type = type
        if type == "creature":
            self.qnty = 15
        else:
            self.qnty = 10
class Character:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed

class Moving_Creature:

    def __init__(self, x, y, size, speed, vision, fam_tree, colour, diet):
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
        self.metabolism = ((self.speed * 0.8) +(self.size * 0.15) +((self.view_h + self.view_w) / 1200)) /10
        self.move_cost = 0.0005 * self.size
        self.greed = 1
        self.patience = 1
        self.alive = 1
        self.count = 0              # Moved from global
        self.new_amount_x = 0       # Moved from global
        self.new_amount_y = 0       # Moved from global
        self.chase_angle = 0
        self.family_tree = fam_tree
        self.hostility = 1
        self.colour = colour
        self.horny = 0.5
        self.baby_amount = 1
        self.repro_timer = 0

        self.diet = diet
        
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
        self.metabolism = ((self.speed * 0.8) +(self.size * 0.15) +((self.view_h + self.view_w) / 1200))/10
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
        if this_creature.diet != "carnivore":
            if distance < (this_creature.size // 2): 
                this_creature.hunger += food_list[m].qnty
                if this_creature.hunger > 100:
                    this_creature.hunger = 100
                food_list.pop(m)
        else:
            if food_list[m].type == "creature":
                if distance < (this_creature.size // 2): 
                    this_creature.hunger += food_list[m].qnty
                    if this_creature.hunger > 100:
                        this_creature.hunger = 100
                    food_list.pop(m)
    if this_creature.diet != "herbivore":
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
                        fam_trees[other.family_tree] -=1


def hunt(this_creature, cx, cy):

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

    if creature_index is not None: # stores [0,1] being "type" and index
        if this_creature.diet == "omnivore" or this_creature.diet == "carnivore":
            target = ("creature", creature_index)
    elif food_index is not None:
        if this_creature.diet == "omnivore" or this_creature.diet == "herbivore" or this_creature.diet == "carnivore":
            if this_creature.diet != "carnivore":
                target = ("food", food_index)
            elif food_list[food_index].type == "creature":
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
        if target[0] == "creature":
            if predator_list[target[1]].size > this_creature.size: #other is larger and thus may eat this creature
                angle += math.pi
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

def random_colour():

    r = random.uniform(0,255)
    b = random.uniform(0,255)
    a = random.uniform(0, 255)
    return [r,b,a]

def random_pos():

    x = random.randint(1,width)
    y = random.randint(1, height)

    return [x,y]
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
    stats_speed = 3 / math.sqrt(stats_size)
    vision_scale = math.sqrt(stats_size / 10)

    stats_vision = [
    random.uniform(40, 100) * vision_scale,
    random.uniform(40, 100) * vision_scale
    ]
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
    fam_trees = np.zeros(init_pop)
    for i in range(random.randint(26, 30)):
        new_food = Food(random.uniform(0, width-10), random.uniform(0, height-10), 3, "food")
        food_list.append(new_food)

    #(size, speed, vision, greed, patience, horny)
        #, x, y, size, speed, vision
    for i in range(init_pop):
        colour = random_colour()
        diet_index = random.randint(0,2)
        diet = diet_types[diet_index]

        new_predator = Moving_Creature(random_pos()[0], random_pos()[1], size, speed, [60, 40], i, colour, diet)
        randomizeStats(new_predator)
        for m in range(init_fam_amount):
            new_predator = Moving_Creature(
                random_pos()[0],
                random_pos()[1],
                size,
                speed,
                [60, 40],
                i,
                colour,
                diet
            )
            randomizeStats(new_predator)

            predator_list.append(new_predator)
            fam_trees[i] += 1
        colour_list.append(colour)
    

    # Return a creature with the new varied attributes
    return predator_list
def make_clone(this_creature):
    # 1. Copy parent's stats
    new_stats = this_creature.stats[:]

    chance_to_evolve = random.uniform(0,1)
    if chance_to_evolve == 0.11:
        current_diet = this_creature.diet
        diet_index = diet_types.index(current_diet)

        indices = list(range(len(predator_list)))
        indices.remove(diet_index)  # remove the current creature

        random_index = random.choice(indices)
        diet = diet_types[random_index]
    else:
        diet = this_creature.diet
    if chance_to_evolve > 0.5: # 50% chance for stat to change

        change_index = random.randint(0, 6)

        if change_index == 2:  # vision (this is a list)
            new_stats[2][0] += random.uniform(-10, 10)
            new_stats[2][1] += random.uniform(-10, 10)

            new_stats[2][0] = max(10, min(150, new_stats[2][0]))
            new_stats[2][1] = max(10, min(150, new_stats[2][1]))
        else:
            stat_to_change = this_creature.stats[change_index]
            change_amnt = (random.uniform(-1,1)/50)*stat_to_change
            new_stats[change_index] = stat_to_change + change_amnt
            if stat_to_change == 0:
                new_stats[1] = 70 / new_stats[0]

    # 4. Create new creature
    new_predator = Moving_Creature(
        this_creature.x,
        this_creature.y,
        this_creature.size,
        this_creature.speed,
        this_creature.vision[:],  # copy vision list
        this_creature.family_tree,
        this_creature.colour,
        diet
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
    if tick >50:
        new_food = Food(random.uniform(0, width-10), random.uniform(0, height-10), 3, "food")
        food_list.append(new_food)
        tick = 0
    
    if len(predator_list) == 0:
        #Gen_testing_list.append(my_creature.score)

        
        # Re-initialize with new values
        fam_trees= np.ones(init_pop) * init_fam_amount
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
            cx, cy, count = hunt(this_creature, cx, cy)

            if this_creature.hunger > ((1 - this_creature.horny) * 100):
                if this_creature.repro_timer > 120:  # 2 seconds at 60 FPS
                    if random.uniform(0,1) > 0.7:
                        for i in range(this_creature.baby_amount): 
                            make_clone(this_creature)
                            this_creature.hunger -= 50
                            this_creature.repro_timer = 0

    
    screen.fill((30, 30, 30))
    for row in grid:
        for tile in row:
            color = (
                int(tile.fertility * 255),
                int(tile.food_regen * 255),
                int(tile.roughness * 255)
            )
            pygame.draw.rect(screen, color, (tile.x, tile.y, tile.size, tile.size))
    for predator in predator_list:
        pcx, pcy = predator.x + (predator.size // 2), predator.y + (predator.size // 2)
        if predator.alive:
            draw_rotated_ellipse(screen, (50, 50, 50), (pcx, pcy), predator.view_w, predator.view_h, predator.angle)
            pygame.draw.rect(screen, (predator.colour), (predator.x, predator.y, predator.size, predator.size))
            
        else:
            pygame.draw.rect(screen, (255, 0, 0), (predator.x, predator.y, predator.size, predator.size))

    ui_x = 20
    ui_y = 20
    spacing = 40
    line_height = 35 
    for i, val in enumerate(fam_trees):
        # Convert whatever the value is (int, float, string) into text
        text_surf = my_font.render(f"F{i}: {int(val)}", True, colour_list[i])
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

    if event.type == pygame.MOUSEBUTTONDOWN:
        mx, my = pygame.mouse.get_pos()

        for creature in predator_list:
            rect = pygame.Rect(creature.x, creature.y, creature.size, creature.size)

            if rect.collidepoint(mx, my):
                selected_creature = creature
                selected_creature = creature
                break
    if selected_creature is not None:
        pygame.draw.rect(
            screen,
            (255, 255, 0),  # yellow border
            (selected_creature.x, selected_creature.y, selected_creature.size, selected_creature.size),
            2
        )
    if selected_creature not in predator_list:
        selected_creature = None
        
    if selected_creature is not None:
        info = f"Hunger: {int(selected_creature.hunger)} | type: {str(selected_creature.diet)}"
        text = my_font.render(info, True, (255, 255, 255))
        screen.blit(text, (20, 550))
        family_colour = colour_list[selected_creature.family_tree]
        pygame.draw.rect(
            screen,
            family_colour,
            (100, 100, 50, 50)
        )

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
