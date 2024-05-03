#Spread of virus
import random


class Person:
    def __init__(self, x, y, infected=False,immune=False):
        self.x = x
        self.y = y
        self.infected = infected
        self.immune = immune
        self.days_infected = 0
        self.in_hospital=False

    def move(self):
        self.x += random.randint(-2, 2)
        self.y += random.randint(-2, 2)

    def infect(self, virus):
        if not self.immune:
            self.infected = True
            self.days_infected = 0
            self.virus = virus

    def update(self):
        if self.infected:
            self.days_infected += 1
            if self.days_infected >= self.virus.recovery_day:
                self.infected = False
                self.immune = True

    def is_infected(self):
        return self.infected

    def is_immune(self):
        return self.immune


class Government:
    def __init__(self, population_size, virus, infection_rate):
        self.population_size = population_size
        self.virus = virus
        self.infection_rate = infection_rate
        self.people = []

    def create_population(self):
        width = int(self.population_size ** 0.5) * 2
        for i in range(width):
            for j in range(width):
                a = random.uniform(0, 1)
                if a <= 0.25:
                    p = Person(i, j)
                    self.people.append(p)

        # Infect a random person
        random_person = random.choice(self.people)
        random_person.infect(self.virus)

    def simulate_spread(self, day):
        infected_count = 0
        for person in self.people:
            person.move()
            person.update()

            if person.is_infected():
                infected_count += 1
            if person.is_infected():
                # Check if person infects others
                for other_person in self.people:
                    if person != other_person and not other_person.is_infected():
                        distance = ((person.x - other_person.x) ** 2 + (person.y - other_person.y) ** 2) ** 0.5
                        if distance <= self.virus.spread_distance and random.random() < self.infection_rate:
                            other_person.infect(self.virus)

        print(f"Day {day}: Infected count: {infected_count}")
        return infected_count

class Hospital:
    def __init__(self, capacity):
        self.capacity = capacity
        self.patients = []

    def admit_patient(self, person):
        if len(self.patients) < self.capacity and person.in_hospital==False:
            self.patients.append(person)
            person.in_hospital=True

    def treat_patient(self):
        for p in self.patients:
            if p.infected:
                p.days_infected += 2


class Virus:
    def __init__(self, recovery_day, spread_distance):
        self.recovery_day = recovery_day
        self.spread_distance = spread_distance


def simulation(population_size=100, infection_rate=0.2, recovery_day=5, simulation_days=20, hospital_capacity=10,
               spread_distance=3):
    random.seed(100)
    # Create government, hospital, and virus objects
    virus = Virus(recovery_day, spread_distance)
    government = Government(population_size, virus, infection_rate)
    hospital = Hospital(hospital_capacity)

    # Create population and simulate spread
    government.create_population()
    for day in range(simulation_days):
        final_infect=government.simulate_spread(day)
        # Admit infected people to the hospital
        for person in government.people:
            if person.is_infected():
                hospital.admit_patient(person)
        hospital.treat_patient()

    return final_infect

final_infect=simulation()
print(final_infect)
