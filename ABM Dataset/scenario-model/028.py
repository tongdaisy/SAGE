#  2D voting peocess
# mesa

from mesa import Agent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random


class VoterAgent(Agent):

    def __init__(self, model, state):
        super().__init__(self,model)
        self.state=state

    def step(self) -> None:
        self.voter_model_step()

    def voter_model_step(self):
        #Pick a random neighbor and copy it's state.
        neighbors = self.model.grid.get_neighbors(self.pos,moore=False) #False here means no diagonal neighbors
        
        other = self.random.choice(neighbors)
        copied_state = other.state
            
        self.state = copied_state



class VoterModel(Model):

    def __init__(self,proportion,width,height):
        self.proportion = proportion #proportion of agents that initially have State B
        self.grid = MultiGrid(width,height,True) #True here, means periodic boundary conditions
        self.schedule = RandomActivation(self) #RandomActivation means iterate the model rules over all agents in random order every step

        self.datacollector_currents=DataCollector(
            {
                "State A": VoterModel.current_a_agents,
                "State B": VoterModel.current_b_agents,
            }
        )

        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]
            if random.random() < self.proportion:
                agent_state = 1
            else:
                agent_state = 0

            agent = VoterAgent(self, agent_state)
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
        
        self.running = True


    def step(self) :
        self.schedule.step()
        self.datacollector_currents.collect(self)
        #We want to stop the simulation if consensus is reached
        if (sum([1 for agent in self.schedule.agents if agent.state == 0]) == self.schedule.get_agent_count()):
            self.running = False
        elif (sum([1 for agent in self.schedule.agents if agent.state == 0]) == 0):
            self.running = False

    @staticmethod
    def current_a_agents(model) -> int:
        #Return the total number of agents with state A
        return sum([1 for agent in model.schedule.agents if agent.state == 0])

    @staticmethod
    def current_b_agents(model) -> int:
        #Return the total number of agents with state B
        return sum([1 for agent in model.schedule.agents if agent.state == 1])


"""
from mesa.visualization.modules import CanvasGrid,ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider

NUMBER_OF_CELLS = 40

SIZE_OF_CANVAS_IN_PIXELS_X = 400
SIZE_OF_CANVAS_IN_PIXELS_Y = 400

simulation_params = {
    "proportion":Slider(
    "State Proportion",
    0.5, #default
    0, #min
    1, #max
    0.05, #step
    description="The proportion of agents that initially have State B"
    ),

    "width": NUMBER_OF_CELLS,
    "height": NUMBER_OF_CELLS,
}


def agent_portrayal(agent):
    portrayal={"Shape":"circle","Filled":"true","r":0.8}

    if agent.state == 0:
        portrayal["Color"]="orange"
        portrayal["Layer"]=0
    else:
        portrayal["Color"]="black"
        portrayal["Layer"]=1
    return portrayal

grid=CanvasGrid(agent_portrayal,NUMBER_OF_CELLS,NUMBER_OF_CELLS,SIZE_OF_CANVAS_IN_PIXELS_X,SIZE_OF_CANVAS_IN_PIXELS_Y)

chart_currents = ChartModule(
    [
        {"Label": "State A","Color":"orange"},
        {"Label": "State B","Color":"black"},
    ],
    canvas_height=300,
    data_collector_name="datacollector_currents"
)

server = ModularServer(
    VoterModel,
    [grid,chart_currents],
    "Voter Model",
    simulation_params
)
server.port = 8521
server.launch()

"""