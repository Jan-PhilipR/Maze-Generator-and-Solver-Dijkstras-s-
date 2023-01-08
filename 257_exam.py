import pygame
import random
import math
import sys
#Initiate Pygame
pygame.init()

#Window Size
width = 900
height = 542
window_height = height + 50
size = width , window_height

#Define window size
screen = pygame.display.set_mode(size)
simulation_start = False
cell_size = 30

start_maze = False


#Initiate clock
clock = pygame.time.Clock()

# Initiate and create fonts
pygame.font.init()
value_font = pygame.font.SysFont('Segoe UI', cell_size //3)
description_font = pygame.font.SysFont('Segoe UI', cell_size //3)
options_font = pygame.font.SysFont('Segoe UI', 25)
#Create a value for set-count of sidewinder algorithm, and step-count for dijkstra's algorithm
value = 0

# Class for each cell
class Cell():
    def __init__(self, x, y): # coordinates
        global value
        self.x = x
        self.y = y
        self.visited_walls = False
        self.visited = False
        self.active = False
        self.path = False
        self.walls = {"top": True, "right": True, "bottom": True, "left": True}

        self.value = value # give each cell a value
        value += 1 # increase value for each cell by 1 (sidewinder)

    def draw(self): # draw each cell and their walls
        x = self.x * cell_size
        y = self.y * cell_size

        if display_bool == True:
            if self.active == False: # Display "grey" during the sidewinder generation
                pygame.draw.rect(screen, pygame.Color("grey20"), pygame.Rect(x, y, cell_size ,cell_size))
            elif self.path == False: # Display "red" during the dijkstra's shortest-path finding
                pygame.draw.rect(screen, pygame.Color("red"), pygame.Rect(x, y, cell_size ,cell_size))
            elif self.path == True: # display "green" if cell is part of the path between start and goal
                pygame.draw.rect(screen, pygame.Color("green"), pygame.Rect(x, y, cell_size ,cell_size))
        elif self.path == True: # keep displaying "green" after dijkstra's is done
            pygame.draw.rect(screen, pygame.Color("green"), pygame.Rect(x, y, cell_size ,cell_size))
        else: # display "grey" if not part of the path
            pygame.draw.rect(screen, pygame.Color("grey20"), pygame.Rect(x, y, cell_size ,cell_size))
           
        # Create walls for each cell
        if self.walls["top"] == True:
            pygame.draw.line(screen, pygame.Color("white"), (x, y), (x + cell_size, y), 3)

        if self.walls["right"] == True:
            pygame.draw.line(screen, pygame.Color("white"), (x + cell_size, y), (x + cell_size, y + cell_size,), 3)

        if self.walls["left"] == True:
            pygame.draw.line(screen, pygame.Color("white"), (x, y + cell_size), (x, y), 3)

        if self.walls["bottom"] == True:
            pygame.draw.line(screen, pygame.Color("white"), (x + cell_size , y + cell_size,), (x, y + cell_size,), 3)


        # Create text for the set-values during the sidewinder algorithm
        text_surface = value_font.render(str(self.value), False, (0, 0, 0))
        if display_bool == True and self.active:
            screen.blit(text_surface, (x , y )) # display cell value when needed

    # Check row of cell
    def check_rows(self):
        return self.x

    # Check collumn of cell
    def check_cols(self): 
        return self.y

    # create outer lines (top, right and bottom (right is added and never removed))
    def remove_row(self):
        global rows
        
        if self.check_cols() == 0:
            self.walls["left"] = False
            self.walls["right"] = False
            self.walls["top"] = True
            if self.check_rows() == 0:
                self.walls["left"] = True
            elif self.check_rows() == rows - 1:
                self.walls["right"] == True
                

    # check neighbouring cells (x position, y position, value = True if looking for value, or False if not)
    def check_cell(self, x, y, value): 
        find_index = lambda x, y: x + y * cols

        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        if value == True:
            return cell_size_cells[find_index(x, y)].value
        else:
            return cell_size_cells[find_index(x, y)]

    # Remove right or bottom wall (as part of the sidewinder algorithm)
    def remove_cell_wall(self, x, y, wall):
        find_index = lambda x, y: x + y * cols
        
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        if wall == "right":
            cell_size_cells[find_index(x, y)].walls["right"] = False
        elif wall == "bottom":
            cell_size_cells[find_index(x, y)].walls["bottom"] = False

    # Create horizontal sets of cells (as part of the sidewinder algorithm)
    def sidewinder_hor(self):
        if random.randint(0, 1) == 1 and self.x != 0: # create 50% chance of uniting self cell and cell to the left and build a wall
            self.value = self.check_cell(self.x - 1, self.y, True)
            self.walls["left"] = False # delete left walls of this cell
            self.remove_cell_wall(self.x - 1, self.y, "right") # delete right wall of previous cell

    # Create upwards-carving passages for each set (as part of sidewinder)
    def sidewinder_vert(self):
        equal_cells = [] # create new list for this cell

        if self.check_cols() == 0:
            return

        if self.value != self.check_cell(self.x + 1, self.y, True): # create list of all cells with equal values
            for cell in cell_size_cells:
                    if cell.value == self.value:
                        equal_cells.append(cell)
            
        else: # if there are cells to the right with equal values, then skip
            return
        random_cell = random.choice(equal_cells)
        random_cell.walls["top"] = False # remove the top of one random cell in list
        random_cell.remove_cell_wall(random_cell.x, random_cell.y - 1, "bottom")

    # Further remove random walls to create more passages
    def clear_walls(self):
        global density
        if self.visited_walls == True:
            return

        chance = random.randint(0, int(density))
        if chance == 0 and self.check_cols() != 0:
            self.walls["top"] = False
            self.remove_cell_wall(self.x, self.y - 1, "bottom")
        elif chance == 1 and self.check_rows() != 0:
            self.walls["left"] = False
            self.remove_cell_wall(self.x - 1, self.y, "right")
        self.visited_walls = True

    # Highlight the start- and goal-cell in yellow. Also mark them with "start" and "goal"
    def draw_start_cell(self):
        start_cellFont = description_font.render("Start", False, ("black"))
        goal_cellFont = description_font.render("Goal", False, (0, 0, 0))
        x = self.x * cell_size
        y = self.y * cell_size
        pygame.draw.rect(screen, pygame.Color("yellow"), pygame.Rect(x + 1, y + 1 , cell_size ,cell_size))
        if self.check_cols() == start_cell.check_cols() and self.check_rows() == start_cell.check_rows():
            screen.blit(start_cellFont, (x , y ))
        elif self.check_cols() == goal_cell.check_cols() and self.check_rows() == goal_cell.check_rows():
            screen.blit(goal_cellFont, (x , y ))

    # For each cell, look at neighbours and add them to a list (each new cell takes one step)
    def dijkstras(self):
        global start_cell
        global next_cell

        if self.active == True:
            return

        top = self.check_cell(self.x, self.y -1, False )
        right = self.check_cell(self.x + 1, self.y, False)
        bottom = self.check_cell(self.x, self.y + 1, False)
        left = self.check_cell(self.x - 1, self.y, False)

        if top != False and not self.walls["top"] and not top.active:
            next_cell.insert(0, top)
            top.value = self.value + 1
        if right != False and not self.walls["right"] and not right.active:
            next_cell.insert(0, right)
            right.value = self.value + 1
        if left != False and not self.walls["left"] and not left.active:
            next_cell.insert(0, left)
            left.value = self.value + 1
        if bottom != False and not self.walls["bottom"] and not bottom.active:
            next_cell.insert(0, bottom)
            bottom.value = self.value + 1

        self.active = True

    # recursion part of dijkstra's: find back to the start from the goal cell
    def recur_dijkstra(self):
        global goal_cell
        global next_child_cell

        self.path = True    # make part of path (color green)

        child_cell = []
        top = self.check_cell(self.x, self.y -1, False) # top cell
        right = self.check_cell(self.x + 1, self.y, False) # right cell
        bottom = self.check_cell(self.x, self.y + 1, False) # bottom cell
        left = self.check_cell(self.x - 1, self.y, False) # left cell

        if top != False and not self.walls["top"]:
            child_cell.append(top)
        if right != False and not self.walls["right"]:
            child_cell.append(right)
        if left != False and not self.walls["left"]:
            child_cell.append(left)
        if bottom != False and not self.walls["bottom"]:
            child_cell.append(bottom)

        for cell in child_cell: #find next cell in path
            if cell.value == (self.value - 1) and cell.active == True:
                next_child_cell = cell


# Bool for displaying values
display_bool = True

# Start of row count (for sidewinder algorithm)
row_count = 0

# Define starting and goal cells
x_cell_beg, y_cell_beg, x_cell_end, y_cell_end = None, None, None, None

# Bool for when starting and goal cells are selected
beginning_cell_bool = False
goal_cell_bool = False

# Start and goal cells
start_cell = None
goal_cell = None

# List for the next cell of dijkstra's
next_cell = []
total_steps = 0
# Object for the recursion of dijkstra's
next_child_cell = None

# Bool for when Dijkstra's is activated (after start and goal cells are selected (Press ENTER))
dijkstras_ON = False

# Define time and message for taking time of dijkstra's
start_time = 0
message = ""

# Options Menu
options_menu = 0
density = 12
density_string = ""

speed = 60
speed_string = "Real-Time"

time_since_enter = 0
# Text
title_text = options_font.render("MAZE GENERATOR AND SOLVER", False, ("white"))
cellsize_text = options_font.render(f"Cell Size: {cell_size}", False, ("white"))
density_text = options_font.render(f"Density: {density_string}", False, ("white"))
speed_text = options_font.render(speed_string, False, ("white"))

options = options_font.render("Navigate with Arrow Keys. Generate maze with ENTER.", False, ("black"))
simulation = options_font.render("Select Start and Goal cells. Press ENTER to solve.", False, ("black"))




# Main Loop
while True:
    screen.fill("grey50")
    # Quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()


    if start_maze == True:
        # Number of rows and collumns
        rows = height // cell_size
        cols = width // cell_size
        # List of all cells
        cell_size_cells = [Cell(col, row) for row in range(rows) for col in range(cols)] 
        simulation_start = True
    # Generate Maze
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            start_maze = True

    if simulation_start == False:
        if density == 2:
            density_string = "Low"
        elif density == 6:
            density_string = "Medium"
        else:
            density_string = "High"
        if speed == 60:
            speed_string = "Real-Time"
        else:
            speed_string = "Step-by-Step"

        pygame.draw.rect(screen, pygame.Color("grey10"), pygame.Rect((width // 2) - 250, 50, 500, 100))
        pygame.draw.rect(screen, pygame.Color("grey10"), pygame.Rect((width // 2) - 150, 200, 300, 50))
        pygame.draw.rect(screen, pygame.Color("grey10"), pygame.Rect((width // 2) - 150, 300, 300, 50))
        pygame.draw.rect(screen, pygame.Color("grey10"), pygame.Rect((width // 2) - 150, 400, 300, 50))
        screen.blit(title_text, ((width // 2) - 200, 75))
        screen.blit(cellsize_text, ((width // 2) - 70, 210))
        screen.blit(density_text, ((width // 2) - 100, 310))
        screen.blit(speed_text, ((width // 2) - 80, 410))
        if event.type == pygame.KEYDOWN:
            clock.tick(5)
            if event.key == pygame.K_DOWN and options_menu < 2:
                options_menu += 1
            elif event.key == pygame.K_UP and options_menu > 0:
                options_menu += -1
            if options_menu == 0:
                if event.key == pygame.K_RIGHT and cell_size <= 75:
                    cell_size += 5
                elif event.key == pygame.K_LEFT and cell_size >= 15:
                    cell_size += -5
            if options_menu == 1:
                if density == 6:
                    if event.key == pygame.K_LEFT:
                        density = 2
                    if event.key == pygame.K_RIGHT:
                        density = 12
                elif density == 12 and event.key == pygame.K_LEFT:
                    density = 6
                elif density == 2 and event.key == pygame.K_RIGHT:
                    density = 6
            if options_menu == 2:
                if event.key == pygame.K_LEFT:
                    speed = 60
                elif event.key == pygame.K_RIGHT:
                    speed = 2
        else:
            clock.tick(60)


    if options_menu == 0 and simulation_start == False:
        cellsize_text = options_font.render(f"Cell Size: {cell_size}", False, ("white"))
        density_text = options_font.render(f"Density: {density_string}", False, ("grey50"))
        speed_text = options_font.render(speed_string, False, ("grey50"))
    elif options_menu == 1 and simulation_start == False:
        cellsize_text = options_font.render(f"Cell Size: {cell_size}", False, ("grey50"))
        density_text = options_font.render(f"Density: {density_string}", False, ("white"))
        speed_text = options_font.render(speed_string, False, ("grey50"))
    elif options_menu == 2 and simulation_start == False:
        cellsize_text = options_font.render(f"Cell Size: {cell_size}", False, ("grey50"))
        density_text = options_font.render(f"Density: {density_string}", False, ("grey50"))
        speed_text = options_font.render(speed_string, False, ("white"))
        
    # ========================= SIMULATION =========================
    if simulation_start == True:
        start_maze = False
        if dijkstras_ON == False:
            screen.blit(simulation, (1, height))
        # Draw all cells, and remove first row
        for cell in cell_size_cells:
            cell.remove_row()
            cell.draw()
            

        for col in range(cols):
            for cell in cell_size_cells[row_count: row_count + rows]: # check all cells for each row and unite cells
                cell.sidewinder_hor()
            for cell in cell_size_cells[row_count: row_count + rows]: # check all cells for each row and remove random top
                cell.sidewinder_vert()
            row_count = row_count + rows # reset after each row (next row)


        # Draw all cells, and further remove walls
        for cell in cell_size_cells: # draw all cells
            cell.clear_walls()
            


        # Select Starting cell
        mousex,mousey=pygame.mouse.get_pos()
        if not beginning_cell_bool:
            if event.type == pygame.MOUSEBUTTONUP:
                for cell in cell_size_cells:
                    x_cell_beg = math.floor(mousex / cell_size)
                    y_cell_beg = math.floor(mousey / cell_size)
                    start_cell = cell.check_cell(x_cell_beg, y_cell_beg, False)
                    beginning_cell_bool = True
                    next_cell.append(start_cell)
        else:
            start_cell.draw_start_cell()

        # Select Goal Cell
        if  beginning_cell_bool == True:
            if goal_cell_bool == False:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for cell in cell_size_cells:
                        x_cell_end = math.floor(mousex / cell_size)
                        y_cell_end = math.floor(mousey / cell_size)
                        goal_cell = cell.check_cell(x_cell_end, y_cell_end, False)
                        goal_cell_bool = True
                        
            else:
                goal_cell.draw_start_cell()
                total_steps = goal_cell.value

        # If cells are selected, press ENTER to start Dijkstra's
        if start_cell and goal_cell:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    dijkstras_ON = True
                    start_time = pygame.time.get_ticks()
            if dijkstras_ON == True:
            # ==================== Dijkstra's ===================================
                start_cell.draw_start_cell()
                goal_cell.draw_start_cell()
                
                clock.tick(speed)
                if goal_cell.active == False and start_cell != next_child_cell:
                    display_value = True
                    start_cell.value = 0
                    for item in next_cell:
                        item.dijkstras()
                        item.draw()
                        next_cell.remove(item)
                elif goal_cell.active == True and start_cell != next_child_cell:
                    goal_cell.draw_start_cell()
                    if next_child_cell == None:
                        goal_cell.recur_dijkstra()
                    else:
                        next_child_cell.recur_dijkstra()
                else:
                    display_bool = False      # disable all cell values
                    # Measure time for Dijkstra's Algorithm
                    if not message:
                        time_since_enter = pygame.time.get_ticks() - start_time
                        message = 'Milliseconds since enter: ' + str(time_since_enter)
                        print(message)
                # ===================================================================
            elif start_cell:
                start_cell.draw_start_cell()

    if simulation_start == False:
        screen.blit(options, (1, height))
    if simulation_start == True and time_since_enter != 0:
        if speed == 60:
            success = options_font.render(f"Success! Time spent: {time_since_enter} milliseconds. Steps taken: {total_steps}", False, ("black"))
        else:
            success = options_font.render(f"Success! Steps taken: {total_steps}", False, ("black"))
        screen.blit(success, (1, height))
    pygame.display.flip()
