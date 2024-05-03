# the war among different countries
import random
import matplotlib.pyplot as plt

class Country:
    def __init__(self, name, population, resources, economy):
        self.name = name
        self.population = population
        self.resources = resources
        self.economy = economy

    def calculate_power(self):
        return self.resources * self.economy

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

            if power1 > power2:
                country1.resources += country2.resources
                country1.population += country2.population
                self.countries.remove(country2)
            else:
                country2.resources += country1.resources
                country2.population += country1.population
                self.countries.remove(country1)

    def plot_results(self):
        resources = [country.resources for country in self.countries]
        population = [country.population for country in self.countries]

        plt.bar(range(len(self.countries)), resources, align='center', alpha=0.5)
        plt.xticks(range(len(self.countries)), [country.name for country in self.countries])
        plt.xlabel('Country')
        plt.ylabel('Resources')
        plt.title('Resources Distribution')
        plt.show()

        plt.bar(range(len(self.countries)), population, align='center', alpha=0.5)
        plt.xticks(range(len(self.countries)), [country.name for country in self.countries])
        plt.xlabel('Country')
        plt.ylabel('Population')
        plt.title('Population Distribution')
        plt.show()

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