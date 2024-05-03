import random


class ImmuneCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 100
        self.infected = False

    def move(self, hiv_cells):
        if self.infected:
            self.energy -= 2
        else:
            self.energy -= 1

        x_offset = random.randint(-1, 1)
        y_offset = random.randint(-1, 1)
        self.x += x_offset
        self.y += y_offset

        if self.infected:
            self.move_towards_hiv(hiv_cells)

    def move_towards_hiv(self, hiv_cells):
        nearest_hiv_cell = self.find_nearest_hiv(hiv_cells)
        if nearest_hiv_cell:
            x_diff = nearest_hiv_cell.x - self.x
            y_diff = nearest_hiv_cell.y - self.y

            if x_diff > 0:
                self.x += 1
            elif x_diff < 0:
                self.x -= 1

            if y_diff > 0:
                self.y += 1
            elif y_diff < 0:
                self.y -= 1

    def find_nearest_hiv(self, hiv_cells):
        nearest_hiv_cell = None
        min_distance = float('inf')

        for hiv_cell in hiv_cells:
            distance = self.calculate_distance(hiv_cell)
            if distance < min_distance:
                min_distance = distance
                nearest_hiv_cell = hiv_cell
        
        return nearest_hiv_cell

    def calculate_distance(self, other_cell):
        x_diff = other_cell.x - self.x
        y_diff = other_cell.y - self.y
        distance = (x_diff**2 + y_diff**2) ** 0.5
        return distance

    def eat(self, food):
        self.energy += food
        if self.energy > 200:
            self.energy = 200

    def divide(self, hiv_cells):
        if self.infected:
            divide_chance = random.uniform(0, 1)
            if divide_chance < 0.4:
                self.energy -= 25
                return ImmuneCell(self.x, self.y)
        else:
            if self.energy >= 150:
                self.energy /= 2
                return ImmuneCell(self.x, self.y)

    def check_infection(self, hiv_cells):
        for hiv_cell in hiv_cells:
            distance = self.calculate_distance(hiv_cell)
            if distance < 2:
                infection_chance = random.uniform(0, 1)
                if infection_chance < 0.8:
                    self.infected = True
                    break

    def fight_hiv(self):
        if self.infected and self.energy > 10:
            self.energy -= 10
            return random.uniform(0, 1) < 0.6
        else:
            return False
        
class HIVCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def move(self):
        x_offset = random.randint(-1, 1)
        y_offset = random.randint(-1, 1)
        self.x += x_offset
        self.y += y_offset

def simulation():
    width = 100
    height = 100
    num_cells = 50
    num_food = 100
    num_iterations = 100
    num_hiv_cells = 5

    env = Environment(width, height, num_cells, num_food, num_hiv_cells)
    for _ in range(num_iterations):
        env.update()

class Environment:
    def __init__(self, width, height, num_cells, num_food, num_hiv_cells):
        self.width = width
        self.height = height
        self.cells = [ImmuneCell(random.randint(0, width), random.randint(0, height)) for _ in range(num_cells)]
        self.food = [Food(random.randint(0, width), random.randint(0, height)) for _ in range(num_food)]
        self.hiv_cells = [HIVCell(random.randint(0, width), random.randint(0, height)) for _ in range(num_hiv_cells)]

    def update(self):
        for cell in self.cells:
            cell.move(self.hiv_cells)
            for food in self.food:
                if cell.x == food.x and cell.y == food.y:
                    cell.eat(food.energy)
                    self.food.remove(food)
            new_cell = cell.divide(self.hiv_cells)
            if new_cell:
                self.cells.append(new_cell)
            if cell.energy <= 0:
                self.cells.remove(cell)

        for hiv_cell in self.hiv_cells:
            hiv_cell.move()

        for cell in self.cells:
            cell.check_infection(self.hiv_cells)
            if cell.fight_hiv():
                self.hiv_cells = [hiv_cell for hiv_cell in self.hiv_cells if cell.calculate_distance(hiv_cell) >= 2]

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = random.randint(10, 50)

simulation()