# Bayesland

import random
import scipy
import numpy as np
import matplotlib.pyplot as plt
import random
class agent():

    game_count = 0
    head_count = 0

    def __init__(self, bankroll):
        self.bankroll = bankroll

    def getBankroll(self):
        return self.bankroll

    def setBankroll(self,add,amount):
        if add:
            self.bankroll += amount
        else:
            self.bankroll -= amount

    def getKey(self):
        return random.randint(1,5)

    def setPast(self):
        self.game_count = self.game_count + 1
        self.head_count = self.head_count + 1

    def getPast(self):
        if self.game_count == 0:
            return random.randint(0, 100)/100
        return self.head_count/self.game_count

# 1 = heads
def tossCoin():
    return np.random.binomial(n=1,size=1,p=0.6)[0]

def simulation():
    agent1 = agent(100)
    agent2 = agent(100)
    agent3 = agent(100)
    agents = [agent1,agent2,agent3]

    bankrolls1 = []
    bankrolls2 = []
    bankrolls3 = []

    print(agent1.getBankroll())
    print(agent2.getBankroll())
    print(agent2.getBankroll())

    print(agent1.getKey())

    print(tossCoin())

    #for i in range(1000):
    for i in range(1):
        key1 = agent1.getKey()
        key2 = agent2.getKey()
        key3 = agent3.getKey()

        past1 = agent1.getPast()
        past2 = agent2.getPast()
        past3 = agent3.getPast()

        if (key1==key2 and past1!=past2):
            result = tossCoin()
            if(result == 1 and past1 > past2):
                amount = 0.05*agent2.getBankroll()
                agent1.setBankroll(add=True, amount=amount)
                agent2.setBankroll(add=False, amount=amount)
                print("agent1 wins")
            if (result == 1 and past1 < past2):
                amount = 0.05 * agent1.getBankroll()
                agent1.setBankroll(add=False, amount=amount)
                agent2.setBankroll(add=True, amount=amount)
                print("agent2 wins")

            bankrolls1.append(agent1.getBankroll())
            bankrolls2.append(agent2.getBankroll())

        if (key1 == key3 and past1!=past3):
            result = tossCoin()
            if (result == 1 and past1 > past3):
                amount = 0.05 * agent3.getBankroll()
                agent1.setBankroll(add=True, amount=amount)
                agent3.setBankroll(add=False, amount=amount)
                print("agent1 wins")
            if (result == 1 and past1 < past3):
                amount = 0.05 * agent1.getBankroll()
                agent1.setBankroll(add=False, amount=amount)
                agent3.setBankroll(add=True, amount=amount)
                print("agent3 wins")

            bankrolls1.append(agent1.getBankroll())
            bankrolls3.append(agent3.getBankroll())

        if (key2 == key3 and past2!=past3):
            result = tossCoin()
            if (result == 1 and past2 > past3):
                amount = 0.05 * agent3.getBankroll()
                agent2.setBankroll(add=True, amount=amount)
                agent3.setBankroll(add=False, amount=amount)
                print("agent2 wins")
            if (result == 1 and past2 < past3):
                amount = 0.05 * agent2.getBankroll()
                agent2.setBankroll(add=False, amount=amount)
                agent3.setBankroll(add=True, amount=amount)
                print("agent3 wins")

            bankrolls2.append(agent2.getBankroll())
            bankrolls3.append(agent3.getBankroll())

if __name__ == '__main__':
    
    simulation()