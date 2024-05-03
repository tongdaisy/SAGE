# SIR model #

import random
import matplotlib.pyplot as plt

## Define parameters

probTrans = 0.3
probRecover = 0.1
initNmS = 8 * 100
initNmI = 2 * 100
numDays = 500


## Define Agent class

class Agent():
    # Constructor
    def __init__(self, health='S'):
        self.health = health  # by default, he is subseceptible

    # A method to update an agent's health
    def health_update(self):
        if self.health == 'S':
            opponent = random.choice(listAllAgents)  # randomly meet another agent
            if opponent.health == 'I':  # if opponent is infected
                if random.uniform(0, 1) < probTrans:
                    self.health = 'I'  # get infected
        elif self.health == 'I':
            if random.uniform(0, 1) < probRecover:
                self.health = 'S'  # get recovered


## Prepare some other functions

### Generate a list of agents' health from the list of agents
def list_healths(listAgents):
    return ([agent.health for agent in listAgents])


### Calculate the proportion of each health from a list of agents
def count_prop(listAgents):
    listHealth = list_healths(listAgents)
    return listHealth.count('S') / len(listAgents), listHealth.count('I') / len(listAgents)

def simulation():
    ## Initial state & run simulation
    listAllAgents = [Agent('S') for i in range(initNmS)] + [Agent('I') for i in range(initNmI)]
    histPropS = []
    histPropI = []

    propS, propI = count_prop(listAllAgents)
    histPropS.append(propS)
    histPropI.append(propI)

    numDays = 1
    ## Run simulation
    for day in range(numDays):
        for agent in listAllAgents:
            agent.health_update()
        propS, propI = count_prop(listAllAgents)
        histPropS.append(propS)
        histPropI.append(propI)

#simulation()
