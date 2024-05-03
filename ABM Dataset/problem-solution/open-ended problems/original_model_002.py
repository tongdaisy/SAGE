# the spread of a forest fire

import random
import matplotlib.pyplot as plt

class Forest:
    def __init__(self, size):
        self.size = size
        self.grid = [[Tree() for _ in range(size)] for _ in range(size)]

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
    def __init__(self, forest):
        self.forest = forest
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


class simulation:
    def __init__(self, size, num_agents):
        self.forest = Forest(size)
        self.agents = [Agent(self.forest) for _ in range(num_agents)]
        self.government = Government(self.forest, self.agents[0])

    def simulate(self, steps):
        for _ in range(steps):
            for agent in self.agents:
                agent.move()
                agent.extinguish_fire()


# Example usage
simulator = simulation(10, 5)  # Forest size of 10x10 with 5 agents
#simulator.simulate(10)  # Run the simulation for 10 steps
#simulator.forest.display()  # Display the state of the forest