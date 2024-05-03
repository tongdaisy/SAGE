#duplicitous spread of a deep fake videos through a social network, through the lens of gender and race.
#mesa

import time, enum, math
import numpy as np
import pandas as pd
import pylab as plt
import random as random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import json
import networkx as nx


def gen_probs(catego):
    """
    Catego can be:
      - all_equals
      - male_has_core_periphery
    """
    if catego == 'all_equals':
        sizes = [75, 75, 75, 75]
        probs = [[0.2, 0.001, 0.001, 0.001],
                 [0.001, 0.2, 0.001, 0.001],
                 [0.001, 0.001, 0.2, 0.001],
                 [0.001, 0.001, 0.001, 0.2]]
    elif catego == 'male_has_core_periphery':
        sizes = [40, 20, 80, 80, 80]
        probs = [[0.3, 0.01, 0.001, 0.001, 0.001],
                 [0.01, 0.2, 0.001, 0.001, 0.001],
                 [0.001, 0.001, 0.2, 0.001, 0.001],
                 [0.001, 0.001, 0.001, 0.2, 0.001],
                 [0.001, 0.001, 0.001, 0.001, 0.2]]
    elif catego == 'white_mainstream':
        sizes = [120, 120, 30, 30]
        probs = [[0.3, 0.05, 0.001, 0.001],
                 [0.05, 0.3, 0.001, 0.001],
                 [0.001, 0.001, 0.2, 0.001],
                 [0.001, 0.001, 0.001, 0.2]]

    return sizes, probs
class Belief_State(enum.IntEnum):
    DUPED = 0
    NEUTRAL = 1
    INFORMED = 2
    NAIVE = 3
class Race(enum.IntEnum):
    WHITE = 0
    NONWHITE = 1
class Gender(enum.IntEnum):
    FEMALE = 0
    MALE = 1
    NONBINARY = 2
class MyAgent(Agent):
    """ An agent in an epidemic model."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        #self.age = int(self.random.normalvariate(20,40))
        self.gender = (Gender)(np.random.choice([Gender.FEMALE, Gender.MALE, Gender.NONBINARY], p=[0.45, 0.45, 0.1]))
        self.race = (Race)(np.random.choice([Race.WHITE, Race.NONWHITE], p=[0.8, 0.2]))
        self.belief_state = Belief_State.NAIVE
        self.videoGender = model.videoGender
        self.videoRace = model.videoRace
        #self.infection_time = 0

    def move(self):
        """Move the agent"""

        possible_steps = [node for node in self.model.grid.get_neighbors(self.pos, include_center=False)
        # if self.model.grid.is_cell_empty(node)          #THIS MAKES IT SO IT DOESN'T MOVE SINCE NETWORK IS FULL, TAKE IT OUT AND THEY MOVE
        ]
        if len(possible_steps) > 0:
            new_position = self.random.choice(possible_steps)                 
            self.model.grid.move_agent(self, new_position)       


    def contact(self):
        """post video and see if anyone watches it, then change their belief_state if they did"""
        # if self.belief_state == Belief_State.DUPED: REMOVE THIS FOR NOW?
        neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
        # naive_neighbors = [
        #     agent
        #     for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
        #     if agent.belief_state is Belief_State.NAIVE
        # ]
        neighbors = [
            agent
            for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
        ]
        #should this be self.random.random
        for a in neighbors:
            finalPDuped = model.pDuped
            #if the neighbor watches the video (again):
            if a.belief_state == Belief_State.DUPED:
                finalPDuped *= model.pStayDuped
            #elif a.belief_state == Belief_State.NEUTRAL:
                #do nothing, prob of becoming duped on second watch stays the same
            elif a.belief_state == Belief_State.INFORMED:
                finalPDuped *= model.pStayInformed
            if (random.random() < model.pWatch) and (model.flags < model.flagsThreshold):
                #if gender of neighbor matches gender of video
                if a.gender == self.videoGender:
                    finalPDuped = model.pDuped * model.genderMatchMult
                #if race of neighbor matches race of video
                if a.race == self.videoRace:
                    finalPDuped *= model.raceMatchMult
                
                if random.random() < finalPDuped:
                    a.belief_state = Belief_State.DUPED
                else:
                    if random.random() < model.pNeutral:
                        #become neutral
                        a.belief_state = Belief_State.NEUTRAL
                    else:
                        a.belief_state = Belief_State.INFORMED
                        if random.random() < model.pFlag:
                            model.flags += 1
            #else: they stay whatever state they were before
      
    def step(self):
        #self.status()
        self.move()
        self.contact()
        
    def toJSON(self):        
        d = self.unique_id
        return json.dumps(d, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


def get_flags(model):
  return(model.flags)
def get_network (model):
  return(model.G)
class DeepFakeSpreadModel(Model):
    """A model for DeepFake spread in a social network"""
    def __init__(self, N=10, pDuped=0.5, pWatch=.01, pNeutral = 0.2, 
                 avg_node_degree=3, genderMatchMult = .1, raceMatchMult = .1, 
                 initialDupedProb = 0.01, pStayDuped = 1.5, pStayInformed = .5,
                 flags=0, flagsThreshold = 1000, pFlag = 0.03, pref_attach_edges=3,
                 videoGender = Gender.MALE, videoRace = Race.WHITE):

        self.initialDupedProb = initialDupedProb

        self.videoGender = videoGender
        self.videoRace = videoRace

        # pWatch is probability a neighbor watches the video. 
        self.pWatch = pWatch
        # PDuped is base probability they fall for the fake
        self.pDuped = pDuped
        # genderMatchMult is the change in pDuped if share gender with video

        #for subsequent video wathes
        self.pStayDuped = pStayDuped
        self.pStayInformed = pStayInformed


        self.genderMatchMult = genderMatchMult
        # raceMatchMult is the change in pDuped if share race with video
        self.raceMatchMult = raceMatchMult
        #pNeutral is the probability a non-duped watcher becomes neutral (or a INFORMED)
        self.pNeutral = pNeutral

        self.pFlag = pFlag
        self.flags = flags
        self.flagsThreshold = flagsThreshold

        #self.num_agents = N
        self.num_nodes = N  
        prob = avg_node_degree / self.num_nodes

        # Make the initial network. 
        # In future shoudl change this to be our actual social network?
        # self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=prob)
        sizes, probs = gen_probs('all_equals')
        self.G = nx.stochastic_block_model(sizes, probs, seed=0)
        #self.G = nx.barabasi_albert_graph(n=self.num_nodes, m=pref_attach_edges)
        self.G.remove_edges_from(list(nx.selfloop_edges(self.G)))
        self.grid = NetworkGrid(self.G)
        
        self.schedule = RandomActivation(self)
        self.running = True
        
        # Create agents
        for i, node in enumerate(self.G.nodes()):
            a = MyAgent(i+1, self)
            self.schedule.add(a)
            #add agent
            self.grid.place_agent(a, node)

            #make some agents duped at start
            duped = np.random.choice([0,1], p=[1-initialDupedProb,initialDupedProb])
            if duped == 1:
                a.belief_state = Belief_State.DUPED
            
        self.datacollector = DataCollector(model_reporters={"Flags": get_flags}, 
                                           agent_reporters={"Gender": lambda g: g.gender, "Belief_State": lambda b: b.belief_state, "Race": lambda r: r.race,
                                                            "Position": lambda a: a.pos})
        #"Belief_State": "belief_state", 
        # self.datacollector = DataCollector(model_reporters={"Flags": get_flags}, agent_reporters={"Belief_State": "belief_state"})
    
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

#RUN MODEL
pop=1000 #keep this at 1000
steps=400 #keep this at 200
st=time.time()
model = DeepFakeSpreadModel(N=pop, pDuped=1, raceMatchMult=0.6, genderMatchMult=0.6)
steps=0
for i in range(steps):
    model.step()