#infection and testing to determine trade-offs of quantity vs. turn-around time
#mesa

from mesa import Agent, Model
from mesa.time import StagedActivation  # RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random
import math
import numpy as np



def percent_sick(model):
    sick = sum([1 if agent.ever_infected else 0 for agent in model.schedule.agents])
    return sick / model.num_agents


def num_infectious(model):
    infectious_now = sum(
        [1 if agent.infectious else 0 for agent in model.schedule.agents]
    )
    return infectious_now


def quarantined(model):
    quarantined = sum(
        [1 if agent.quarantined else 0 for agent in model.schedule.agents]
    )
    return quarantined


class Contact_Trace_Agent(Agent):  # noqa
    """
    Person, can be Susceptable, Pre-infectious, Infectious pre-symptomatic,
    Infectious asymptomatic, Infectious symptomatic, recovered immune, or recovered
    non-immune. Person has contacts/day normally distributed around a model parameter.
    Person can be tested at any time and if postivie will be quarantined and no longer
    contact other people. If contact tracing is in place, some set of recent contacts
    will be tested the next day. People have families they contact
    every day and work they contact with some percent chance every day. People
    also interact with random people at some rate.
    """

    def __init__(self, unique_id, model):
        """
        Customize the agent
        """
        self.unique_id = unique_id
        super().__init__(unique_id, model)
        self.day = 0
        self.step = 0

        self.contacts = {}

        self.family = []
        self.coworkers = []
        self.random_people = []

        self.symptomatic = False
        self.state = "susceptable"

        self.ever_infected = False

        self.incubation = 999
        self.infectious_period = 999
        self.quarantine_countdown = 999
        self.recovered = False
        self.immune = False
        self.quarantined = False

        self.infectious = False

        self.random_contacts = 0
        self.quarantine_ingorer = False

    def move(self):
        """
        Agent interacts with people based on day of week and characteristics of
        agent.
        """
        self.step += 1
        self.day += 1

        if self.day == 8:
            self.day = 1

        # if agent not quarantined or if they're ignoring it, add other agents to their
        # contact list
        if not self.quarantined or self.quarantine_ingorer:
            self.contacts[self.step] = self.family.copy()

            # get random people not in the family
            self.contacts[self.step].extend(
                random.sample(self.random_people, self.random_contacts)
            )

    def infect(self):
        """
        if agent came in contact with an infectious person, there is a chance they
        become infected
        """

        if self.state == "susceptable":
            infectious_contacts = sum(
                [
                    self.model.schedule.agents[contact].infectious
                    for contact in self.contacts[self.step]
                ]
            )

            if infectious_contacts > 0:
                self.check_sick(infectious_contacts)

        elif self.state == "pre_infectious":
            # print(f"I'm agent {self.unique_id} and I'm pre-infectious")
            self.incubation += -1
            if self.incubation == 0:
                self.state = "infectious"
                self.infectious = True

        elif self.state == "infectious":
            # print(f"I'm agent {self.unique_id} and I'm infectious")

            self.infectious_period += -1
            if self.infectious_period == 0:
                self.state = "recovered"
                self.infectious = False

        elif self.state == "awaiting_quarantine":
            self.quarantine_countdown += -1
            if self.quarantine_countdown == 0:
                print("quarantined infectious person")
                self.state = "quarantined"
                self.infectious = False
                self.quarantined = True

    def test(self):
        """
        random testing
        """

        # if the random number is below the percent tested and there are tests left
        if random.random() <= self.model.percent_tested_per_day:
            self.model.step_tests += -1

            if self.state in ["pre_infectious", "infectious"]:
                print("tested infectious person")
                self.quarantine_countdown = self.model.turn_around_time
                self.state = "awaiting_quarantine"

    def get_random_agent(self):
        return random.randrange(0, self.model.num_agents, 1,)

    def check_sick(self, infectious_contacts):
        # random number between 0-1 compared to 1 - (infection chance * number of infectous contacts in the day)
        # if the random is larger, they get sick
        # if not they're ok
        chance_sick = random.random()

        if chance_sick > (1 - (infectious_contacts * self.model.infection_chance)):
            # print(f"I'm agent {self.unique_id}, and I just got sick")
            # print(
            #    f"my chance was {1 - (infectious_contacts * self.model.infection_chance)} vs. {chance_sick}"
            # )

            self.sick = True
            self.ever_infected = True
            self.pre_infectious = True

            self.state = "pre_infectious"
            # set the incubation period to be a random number in the interval
            # definied as a model parameter
            self.incubation = random.randrange(
                self.model.incubation[0], (self.model.incubation[1]) + 1, 1
            )

            self.infectious_period = random.randrange(
                self.model.infectious_period[0],
                (self.model.infectious_period[1]) + 1,
                1,
            )
        return False


class Contact_Trace_Model(Model):
    """
    The model class holds the model-level attributes, manages the agents, and generally handles
    the global level of our model.

    There is only one model-level parameter: how many agents the model contains. When a new model
    is started, we want it to populate itself with the given number of agents.

    The scheduler is a special model component which controls the order in which agents are activated.
    """

    def __init__(
        self,
        num_agents=10,
        num_sick=1,
        infection_chance=0.1,
        incubation_period=[2, 6],
        presypmtomatic_infectious_period=[0, 3],
        infectious_period=[5, 10],
        percent_asymptomatic=0,
        immunity_percent=1,
        percent_employed_small=0.5,
        perecent_employed_medium=0.25,
        percent_employed_large=0.25,
        family_size=[0, 8],
        random_contact_mean=5,
        random_contact_sd=2,
        contact_trace_percent=0.75,
        false_positive_rate=0.1,
        false_negative_rate=0.1,
        percent_tested_per_day=0.01,
        turn_around_time=2,
    ):

        super().__init__()
        self.num_agents = num_agents

        # self.schedule = RandomActivation(self)
        self.schedule = StagedActivation(self, stage_list=["move", "infect", "test"])
        # self.grid = MultiGrid(width=width, height=height, torus=False)

        # get workplaces

        self.infection_chance = infection_chance
        self.incubation = incubation_period
        self.infectious_period = infectious_period
        self.infection_chance = infection_chance
        self.incubation_period = incubation_period
        self.presypmtomatic_infectious_period = presypmtomatic_infectious_period
        self.percent_asymptomatic = percent_asymptomatic
        self.immunity_percent = immunity_percent
        self.percent_employed_small = percent_employed_small
        self.perecent_employed_medium = perecent_employed_medium
        self.percent_employed_large = percent_employed_large
        self.family_size = family_size
        self.random_contact_mean = random_contact_mean
        self.random_contact_sd = random_contact_sd
        self.contact_trace_percent = contact_trace_percent
        self.false_positive_rate = false_positive_rate
        self.false_negative_rate = false_negative_rate
        self.percent_tested_per_day = percent_tested_per_day
        self.turn_around_time = turn_around_time

        # num_classrooms = math.ceil(num_agents / max_class_size)
        # for i in range(1, num_classrooms + 1):
        #    self.class_dict[i] = {
        #        "students": [],
        #        "count": 0,
        #        "infected": False,
        #    }

        random_contacts = np.random.normal(
            self.random_contact_mean, self.random_contact_sd, self.num_agents
        )

        family_dict = {}

        # people still available to be in a family. if this gets to 0, remaining
        # agents will have no family members (should be at end only)
        family_available = self.num_agents

        non_family = set(range(1, self.num_agents, 1))

        for i in range(self.num_agents):
            agent = Contact_Trace_Agent(i, self)

            agent.random_contacts = max(math.floor(random_contacts[i]), 0)

            if family_available <= 0:
                print(f"agent {i} has no one left to be in their family")

            # if you're in a family already, that's your family, if not generate one
            if agent.unique_id in family_dict:
                agent.family = family_dict[agent.unique_id]
            else:
                family_size = min(
                    family_available,
                    random.randrange(self.family_size[0], self.family_size[1] + 1, 1,),
                )

                family_list = []

                # grab random id in range of num_agents, if that person is not in a
                # family already, add them to list, repeat until the family is the
                # right size
                family_counter = 0
                while family_counter < family_size:
                    person = random.randrange(0, self.num_agents, 1,)

                    if person not in family_dict:
                        family_list.append(person)
                        family_counter += 1

                # now that we have the list of family members, assingn them all
                # to the family
                for f in family_list:
                    family_dict[f] = family_list

                # assign the agent's family list
                agent.family = family_list

                # remove these people from family_available
                family_available += -family_size

            agent.random_people = list(non_family - set(agent.family))

            if num_sick > 0:
                agent.sick = True
                agent.pre_infectious = True
                agent.state = "pre_infectious"
                agent.incubation = random.randrange(
                    self.incubation[0], self.incubation[1] + 1, 1
                )

                agent.infectious_period = random.randrange(
                    self.infectious_period[0], (self.infectious_period[1]) + 1, 1,
                )

                num_sick += -1

            # job_asigned = False
            # while not dining_asigned:
            #    dining_option = random.choice(list(self.dining_dict.keys()))

            #    if self.dining_dict[dining_option]["count"] < max_dining:
            #        agent.dining = dining_option
            #        self.dining_dict[dining_option]["count"] += 1
            #        dining_asigned = True
            #        break
            #    else:
            #        continue

            self.schedule.add(agent)

        self.running = True
        # self.datacollector = DataCollector(model_reporters={"Number Sick": num_sick})
        self.datacollector = DataCollector(
            model_reporters={
                "Percent Ever Sick": percent_sick,
                "Number Infectious": num_infectious,
                "Tested and Quarantined": quarantined,
            }
        )

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.step_tests = self.percent_tested_per_day * self.num_agents

        self.datacollector.collect(self)
        self.schedule.step()


"""
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

percent_sick = ChartModule([{"Label": "Percent Ever Sick", "Color": "Pink"},],)
num_infectious = ChartModule([{"Label": "Number Infectious", "Color": "Green"},],)
quarantined = ChartModule([{"Label": "Tested and Quarantined", "Color": "Blue"},],)

model_params = {
    "num_agents": UserSettableParameter("number", "Number of agents", value=1000),
    "num_sick": UserSettableParameter("number", "Number of initial sick", value=1),
    "infection_chance": UserSettableParameter(
        "slider",
        "Chance of infection from encountering infectious person",
        0.01,
        0,
        0.5,
        0.01,
    ),
    "random_contact_mean": UserSettableParameter(
        "slider", "Average number of random contacts per day", 3, 0, 25, 1
    ),
    "random_contact_sd": UserSettableParameter(
        "slider", "Standard deviation of random contacts per day", 1, 1, 5, 1
    ),
    "percent_tested_per_day": UserSettableParameter(
        "slider", "Percent of population tested each day", 0.05, 0, 1, 0.01
    ),
    "turn_around_time": UserSettableParameter(
        "slider", "Days to return test results", 2, 1, 10, 1
    ),
    "false_negative_rate": UserSettableParameter(
        "slider",
        "Percent of total tests that come back negative when agent is infected",
        0.05,
        0,
        1,
        0.01,
    ),
    "false_positive_rate": UserSettableParameter(
        "slider",
        "Percent of total tests that come back positive when agent is not infected",
        0.05,
        0,
        1,
        0.01,
    ),
}

server = ModularServer(
    Contact_Trace_Model,
    [percent_sick, num_infectious, quarantined],
    "Contact_Trace_Mesa_Model",
    model_params,
)
server.port = 8521
server.launch()


"""
