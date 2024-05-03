#arctic ecology

from abc import ABC, abstractmethod
from matplotlib.colors import ListedColormap
from random import randint, uniform
from matplotlib import gridspec
import numpy as np
from pylab import *
import matplotlib
from random import random, uniform, choice, shuffle
from numpy.random import exponential



class Animal(ABC):
    seasons = {'winter': 0, 'spring': 122, 'summer': 183, 'autumn': 304}

    def __init__(self, gender, age, probability_death, probability_birth,
                 movement_speed, hunger, radius, weaning, mating, parents, pregnancy):
        self.gender = gender
        self.age = age
        self.probability_death = probability_death
        self.probability_birth = probability_birth
        self.movement_speed = movement_speed
        self.hunger = hunger
        self.radius = radius
        self.radius_sq = self.radius ** 2
        self.weaning = weaning
        self.mating = mating[gender]
        self.parents = parents
        self.isPregnant = False
        self.daysSpentInPregnancy = None
        self.pregnancy = randint(pregnancy[0], pregnancy[1])
        self.partner = None
        self.children = []
        self.isInDen = None

    @abstractmethod
    def check_death(self):
        pass

    @abstractmethod
    def check_birth(self):
        pass

    @abstractmethod
    def move(self):
        pass

    def restrict(self, n, min_, max_):
        n = max(min(max_, n), min_)
        if n == 100:
            n -= uniform(0, self.movement_speed)
        elif n == 0:
            n += uniform(0, self.movement_speed)
        return n

    @abstractmethod
    def give_birth(self):
        pass




class PolarBear(Animal):
    count = 0
    initial_population = 8
    capacity = 16

    def __init__(self, gender, parents, age=2555, hunger=0.1):
        super().__init__(gender=gender,
                         age=age,
                         probability_death=0.1 * hunger,
                         probability_birth=0.1,
                         movement_speed=10,
                         hunger=hunger,
                         radius=30,
                         weaning=912.5,
                         mating={'m': 1825, 'f': 1460},
                         parents=parents,
                         pregnancy=[195, 265]
                         )
        self.x = uniform(0, 100)
        self.y = uniform(20, 40)
        self.uid = PolarBear.count
        PolarBear.count += 1

    def check_death(self, agents, neighbours):
        if self.isInDen:
            return False
        random_val = random()

        if len(neighbours) == 0 and random_val < self.probability_death and self.age > self.weaning:
            deaths = []
            deaths.append(self)
            PolarBear.count -= 1
            for child in self.children:
                if child.age < child.weaning:
                    deaths.append(child)
                    PolarBear.count -= 1
            return deaths
        return False

    def give_birth(self, chosen):
        if self.gender == 'f':
            female = self
            male = chosen
        else:
            female = chosen
            male = self
        parents = {
            'f': female,
            'm': male
        }
        numChildren = 0
        random_val = random()
        childrenList = []
        if random_val <= 0.85:
            numChildren = choice([1, 2])
        elif random_val <= 0.98:
            numChildren = 3
        else:
            numChildren = 4
        for i in range(numChildren):
            child = PolarBear(choice(['f', 'm']), parents, 0)
            self.children.append(child)
            childrenList.append(child)
        self.isPregnant = False
        return childrenList

    def check_birth(self, agents, same_neighbours, day):
        if day < self.seasons['spring'] or day > self.seasons['summer']:
            return False
        if self.age > self.mating:
            if len(same_neighbours) > 0 and random() < self.probability_birth * (
                    1 - PolarBear.count / PolarBear.capacity):
                opp_gender = [ag for ag in same_neighbours if ag.gender !=
                              self.gender and not ag.isPregnant and ag.age > ag.weaning]
                for i in opp_gender:
                    hasWeaningChildren = False
                    if len(i.children) != 0:
                        for j in i.children:
                            if j.age < j.weaning:
                                hasWeaningChildren = True
                                break
                    if hasWeaningChildren:
                        opp_gender.remove(i)
                if len(opp_gender) == 0:
                    return False
                chosen = choice(opp_gender)
                if self.gender == 'f':
                    self.isPregnant = True
                    self.daysSpentInPregnancy = 0
                # self.probability_death-=0.9*self.probability_death
                else:
                    chosen.isPregnant = True
                    chosen.daysSpentInPregnancy = 0
                self.partner = chosen
                return True
        return False

    def move(self, agents, day):
        if self.isPregnant and (day > self.seasons['autumn'] or day < self.seasons['spring']):
            if not self.isInDen:
                self.find_den()
            return
        if self.age > self.weaning:
            name = 'PolarBear'
            neighbours_vector = []
            neighbours_dist = []
            for nb in agents:
                if type(nb).__name__ != name:
                    neighbours_vector.append([nb.x - self.x, nb.y - self.y])
                    neighbours_dist.append(
                        neighbours_vector[-1][0] ** 2 + neighbours_vector[-1][1] ** 2)
                    if neighbours_dist[-1] >= self.radius_sq:
                        neighbours_vector.pop(-1)
                        neighbours_dist.pop(-1)
            if len(neighbours_vector) > 0:
                neighbours_vector = np.array(neighbours_vector)
                neigbours_dist = np.array(neighbours_dist)
                for i in range(len(neighbours_vector)):
                    neighbours_vector[i] = (neighbours_vector[i] * self.movement_speed *
                                            (1 - neighbours_dist[i] / self.radius_sq)) / (neighbours_dist[i] ** 0.5)
                final_vector = np.sum(
                    neighbours_vector, axis=0) / len(neighbours_vector)
                if day > self.seasons['summer']:
                    self.x += final_vector[0] * min(self.hunger, 1)
                    self.y += final_vector[1] * min(self.hunger, 1)
                else:
                    self.x += final_vector[0]
                    self.y += final_vector[1]
            if day > self.seasons['summer']:
                self.x += uniform(-self.movement_speed // 2,
                                  self.movement_speed // 2)
                self.y -= uniform(0, self.movement_speed // 2)
            elif self.gender == 'f' and not self.isPregnant or self.gender == 'm':
                if len(neighbours_vector) == 0:
                    self.x += uniform(-self.movement_speed,
                                      self.movement_speed)
                    self.y += uniform(-self.movement_speed,
                                      self.movement_speed)
            self.x = self.restrict(self.x, 0, 100)
            self.y = self.restrict(self.y, 0, 100)
        else:
            self.x = self.parents['f'].x + uniform(-2, 2)
            self.y = self.parents['f'].y + uniform(-2, 2)

    def find_den(self):
        move_val = self.movement_speed // 2 + random()
        self.y = self.restrict(self.y - uniform(0, move_val), 0, 100)
        self.x = self.restrict(
            self.x + uniform(-self.movement_speed // 2, self.movement_speed // 2), 0, 100)
        if self.y < 25:
            self.isInDen = True


class RingedSeal(Animal):
    count = 0
    initial_population = 400
    capacity = 600

    def __init__(self, gender, parents, age=2555):
        super().__init__(gender=gender,
                         age=age,
                         probability_death=0.15,
                         probability_birth=0.3,
                         movement_speed=0.5,
                         hunger=0,
                         radius=30,
                         weaning=42,
                         mating={'m': 1825, 'f': 1095},
                         parents=parents,
                         pregnancy=[269, 271])
        self.x = uniform(0, 100)
        self.y = self.restrict(100 - exponential(1.65) * 15, 0, 100)
        self.uid = RingedSeal.count
        RingedSeal.count += 1

    def check_death(self, agents, neighbours):
        if len(neighbours) > 0 and random() < self.probability_death and self.age > self.weaning:
            temp_neighbours = [
                i for i in neighbours if i.age > i.weaning]
            shuffle(temp_neighbours)
            temp_uid = 0
            temp = 0
            for i in temp_neighbours:
                if i.hunger > 0.7:
                    i.hunger = 0.1
                    i.probability_death = (i.hunger) + (i.age) / 1000
                    deaths = []
                    deaths.append(self)
                    RingedSeal.count -= 1
                    for child in self.children:
                        if child.age < child.weaning:
                            deaths.append(child)
                            RingedSeal.count -= 1
                    return deaths
        return False

    def give_birth(self, chosen):
        if self.gender == 'f':
            female = self
            male = chosen
        else:
            female = chosen
            male = self
        parents = {
            'm': male,
            'f': female
        }
        child = RingedSeal(choice(['f', 'm']), parents, 0)
        self.children.append(child)
        self.isPregnant = False
        return [child]

    def check_birth(self, agents, same_neighbours, day):
        if day < 130 or day > self.seasons['autumn']:
            return False
        if self.age > self.mating:
            if len(same_neighbours) > 0 and random() < self.probability_birth * (
                    1 - RingedSeal.count / RingedSeal.capacity):
                opp_gender = [ag for ag in same_neighbours if ag.gender !=
                              self.gender and not ag.isPregnant and ag.age > ag.weaning]
                for i in opp_gender:
                    hasWeaningChildren = False
                    if len(i.children) != 0:
                        for j in i.children:
                            if j.age < j.weaning:
                                hasWeaningChildren = True
                                break
                    if hasWeaningChildren:
                        opp_gender.remove(i)
                if len(opp_gender) == 0:
                    return False
                chosen = choice(opp_gender)
                if self.gender == 'f':
                    self.isPregnant = True
                    self.daysSpentInPregnancy = 0
                else:
                    chosen.isPregnant = True
                    chosen.daysSpentInPregnancy = 0
                self.partner = chosen
                return True
        return False

    def move(self, agents, day):
        if self.age > self.weaning:
            self.x = self.restrict(
                self.x + uniform(-self.movement_speed, self.movement_speed), 0, 100)
            self.y = self.restrict(
                self.y + uniform(-self.movement_speed, self.movement_speed), 0, 100)
        else:
            self.x = self.parents['f'].x + uniform(-2, 2)
            self.y = self.parents['f'].y + uniform(-2, 2)





matplotlib.use('TkAgg')
spec = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=[3, 1])
cumulative_population = {'PolarBear': [0], 'RingedSeal': [0]}


def initialize():
    global env, agents
    # env = np.vstack((np.zeros((75, 101)), np.ones((26, 101))))
    env = [[None for j in range(100)] for i in range(100)]
    for i in range(100):
        for j in range(100):
            env[i][j] = i
    agents = []
    parents = {
        'm': "Initialized",
        'f': "Initialized"
    }
    for i in range(PolarBear.initial_population // 2):
        agents.append(PolarBear('m', parents))
        agents.append(PolarBear('f', parents))
    for i in range(RingedSeal.initial_population // 2):
        agents.append(RingedSeal('m', parents))
        agents.append(RingedSeal('f', parents))


spec = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=[3, 1])


def update(ag):
    global agents
    name = type(ag).__name__
    neighbours = [nb for nb in agents if type(nb).__name__ != name and
                  (ag.x - nb.x) ** 2 + (ag.y - nb.y) ** 2 < ag.radius_sq]
    same_neighbours = [nb for nb in agents if type(nb).__name__ == name and
                       (ag.x - nb.x) ** 2 + (ag.y - nb.y) ** 2 < ag.radius_sq]
    deaths = ag.check_death(agents, neighbours)
    if deaths != False:
        for death in deaths:
            agents.remove(death)
        return True
    if not ag.isPregnant:
        ag.check_birth(agents, same_neighbours, day)
    else:
        if ag.daysSpentInPregnancy < ag.pregnancy:
            ag.daysSpentInPregnancy += 1
        else:
            childrenList = ag.give_birth(ag.partner)
            for i in childrenList:
                agents.append(i)
            ag.partner = None
            ag.daysSpentInPregnancy = None

    ag.age += 1
    if type(ag).__name__ == "PolarBear" and not ag.isPregnant:
        if 180 <= day <= 300:
            ag.hunger += 0.01
            ag.probability_death += ((ag.hunger) + (ag.age) / 1000)
        else:
            ag.hunger += 0.1
            ag.probability_death += ((ag.hunger) + (ag.age) / 1000)
        # print(img_count, ag.hunger)

        if type(ag).__name__ == "PolarBear" and ag.age >= 9125:
            ag.probability_death = 0.8
    return False


def update_one_unit_time():
    global agents, days
    for ag in agents:
        ag.move(agents, day)
        print(ag.x)

    i = 0
    while i < len(agents):
        if not update(agents[i]):
            i += 1

if __name__ == "__main__":
    img_count = 0
    day = 0
    blue = cm.get_cmap('Blues', 100)
    cm.register_cmap(name='ice', cmap=ListedColormap(
        [blue(i) for i in range(3)] + [blue(35)]))
    #matplotlib.rcParams['image.cmap'] = 'ice'

