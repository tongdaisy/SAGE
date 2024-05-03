# the war among different countries
import random

class Country:
    def __init__(self, name, population, resources, economy):
        self.name = name
        self.population = population
        self.resources = resources
        self.economy = economy
        self.alliance = None

    def calculate_power(self):
        return self.resources * self.economy

    def form_alliance(self, alliance):
        if self.alliance is None:
            self.alliance = alliance
            alliance.add_member(self)

class Alliance:
    def __init__(self, name):
        self.name = name
        self.members = []

    def add_member(self, country):
        self.members.append(country)

    def calculate_power(self):
        total_power = 0
        for member in self.members:
            total_power += member.calculate_power()
        return total_power

class WarModel:
    def __init__(self, countries):
        self.countries = countries

    def simulate(self, num_iterations):
        for _ in range(num_iterations):
            if len(self.countries)>=2:
                country1, country2 = random.sample(self.countries, 2)
            else:
                break

            power1 = country1.calculate_power()
            power2 = country2.calculate_power()

            if country1.alliance and country2.alliance and country1.alliance == country2.alliance:
                alliance_power1 = country1.alliance.calculate_power()
                alliance_power2 = country2.alliance.calculate_power()
                if alliance_power1 > alliance_power2:
                    country1.alliance.add_member(country2)
                    self.countries.remove(country2)
                else:
                    country2.alliance.add_member(country1)
                    self.countries.remove(country1)
            elif power1 > power2:
                country1.resources += country2.resources
                country1.population += country2.population
                self.countries.remove(country2)
            else:
                country2.resources += country1.resources
                country2.population += country1.population
                self.countries.remove(country1)

def simulation():

    countries = [
        Country('Country1', 100, 50, 0.8),
        Country('Country2', 80, 70, 0.6),
        Country('Country3', 120, 40, 0.7),
        Country('Country4', 90, 60, 0.9),
        Country('Country1', 110, 50, 0.8),
        Country('Country2', 85, 70, 0.6),
        Country('Country3', 120, 80, 0.7),
        Country('Country4', 90, 120, 0.9)
    ]

    model = WarModel(countries)

    model.simulate(10)

simulation()