# the spread of covid and the prevent process; 



import random
# Classes
class Virus:
    def __init__(self, transmission_rate, mortality_rate):
        self.transmission_rate = transmission_rate
        self.mortality_rate = mortality_rate

    def transmit(self, person):
        if random.random() < self.transmission_rate:
            person.infect(self)

    def kill(self, person):
        if random.random() < self.mortality_rate:
            person.die()

class Person:
    def __init__(self, id, is_infected=False, is_dead=False):
        self.id = id
        self.is_infected = is_infected
        self.is_dead = is_dead

    def infect(self, virus):
        if not self.is_dead:
            self.is_infected = True
            virus.kill(self)

    def die(self):
        self.is_dead = True

    def is_alive(self):
        return not self.is_dead

class Hospital:
    def __init__(self, capacity):
        self.capacity = capacity
        self.patients = []

    def admit(self, person):
        if len(self.patients) < self.capacity:
            self.patients.append(person)
        else:
            print("Hospital is at full capacity")

    def discharge(self, person):
        self.patients.remove(person)

class Government:
    def __init__(self):
        self.lockdown = False

    def impose_lockdown(self):
        self.lockdown = True

    def lift_lockdown(self):
        self.lockdown = False

# Simulation function
def simulation(num_people, transmission_rate, mortality_rate, num_iterations):
    people = [Person(id) for id in range(num_people)]
    virus = Virus(transmission_rate, mortality_rate)
    hospital = Hospital(10)
    government = Government()

    # Infect one random person
    initial_infected = random.choice(people)
    initial_infected.infect(virus)

    for _ in range(num_iterations):
        # Transmit disease
        for person in people:
            if person.is_alive() and not person.is_infected and not person.is_dead:
                virus.transmit(person)

        # Hospitalization
        for person in people:
            if person.is_alive() and person.is_infected and not person.is_dead:
                hospital.admit(person)

        # Print the number of infected people in each iteration
        num_infected = sum(person.is_infected and person.is_alive() for person in people)
        print(f"Iteration {_ + 1}: {num_infected} people infected")

# Example usage
#simulation(num_people=100, transmission_rate=0.1, mortality_rate=0.05, num_iterations=10)