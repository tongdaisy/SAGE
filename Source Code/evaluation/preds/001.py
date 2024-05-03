import random
import math

# Objects Definition
class Market:
    def __init__(self, T, N, mu, sigma, avg, stdv):
        self.T = T
        self.N = N
        self.mu = mu
        self.sigma = sigma
        self.avg = avg
        self.stdv = stdv
        self.prices = []

    def currentPrice(self):
        if len(self.prices) > 0:
            return self.prices[-1]
        else:
            return self.avg

    def getNextPrice(self):
        dt = 1 / self.T
        drift = (self.mu - 0.5 * self.sigma ** 2) * dt
        diffusion = self.sigma * math.sqrt(dt) * random.gauss(0, 1)
        price = self.currentPrice() * math.exp(drift + diffusion)
        self.prices.append(price)
        return price

    def runMarket(self):
        for _ in range(self.N):
            self.getNextPrice()

class Agent:
    def __init__(self, stock, cash, bf, sf, bp, sp, hp, options):
        self.stock = stock
        self.cash = cash
        self.bf = bf
        self.sf = sf
        self.bp = bp
        self.sp = sp
        self.hp = hp
        self.options = options
        self.buyStockCount = 0  # rename buyStock to avoid method and attribute name conflict
        self.sellStockCount = 0  # rename sellStock to avoid method and attribute name conflict
        self.holdStockValue = 0  # rename holdStock to avoid method and attribute name conflict

    def getTransactionType(self):
        if self.stock < self.bf:
            return "buyStock"
        elif self.stock > self.sf:
            return "sellStock"
        else:
            return "holdStock"

    def buyStock(self, price):
        numStocks = math.floor(self.cash / price)
        if numStocks > 0:
            transactionValue = numStocks * price
            self.stock += numStocks
            self.cash -= transactionValue
            self.buyStockCount += transactionValue
            self.options -= numStocks

    def sellStock(self, price):
        numStocks = math.floor(self.stock * self.hp / price)
        if numStocks > 0:
            transactionValue = numStocks * price
            self.stock -= numStocks
            self.cash += transactionValue
            self.sellStockCount += transactionValue
            self.options += numStocks

    def holdStock(self, price):
        self.holdStockValue += self.stock * price

    def executeTransaction(self, price):
        transactionType = self.getTransactionType()
        if transactionType == "buyStock":
            self.buyStock(price)
        elif transactionType == "sellStock":
            self.sellStock(price)
        elif transactionType == "holdStock":
            self.holdStock(price)

# Functions
def randNorm(mu, sigma):
    return random.gauss(mu, sigma)

# Simulation & Schedules
def simulation(T, N, mu, sigma, avg, stdv, stock, cash, bf, sf, bp, sp, hp, options):
    market = Market(T, N, mu, sigma, avg, stdv)
    agent = Agent(stock, cash, bf, sf, bp, sp, hp, options)

    for _ in range(N):
        price = market.getNextPrice()
        agent.executeTransaction(price)

    return agent

# Example Usage
simulation(T=1, N=100, mu=0.1, sigma=0.2, avg=100, stdv=10, stock=10, cash=1000, bf=8, sf=12, bp=0.1, sp=0.1, hp=0.05, options=0)