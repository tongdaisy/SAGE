# Electricity transmission and and usage Issues in Cities
import random

class User:
    def __init__(self, location, income):
        self.location = location
        self.income = income
        self.demand = random.randint(1, 10) 

    def consume(self, electricity):
        if electricity >= self.demand:
            electricity -= self.demand
            self.demand = 0
        else:
            self.demand -= electricity
            electricity = 0
        return electricity

class Government:
    def __init__(self, location):
        self.location = location

    def regulate(self, electricity, demand):
        electricity_limit = demand * 1.2  
        if electricity > electricity_limit:
            electricity = electricity_limit
        return electricity

class PowerPlant:
    def __init__(self, location, capacity):
        self.location = location
        self.capacity = capacity

    def generate(self):
        return self.capacity

class PowerGrid:
    def __init__(self, power_plants, transmission_loss):
        self.power_plants = power_plants
        self.transmission_loss = transmission_loss

    def transmit_electricity(self):
        total_electricity = sum(power_plant.generate() for power_plant in self.power_plants)
        transmitted_electricity = total_electricity * (1 - self.transmission_loss)
        return transmitted_electricity

class City:
    def __init__(self, users, government, power_grid):
        self.users = users
        self.government = government
        self.power_grid = power_grid

    def simulate(self, cycles):
        for cycle in range(cycles):
            transmitted_electricity = self.power_grid.transmit_electricity()

            for user in self.users:
                user_ratio = user.demand / sum(user.demand for user in self.users)
                allocated_electricity = transmitted_electricity * user_ratio
                electricity = user.consume(allocated_electricity)
                user.demand = random.randint(1, 10)


            remaining_electricity = transmitted_electricity - sum(user.demand for user in self.users)
            remaining_electricity = self.government.regulate(remaining_electricity, sum(user.demand for user in self.users))

            print("Cycle", cycle+1)
            print("Transmitted electricity:", transmitted_electricity)
            print("Remaining electricity:", remaining_electricity)
            for user in self.users:
                print("User demand:", user.demand)
            print()

def simulation():
    users = [User(f"Location{i}", random.randint(500, 1500)) for i in range(1, 101)]
    government = Government("LocationA")
    power_plants = [PowerPlant(f"LocationB{i}", random.randint(500, 1000)) for i in range(1, 11)]
    transmission_loss = 0.1  

    power_grid = PowerGrid(power_plants, transmission_loss)
    city = City(users, government, power_grid)
    city.simulate(10)

simulation()