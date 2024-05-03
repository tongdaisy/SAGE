# Electricity Usage and Distribution Issues in Cities
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

class City:
    def __init__(self, users, government, power_plants):
        self.users = users
        self.government = government
        self.power_plants = power_plants

    def simulate(self, cycles):
        for cycle in range(cycles):
            total_demand = sum(user.demand for user in self.users)
            total_electricity = sum(power_plant.generate() for power_plant in self.power_plants)

            for user in self.users:
                user_ratio = user.demand / total_demand
                allocated_electricity = total_electricity * user_ratio
                electricity = user.consume(allocated_electricity)
                user.demand=random.randint(1, 10)

            remaining_electricity = total_electricity - sum(user.demand for user in self.users)
            remaining_electricity = self.government.regulate(remaining_electricity, total_demand)

            print("Cycle", cycle+1)
            print("Remaining electricity:", remaining_electricity)
            for user in self.users:
                print("User demand:", user.demand)
            print()

users = [User(f"Location{i}", random.randint(500, 1500)) for i in range(1, 101)]
government = Government("LocationA")
power_plants = [PowerPlant(f"LocationB{i}", random.randint(500, 1000)) for i in range(1, 11)]


city = City(users, government, power_plants)
city.simulate(10)

