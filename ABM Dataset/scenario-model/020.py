#Schelling's model


import matplotlib.pyplot as plt
import itertools
import random
import copy

def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

class Schelling:
    def __init__(self, width, height, empty_ratio, similarity_threshold, n_iterations, races=2):
        '''城市的宽和高'''
        self.width = width
        self.height = height
        '''种族数'''
        self.races = races
        '''空房子的比例'''
        self.empty_ratio = empty_ratio
        '''相似性阈值'''
        self.similarity_threshold = similarity_threshold
        '''迭代数'''
        self.n_iterations = n_iterations
        '''存储空房子坐标'''
        self.empty_houses = []
        '''存储代理人'''
        self.agents = {}

    
    def populate(self):
        '''Residents are randomly allocated on a grid'''

        
        self.all_houses = list(itertools.product(range(self.width), range(self.height))) #'''初始化房子的坐标'''
        '''将房子的顺序打乱'''
        random.shuffle(self.all_houses)
        '''空房个数'''
        self.n_empty = int(self.empty_ratio * len(self.all_houses))
        '''空房坐标'''
        self.empty_houses = self.all_houses[:self.n_empty]
        '''已经住人的房子坐标'''
        self.remaining_houses = self.all_houses[self.n_empty:]
        '''将房子均匀的分配给不同种族'''
        houses_by_race = [self.remaining_houses[i::self.races] for i in range(self.races)]
        '''为每一个种族，每一户人家初始化一个Agent'''
        for i in range(self.races):
            self.agents = Merge(dict(zip(houses_by_race[i], [i + 1] * len(houses_by_race[i]))),self.agents)

    '''判断代理人（x，y）是否满意'''
    def is_unsatisfied(self, x, y):
        '''
        Determine if the agent at (x, y) is satisfied
        The agent at (x, y) examines the proportion of neighboring agents of the same population. If it is below a threshold, return False; otherwise, return True.
        '''
        
        race = self.agents[(x, y)] #'''记录代理人（x，y）的种族'''
        '''记录代理人（x，y）周围同种族邻居的个数'''
        count_similar = 0
        '''记录代理人（x，y）周围不同种族邻居的个数'''
        count_different = 0
        '''统计周围邻居中各个种族人数'''
        if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
            if self.agents[(x - 1, y - 1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if y > 0 and (x, y - 1) not in self.empty_houses:
            if self.agents[(x, y - 1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
            if self.agents[(x + 1, y - 1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and (x - 1, y) not in self.empty_houses:
            if self.agents[(x - 1, y)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
            if self.agents[(x + 1, y)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
            if self.agents[(x - 1, y + 1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
            if self.agents[(x, y + 1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
            if self.agents[(x + 1, y + 1)] == race:
                count_similar += 1
            else:
                count_different += 1
        if (count_similar + count_different) == 0:
            return False
        else:
            return float(count_similar) / (count_similar + count_different) < self.similarity_threshold

    def update(self):
        """Check if residents on the grid are satisfied. If they are not satisfied, randomly assign them to an empty house."""
        
        for i in range(self.n_iterations):
            '''循环n_iterations次'''
            self.old_agents = copy.deepcopy(self.agents)
            '''统计搬家人数'''
            n_changes = 0

            for agent in self.old_agents:
                '''判断agent是否满意，不满意则将他随机分配到空房子中'''
                if self.is_unsatisfied(agent[0], agent[1]):
                    agent_race = self.agents[agent]
                    '''随机选择待搬入的空房子'''
                    empty_house = random.choice(self.empty_houses)
                    '''搬家后生成新的agent'''
                    self.agents[empty_house] = agent_race
                    '''删除原来的坐标，因为他搬家了'''
                    del self.agents[agent]
                    '''更新空房子列表'''
                    self.empty_houses.remove(empty_house)
                    self.empty_houses.append(agent)

                    n_changes += 1

            '''如果大家都满意，则迭代结束'''
            if n_changes == 0:
                break

    def calculate_similarity(self):
        """Calculate the average satisfaction level of all agents."""
        similarity = []
        for agent in self.agents:
            count_similar = 0
            count_different = 0
            x = agent[0]
            y = agent[1]
            race = self.agents[(x, y)]
            if x > 0 and y > 0 and (x - 1, y - 1) not in self.empty_houses:
                if self.agents[(x - 1, y - 1)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            if y > 0 and (x, y - 1) not in self.empty_houses:
                if self.agents[(x, y - 1)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y > 0 and (x + 1, y - 1) not in self.empty_houses:
                if self.agents[(x + 1, y - 1)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and (x - 1, y) not in self.empty_houses:
                if self.agents[(x - 1, y)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and (x + 1, y) not in self.empty_houses:
                if self.agents[(x + 1, y)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x - 1, y + 1) not in self.empty_houses:
                if self.agents[(x - 1, y + 1)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            if x > 0 and y < (self.height - 1) and (x, y + 1) not in self.empty_houses:
                if self.agents[(x, y + 1)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            if x < (self.width - 1) and y < (self.height - 1) and (x + 1, y + 1) not in self.empty_houses:
                if self.agents[(x + 1, y + 1)] == race:
                    count_similar += 1
                else:
                    count_different += 1
            try:
                similarity.append(float(count_similar) / (count_similar + count_different))
            except:
                similarity.append(1)
        return sum(similarity) / len(similarity)


def simulation():
    # First Simulation and Second Simulation for Measuring Seggregation    
    width, height = 50,50 #'''城市的大小'''
    '''种族数量'''
    race = 2
    '''最大迭代次数'''
    #max_iterations = 500
    max_iterations=1
    '''空房子的比列'''
    empty_ratio = 0.3

    schelling_1 = Schelling(width, height, empty_ratio, 0.3, max_iterations, race)

    schelling_1.populate()

    schelling_2 = Schelling(width, height, empty_ratio, 0.5, max_iterations, race)

    schelling_2.populate()

    schelling_3 = Schelling(width, height, empty_ratio, 0.8, max_iterations, race)

    schelling_3.populate()


    schelling_1.update()

    schelling_2.update()

    schelling_3.update()

    similarity_threshold_ratio = {}

    for i in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]:
        schelling = Schelling(width, height, empty_ratio, i, max_iterations, race)

        schelling.populate()

        schelling.update()

        similarity_threshold_ratio[i] = schelling.calculate_similarity()


if __name__ == "__main__":
    simulation()