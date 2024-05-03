# the marine ecosystem with pollution
import random

class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.x += random.randint(-1, 1)
        self.y += random.randint(-1, 1)
        self.x = max(0, min(self.x, width - 1))
        self.y = max(0, min(self.y, height - 1))

class Fish(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.energy = 10

    def eat(self):
        self.energy += 5

    def reproduce(self):
        if self.energy >= 20:
            self.energy -= 10
            return Fish(self.x, self.y)

    def update(self):
        self.energy -= 1
        self.move()

class Shark(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.energy = 20

    def eat(self, fish):
        self.energy += fish.energy

    def reproduce(self):
        if self.energy >= 40:
            self.energy -= 20
            return Shark(self.x, self.y)

    def update(self):
        self.energy -= 1
        self.move()

class Ocean:
    def __init__(self, width, height, num_fish, num_sharks):
        self.width = width
        self.height = height
        self.agents = []
        for _ in range(num_fish):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.agents.append(Fish(x, y))
        for _ in range(num_sharks):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.agents.append(Shark(x, y))

    def update(self):
        random.shuffle(self.agents)
        new_agents = []
        for agent in self.agents:
            if isinstance(agent, Fish):
                agent.update()
                if agent.energy > 0:
                    new_agents.append(agent)
                else:
                    new_agent = agent.reproduce()
                    if new_agent:
                        new_agents.append(new_agent)
            elif isinstance(agent, Shark):
                fish = self.find_fish(agent.x, agent.y)
                if fish:
                    agent.eat(fish)
                agent.update()
                if agent.energy > 0:
                    new_agents.append(agent)
                else:
                    new_agent = agent.reproduce()
                    if new_agent:
                        new_agents.append(new_agent)
        self.agents = new_agents

    def find_fish(self, x, y):
        for agent in self.agents:
            if isinstance(agent, Fish) and agent.x == x and agent.y == y:
                return agent
        return None

    def add_garbage(self, x, y):
        self.agents.append(Garbage(x, y))

class Garbage(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self):
        self.move()
        # Check if garbage is near a fish
        for agent in ocean.agents:
            if isinstance(agent, Fish) and abs(agent.x - self.x) <= 1 and abs(agent.y - self.y) <= 1:
                agent.energy -= 2

width = 10
height = 10
num_fish = 10
num_sharks = 5
num_garbage = 3


ocean = Ocean(width, height, num_fish, num_sharks)
def simulation():
    # Add garbage to the ocean
    for _ in range(num_garbage):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        ocean.add_garbage(x, y)

    for _ in range(100):
        print("Fish:", sum(isinstance(agent, Fish) for agent in ocean.agents))
        print("Sharks:", sum(isinstance(agent, Shark) for agent in ocean.agents))
        print("Garbage:", sum(isinstance(agent, Garbage) for agent in ocean.agents))
        ocean.update()
        for _ in range(num_garbage):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            ocean.add_garbage(x, y)
        print("------")

simulation()