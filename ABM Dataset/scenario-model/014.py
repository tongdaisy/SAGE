# disease distribution

import random as rn
import sys

import matplotlib.pyplot as plt
import networkx as nx


class Agent():
    #Represents a person in the simulation

    
    def __init__(self,id,status,age,home,work,exposed_time,infected_time,recovered_time,infection_multiplier):
        #Called upon instantiation of Agent, initilaises necessary attributes
        global num_schools

        self.id=id
        self.status=status
        self.age=age
        self.home=home
        self.location=home
        self.exposed_time=exposed_time
        self.infected_time=infected_time
        self.recovered_time=recovered_time
        self.infection_multiplier=infection_multiplier

        #Assigns each person either a workplace as passed originally or a school location
        if self.age>=5 and self.age<18:
            self.work="S"+str(rn.randint(1,num_schools))
        else:
            self.work=work

        self.setStageTime()
        
    
    def setStageTime(self):
        #Calculates the time of the current status of the agent (in hours)
        if self.status=="S" or self.status=="D":
            self.current_stage_time=0
        elif self.status=="E":
            self.current_stage_time=self.exposed_time
        elif self.status=="I" or self.status=="H":
            self.current_stage_time=self.infected_time
        elif self.status=="R":
            self.current_stage_time=self.recovered_time

    
    def locate(self,time):
        #Updates the location of the agent based on their status, age and time
        global lockdown

        self.location=self.home
        if self.status=="H":
            self.location="HOSPITAL"
        elif self.age>18 and self.age<65 and time>=9 and time<=17:
            self.location=self.work
        elif self.age>=5 and self.age>18 and time>=8 and time<=15:
            self.location=self.work
        if lockdown and self.location!="HOSPITAL":
            self.location=self.home
    
    
    def updateStatus(self,infected_locations,global_infection_chance):
        #Updates the status of the agent, allows for infection spread and progression through stages
        global total_infected_per_location
        global hospitalisation_edges
        global school_edges
        global hospitalisation_calculator
        global death_calculator

        #Calculates if the agents is to become infected if they are susceptible
        if self.status=="S" and self.location in infected_locations:
            #Infection chance at schools is higher than in homes and workplaces
            if self.location[0]=="S" and rn.randint(1,100)<=global_infection_chance*self.infection_multiplier*2:
                self.status="E"
                self.setStageTime()
            #Infection calculator for homes and workplaces
            elif rn.randint(1,100)<=global_infection_chance*self.infection_multiplier:
                self.status="E"
                self.setStageTime()
                school_edges.append(tuple([self.location,self.id]))
        else:
            #Removes 1 hour from current stage time
            self.current_stage_time-=1
            #Updates the infected locations list with infected people
            if self.status=="I" or self.status=="H":
                if [self.location,self.id] not in total_infected_per_location:
                    total_infected_per_location.append([self.location,self.id])
            #Updates stage if end of current stage, accounting for branches for death and hospitalisation
            if self.current_stage_time==0:
                if self.status=="E":
                    if rn.randint(0,hospitalisation_calculator)<=self.age:
                        self.status="H"
                        hospitalisation_edges.append(tuple([self.location,"HOSPITAL"]))
                        self.location="HOSPITAL"
                    else:
                        self.status="I"
                elif self.status=="H":
                    if rn.randint(1,death_calculator)<=2:
                        self.status="D"
                    else:
                        self.status="R"
                elif self.status=="I":
                    self.status="R"
                elif self.status=="R":
                    self.status="S"
                self.setStageTime()
              
def globalStatusCheck():
    #Totals the number of people in each category allowing the graphing of disease spread each day
    global suscpetible
    global exposed
    global infected
    global recovered
    global dead
    global hospitalised

    s=0
    e=0
    i=0
    r=0
    d=0
    h=0

    for agent in agents:
        if agent.status=="S": s+=1
        elif agent.status=="E": e+=1
        elif agent.status=="I": i+=1
        elif agent.status=="R": r+=1
        elif agent.status=="D": d+=1
        elif agent.status=="H": h+=1
        
    suscpetible.append(s)
    exposed.append(e)
    infected.append(i)
    recovered.append(r)
    dead.append(d)
    hospitalised.append(h)


def locateInfected():
    #Locates the locations with infected people at time of calling
    infected_locations=[]

    for i in agents:
        if (i.status=="I" or i.status=="H") and i.location not in infected_locations:
            infected_locations.append(i.location)
    return infected_locations






def listLocations():
    #Returns a list of all locations in the simulation
    locations=[]
    for i in agents:
        if i.home not in locations:
            locations.append(i.home)
        if i.work not in locations:
            locations.append(i.work)
    locations.append("HOSPITAL")
    return(locations)

#Initialising lists and variables needed elsewhere.
#DO NOT CHANGE!
agents = []

locations = []
total_infected_per_location = []

days = 0
time = 0
lockdown = False

suscpetible = []
exposed = []
infected = []
hospitalised = []
recovered = []
dead = []

hospitalisation_edges = []
school_edges = []

#Parameters that the user can change:

#Standard settings
num_days = 100
num_agents = 2500
infection_chance = 2
start_statuses = [0.99, 0.01, 0, 0] #Decimal values representing the proportion of people at stages S,E,I,R at the start of the simulation
num_homes = 500
num_workplaces = 125
num_schools = 50
infection_multiplier_range = [1, 3]
hospitalisation_calculator = 250 #Generates a random number every hour inbetween this and 0, and if age is larger than this, the person is hospitalised
death_calculator = 10 #2 in n people will die when hospitalised

#Time spent in each stage (upper and lower bounds in hours)
time_E = [24, 72]
time_I = [72, 168]
time_R = [672, 1008]

#Lockdown settings
lockdown_days = [1, 15]

#New wave settings
second_wave_day = 60
people_infected_at_new_wave = 10

def simulation(start_statuses,num_homes,num_works, time_e, time_i, time_r, multiplier_range):

    #Runs the whole program
    global time
    global days
    global num_days
    global lockdown_days
    global lockdown
    global second_wave_day
    global agents
    global people_infected_at_new_wave

    #Sets up the enitre simulation, generating all agents, and starts the simulation
    global locations

    statuses=[]
    ages=list(range(0,105,5))
    adjusted_ages=rn.choices(ages, weights=(5,6,6,6,6,6,7,7,6,5,6,7,6,5,5,4,2,2,2,1,1),k=num_agents)

    for i in range(int(num_agents*start_statuses[0])):
        statuses.append("S")
    for i in range(int(num_agents*start_statuses[1])):
        statuses.append("E")
    for i in range(int(num_agents*start_statuses[2])):
        statuses.append("I")
    for i in range(int(num_agents*start_statuses[3])):
        statuses.append("R")

    rn.shuffle(statuses)

    for i in range(num_agents):
        agents.append(Agent(i,statuses[i],adjusted_ages[i],
            "H"+str(rn.randint(1,num_homes)),"W"+str(rn.randint(1,num_works)),
            rn.randint(time_e[0],time_e[1]),rn.randint(time_i[0],time_i[1]),rn.randint(time_r[0],time_r[1]),
            rn.randint(multiplier_range[0],multiplier_range[1])))
    
    locations=listLocations()

    while days<num_days:
        infected_locations=locateInfected()
        for i in agents:
            i.locate(time)
            i.updateStatus(infected_locations,infection_chance)
        time+=1
        #Calculates special time cases such as lockdown or new waves or infection
        if time==24:
            time=0
            days+=1
            progress = days / num_days
            if lockdown_days[0]==days: 
                lockdown=True
            if lockdown_days[1]==days: 
                lockdown=False
            if second_wave_day==days: 
                people=list(rn.choices(agents,k=people_infected_at_new_wave))
                for i in people:
                    i.status="E"
                    i.current_stage_time = i.exposed_time

            globalStatusCheck()


#Calls the setup
#simulation(start_statuses,num_homes,num_workplaces, time_E, time_I, time_R, infection_multiplier_range)