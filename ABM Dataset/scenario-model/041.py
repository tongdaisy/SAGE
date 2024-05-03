import random

class Animal:
    def __init__(self, animal_type, position):
        self.type = animal_type
        self.status = "Alive"
        self.position = position

class Forest:
    def __init__(self, size):
        self.size = size
        self.grid = [[Tree() for _ in range(size)] for _ in range(size)]
        self.animals = []

    def get_neighbors(self, x, y):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i != 0 or j != 0) and 0 <= x + i < self.size and 0 <= y + j < self.size:
                    neighbors.append((x + i, y + j))
        return neighbors

    def spread_fire(self, x, y):
        tree = self.grid[x][y]
        if tree.status == "Burning":
            return

        tree.set_status("Burning")
        neighbors = self.get_neighbors(x, y)
        for nx, ny in neighbors:
            if self.grid[nx][ny].status == "Healthy":
                self.grid[nx][ny].set_status("Burning")
                self.spread_fire_to_animal(nx, ny)

    def spread_fire_to_animal(self, x, y):
        for animal in self.animals:
            if animal.position == (x, y) and animal.status == "Alive":
                animal.status = "Affected"

    def count_burning_trees(self):
        count = 0
        for row in self.grid:
            for tree in row:
                if tree.status == "Burning":
                    count += 1
        return count

    def display(self):
        for row in self.grid:
            for tree in row:
                print(tree.status[0], end=" ")
            print()

class Tree:
    def __init__(self):
        self.status = "Healthy"

    def set_status(self, status):
        self.status = status

class Agent:
    def __init__(self, forest, animal_type):
        self.forest = forest
        self.animal_type = animal_type
        self.x = random.randint(0, forest.size - 1)
        self.y = random.randint(0, forest.size - 1)

    def move(self):
        neighbors = self.forest.get_neighbors(self.x, self.y)
        random.shuffle(neighbors)
        for nx, ny in neighbors:
            if self.forest.grid[nx][ny].status == "Burning":
                self.forest.spread_fire(nx, ny)
                self.x, self.y = nx, ny
                return

    def extinguish_fire(self):
        if self.forest.grid[self.x][self.y].status == "Burning":
            self.forest.grid[self.x][self.y].set_status("Healthy")

class Government:
    def __init__(self, forest, agent):
        self.forest = forest
        self.agent = agent


class Simulation:
    def __init__(self, size, num_agents):
        self.forest = Forest(size)
        self.agents = [Agent(self.forest, "Deer") for _ in range(num_agents)]
        self.government = Government(self.forest, self.agents[0])

    def distribute_animals(self, num_animals):
        for _ in range(num_animals):
            x = random.randint(0, self.forest.size - 1)
            y = random.randint(0, self.forest.size - 1)
            animal_type = random.choice(["Deer", "Rabbit", "Fox"])
            animal = Animal(animal_type, (x, y))
            self.forest.animals.append(animal)

    def simulate(self, steps):
        for _ in range(steps):
            for agent in self.agents:
                agent.move()
                agent.extinguish_fire()


# Example usage
simulator = Simulation(10, 5)  # Forest size of 10x10 with 5 agents
simulator.distribute_animals(10)  # Distribute 10 animals in the forest
simulator.simulate(10)  # Run the simulation for 10 steps
simulator.forest.display()  # Display the state of the forest

# Additional methods for animals and fire spread can be added as needed.