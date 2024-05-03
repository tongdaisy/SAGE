# Spread of virus
import random


class Person:
    def __init__(self, x, y, infected=False, immune=False, wearing_mask=False):
        self.x = x
        self.y = y
        self.infected = infected
        self.immune = immune
        self.days_infected = 0
        self.in_hospital = False
        self.wearing_mask = wearing_mask
        self.quarantined = False
        self.is_employed = True
        self.salary = 1 * random.uniform(0.5, 1.5)

    def move(self):
        self.x += random.randint(-2, 2)
        self.y += random.randint(-2, 2)

    def infect(self, virus):
        if not self.immune:
            self.infected = True
            self.days_infected = 0
            self.virus = virus
            # Assume infected people are unable to work
            self.is_employed = False
            return 1
        return 0

    def update(self):
        if self.infected:
            self.days_infected += 1
            if self.days_infected >= self.virus.recovery_day:
                self.infected = False
                self.immune = True
                # Assume recovered people can work again
                self.is_employed = True

    def is_infected(self):
        return self.infected

    def is_immune(self):
        return self.immune

    def is_employed(self):
        return self.is_employed


class Government:
    def __init__(self, population_size, virus, infection_rate, mask_wearing_rate, quarantine_rate):
        self.population_size = population_size
        self.virus = virus
        self.infection_rate = infection_rate
        self.people = []
        self.manual_productivity = 1.0
        self.NDI = 0.0
        self.GDP = 0.0
        self.mask_wearing_rate = mask_wearing_rate
        self.quarantine_rate = quarantine_rate

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
                        if not other_person.quarantined and not other_person.wearing_mask:
                            distance = ((person.x - other_person.x) ** 2 + (person.y - other_person.y) ** 2) ** 0.5
                            if distance <= self.virus.spread_distance and random.random() < self.infection_rate:
                                new_infect += other_person.infect(self.virus)

        print(f"Day {day}: new Infected count: {new_infect}")
        self.calculate_GDP()
        self.calculate_NDI()
        return new_infect

    def enforce_quarantine(self, quarantine_percentage):
        quarantine_count = int(self.population_size * quarantine_percentage)
        quarantined_people = random.sample(self.people, quarantine_count)
        for person in quarantined_people:
            person.quarantined = True

    def enforce_wearing_mask(self):
        num_wear_mask = int(self.population_size * self.mask_wearing_rate)
        masking_people = random.sample(self.people, num_wear_mask)
        for person in masking_people:
            person.wearing_mask = True


    def calculate_NDI(self):
        self.NDI = sum(person.is_employed * person.salary for person in self.people) / len(self.people)
        return self.NDI

    def calculate_GDP(self):
        self.GDP = sum(person.is_employed * self.manual_productivity for person in self.people) / len(self.people)
        return self.GDP


class Vaccination:
    def __init__(self, vaccine_efficacy, vaccination_rate, government,safe_immune_rate):
        self.vaccine_efficacy = vaccine_efficacy
        self.vaccination_rate = vaccination_rate
        self.government = government
        self.immune_rate=safe_immune_rate

    def apply_vaccination(self, people):
        immune_rate=len([p for p in people if p.immune])/len(people)
        if immune_rate>self.immune_rate:
            return
        # spend healthy care money of the government
        self.government.GDP *= 0.95
        vaccinated_count = int(len(people) * self.vaccination_rate)
        vaccinated_people = random.sample(people, vaccinated_count)
        for person in vaccinated_people:
            if not person.is_infected() and not person.is_immune():
                if random.random() < self.vaccine_efficacy:
                    person.immune = True


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
               spread_distance=4, mask_wearing_rate=0.2, quarantine_rate=0.2,
               vaccine_efficacy=0.9, vaccination_rate=0.2,safe_immune_rate=0.8):
    random.seed(30)
    # Create government, hospital, and virus objects
    virus = Virus(recovery_day, spread_distance)
    government = Government(population_size, virus, infection_rate, mask_wearing_rate, quarantine_rate)
    hospital = Hospital(hospital_capacity)
    vaccination = Vaccination(vaccine_efficacy, vaccination_rate,government,safe_immune_rate)
    treatment_num = 0
    # Create population and simulate spread
    government.create_population()
    original_GDP = government.calculate_GDP()
    original_NDI = government.calculate_NDI()
    total_GDP = 0
    total_NDI = 0
    for day in range(simulation_days):
        government.simulate_spread(day)
        # Admit infected people to the hospital
        hospital.admit_patient(government.people)
        hospital.treat_patient()
        vaccination.apply_vaccination(government.people)
        government.enforce_quarantine(quarantine_rate)
        government.enforce_wearing_mask()
        total_GDP += government.GDP
        total_NDI += government.NDI
    GDP_decrease_ratio = (original_GDP - total_GDP / simulation_days) / original_GDP
    NDI_decrease_ratio = (original_NDI - total_NDI / simulation_days) / original_NDI
    return GDP_decrease_ratio, NDI_decrease_ratio


GDP_decrease_ratio,NDI_decrease_ratio = simulation()
print(GDP_decrease_ratio,NDI_decrease_ratio)
