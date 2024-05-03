import random

# Objects Definition
class User:
    def __init__(self, location, income):
        self.location = location
        self.income = income
        self.demand = 0
    
    def consume(self):
        self.demand = random.randint(100, 1000)

class Government:
    def __init__(self, location):
        self.location = location
    
    def regulate(self):
        # Some logic to regulate electricity usage and distribution
        # specific code
        print(f"Government is regulating electricity usage and distribution in {self.location}")

class PowerPlant:
    def __init__(self, location, capacity):
        self.location = location
        self.capacity = capacity
    
    def generate(self):
        produced_energy = random.randint(1000, self.capacity)
        # Some logic to distribute the generated energy to the city
        # specific code
        print(f"Power plant at {self.location} is generating {produced_energy} units of electricity")

class City:
    def __init__(self):
        self.users = []
        self.government = Government(location="City Hall")
        self.power_plants = []
    
    def add_user(self, user):
        self.users.append(user)

    def add_power_plant(self, power_plant):
        self.power_plants.append(power_plant)
    
    def simulate(self):
        total_demand = sum(user.demand for user in self.users)
        total_capacity = sum(power_plant.capacity for power_plant in self.power_plants)
        
        if total_capacity < total_demand:
            print("Not enough energy supply. Government should take action.")
            self.government.regulate()
        else:
            print("Energy supply is sufficient. Power plants can generate electricity.")
            for power_plant in self.power_plants:
                power_plant.generate()

# Example Usage
city = City()

# Create users
user1 = User(location="Residential Area A", income=50000)
user2 = User(location="Residential Area B", income=60000)
user3 = User(location="Commercial Area", income=100000)
city.add_user(user1)
city.add_user(user2)
city.add_user(user3)

# Create power plants
power_plant1 = PowerPlant(location="Power Plant 1", capacity=5000)
power_plant2 = PowerPlant(location="Power Plant 2", capacity=10000)
city.add_power_plant(power_plant1)
city.add_power_plant(power_plant2)

# Simulate city's electricity usage and distribution
city.simulate()