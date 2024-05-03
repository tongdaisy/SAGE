# the behavior and interactions of immune cells in an immune system
import random

class ImmuneCell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 100

    def move(self):
        self.x += random.randint(-1, 1)
        self.y += random.randint(-1, 1)
        self.energy -= 1

    def eat(self, food):
        self.energy += food
        if self.energy > 200:
            self.energy = 200

    def divide(self):
        if self.energy >= 150:
            self.energy /= 2
            return ImmuneCell(self.x, self.y)

class Environment:
    def __init__(self, width, height, num_cells, num_food):
        self.width = width
        self.height = height
        self.cells = [ImmuneCell(random.randint(0, width), random.randint(0, height)) for _ in range(num_cells)]
        self.food = [Food(random.randint(0, width), random.randint(0, height)) for _ in range(num_food)]

    def update(self):
        for cell in self.cells:
            cell.move()
            for food in self.food:
                if cell.x == food.x and cell.y == food.y:
                    cell.eat(food.energy)
                    self.food.remove(food)
            new_cell = cell.divide()
            if new_cell:
                self.cells.append(new_cell)
            if cell.energy <= 0:
                self.cells.remove(cell)


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = random.randint(10, 50)

def simulation():
    width = 100
    height = 100
    num_cells = 50
    num_food = 100
    num_iterations = 100

    env = Environment(width, height, num_cells, num_food)
    for _ in range(num_iterations):
        env.update()

simulation()