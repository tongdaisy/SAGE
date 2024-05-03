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

    def suffer_toxicity(self, toxicity_level):
        self.energy -= toxicity_level

    def update(self, nearby_nuclear_waste):
        self.energy -= 1
        self.move()
        for waste in nearby_nuclear_waste:
            self.suffer_toxicity(waste.toxicity_level)

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

    def update(self, nearby_fish):
        self.energy -= 1
        self.move()
        if len(nearby_fish) >= 1:
            fish = random.choice(nearby_fish)
            self.eat(fish)

class NuclearWaste(Agent):
    def __init__(self, x, y, toxicity_level, decay_rate):
        super().__init__(x, y)
        self.toxicity_level = toxicity_level
        self.decay_rate = decay_rate

    def spread_toxicity(self, nearby_agents):
        for agent in nearby_agents:
            agent.suffer_toxicity(self.toxicity_level)

    def update(self):
        self.decay()
        nearby_agents = self.get_nearby_agents()
        self.spread_toxicity(nearby_agents)

    def decay(self):
        self.toxicity_level -= self.decay_rate

    def get_nearby_agents(self):
        nearby_agents = []
        for agent in ocean.agents:
            if agent != self:
                distance = abs(self.x - agent.x) + abs(self.y - agent.y)
                if distance <= 1:
                    nearby_agents.append(agent)
        return nearby_agents

class MarinePlant(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.energy = 5

    def grow(self):
        self.energy += 1

    def update(self):
        self.grow()

class Predator(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.energy = 15

    def eat(self, fish):
        self.energy += fish.energy

    def update(self, nearby_fish):
        self.energy -= 1
        self.move()
        if len(nearby_fish) >= 1:
            fish = random.choice(nearby_fish)
            self.eat(fish)

class Ocean:
    def __init__(self, width, height, num_fish, num_sharks, num_nuclear_waste, num_marine_plants, num_predators):
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
        for _ in range(num_nuclear_waste):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            toxicity_level = random.randint(1, 10)
            decay_rate = random.randint(1, 3)
            self.agents.append(NuclearWaste(x, y, toxicity_level, decay_rate))
        for _ in range(num_marine_plants):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.agents.append(MarinePlant(x, y))
        for _ in range(num_predators):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            self.agents.append(Predator(x, y))

    def update(self):
        random.shuffle(self.agents)
        new_agents = []
        for agent in self.agents:
            if isinstance(agent, Fish):
                nearby_nuclear_waste = self.find_nearby_nuclear_waste(agent.x, agent.y)
                agent.update(nearby_nuclear_waste)
                if agent.energy > 0:
                    new_agents.append(agent)
                else:
                    new_agent = agent.reproduce()
                    if new_agent:
                        new_agents.append(new_agent)
            elif isinstance(agent, Shark):
                nearby_fish = self.find_nearby_fish(agent.x, agent.y)
                agent.update(nearby_fish)
                if agent.energy > 0:
                    new_agents.append(agent)
                else:
                    new_agent = agent.reproduce()
                    if new_agent:
                        new_agents.append(new_agent)
            elif isinstance(agent, NuclearWaste):
                agent.update()
                new_agents.append(agent)
            elif isinstance(agent, MarinePlant):
                agent.update()
                new_agents.append(agent)
            elif isinstance(agent, Predator):
                nearby_fish = self.find_nearby_fish(agent.x, agent.y)
                agent.update(nearby_fish)
                if agent.energy > 0:
                    new_agents.append(agent)
        self.agents = new_agents

    def find_nearby_fish(self, x, y):
        nearby_fish = []
        for agent in self.agents:
            if isinstance(agent, Fish):
                distance = abs(x - agent.x) + abs(y - agent.y)
                if distance <= 1:
                    nearby_fish.append(agent)
        return nearby_fish

    def find_nearby_nuclear_waste(self, x, y):
        nearby_nuclear_waste = []
        for agent in self.agents:
            if isinstance(agent, NuclearWaste):
                distance = abs(x - agent.x) + abs(y - agent.y)
                if distance <= 1:
                    nearby_nuclear_waste.append(agent)
        return nearby_nuclear_waste