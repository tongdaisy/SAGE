# Spread of virus
import random


class Person:
    def __init__(self, x, y, infected=False, immune=False):
        self.x = x
        self.y = y
        self.infected = infected
        self.immune = immune
        self.days_infected = 0
        self.in_hospital = False

    def move(self):
        self.x += random.randint(-2, 2)
        self.y += random.randint(-2, 2)

    def infect(self, virus):
        if not self.immune:
            self.infected = True
            self.days_infected = 0
            self.virus = virus
            return 1
        return 0

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
        new_infect = 0
        for person in self.people:
            person.move()
            person.update()
            if person.is_infected():
                # Check if person infects others
                for other_person in self.people:
                    if person != other_person and not other_person.is_infected():
                        distance = ((person.x - other_person.x) ** 2 + (person.y - other_person.y) ** 2) ** 0.5
                        if distance <= self.virus.spread_distance and random.random() < self.infection_rate:
                            new_infect += other_person.infect(self.virus)

        print(f"Day {day}: new Infected count: {new_infect}")
        return new_infect


class Hospital:
    def __init__(self, capacity):
        self.capacity = capacity
        self.patients = []

    def admit_patient(self, people):
        new_treat = 0
        for person in people:
            if person.is_infected():
                if len(self.patients) < self.capacity and person.in_hospital == False:
                    self.patients.append(person)
                    person.in_hospital = True
                    new_treat += 1
            if len(self.patients) == self.capacity:
                break
        return new_treat

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
    treatment_num = 0
    # Create population and simulate spread
    government.create_population()
    new_infect_max = 0
    for day in range(simulation_days):
        new_infect = government.simulate_spread(day)
        # Admit infected people to the hospital
        new_treat = hospital.admit_patient(government.people)
        treatment_num += new_treat
        hospital.treat_patient()
        if day>=1 and new_infect > new_infect_max:
            new_infect_max = new_infect
    max_spread_rate = new_infect_max / len(government.people)
    return max_spread_rate


max_spread_rate = simulation()
print(max_spread_rate)
