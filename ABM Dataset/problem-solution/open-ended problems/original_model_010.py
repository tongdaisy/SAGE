# the spread of rumor in the social network
import random

class Agent:
    def __init__(self, agent_id, neighbors):
        self.agent_id = agent_id
        self.neighbors = neighbors
        self.rumors_heard = set()

    def hear_rumor(self, rumor):
        self.rumors_heard.add(rumor)

    def spread_rumor(self, rumor, agents):
        for neighbor in self.neighbors:
            agents[neighbor].hear_rumor(rumor)

class Network:
    def __init__(self):
        self.agents = {}

    def add_agent(self, agent_id, neighbors):
        agent = Agent(agent_id, neighbors)
        self.agents[agent_id] = agent

    def get_agent(self, agent_id):
        return self.agents[agent_id]

    def get_random_agent(self):
        return random.choice(list(self.agents.values()))

class Rumor:
    def __init__(self, rumor_id, initial_agent_id):
        self.rumor_id = rumor_id
        self.initial_agent_id = initial_agent_id
        self.spread_agents = {initial_agent_id}

    def add_spread_agent(self, agent_id):
        self.spread_agents.add(agent_id)

class Simulation:
    def __init__(self, network, rumor):
        self.network = network
        self.rumor = rumor

    def run(self, num_iterations):
        initial_agent = self.network.get_agent(self.rumor.initial_agent_id)
        initial_agent.hear_rumor(self.rumor)
        self.rumor.add_spread_agent(initial_agent.agent_id)

        for _ in range(num_iterations):
            spread_agent = self.network.get_random_agent()
            spread_agent.spread_rumor(self.rumor,self.network.agents)
            self.rumor.add_spread_agent(spread_agent.agent_id)


class Main:
    def __init__(self):
        self.network = Network()
        self.create_agents()
        self.rumor = Rumor(rumor_id=1, initial_agent_id=1)
        self.simulation = Simulation(self.network, self.rumor)

    def create_agents(self):
        self.network.add_agent(agent_id=1, neighbors=[2, 3])
        self.network.add_agent(agent_id=2, neighbors=[1, 3, 4])
        self.network.add_agent(agent_id=3, neighbors=[1, 2, 4])
        self.network.add_agent(agent_id=4, neighbors=[2, 3])

    def run_simulation(self):
        num_iterations = 10
        self.simulation.run(num_iterations)
        self.print_rumor_spread()

    def print_rumor_spread(self):
        spread_agents = self.rumor.spread_agents
        print("Rumor spread to the following agents:")
        for agent_id in spread_agents:
            print(f"Agent {agent_id}")

if __name__ == "__main__":
    main = Main()
    main.run_simulation()

