# the production and consumption life
import random
from collections import deque
import numpy as np


class Worker:
    def __init__(self, id, money, employed):
        self.id = id
        self.money = money
        self.employed = employed
        self.salary = 0
        self.skill = 1
        self.need = int(self.skill * random.randint(1, 2))

    def find_job(self, factories):
        unemployed_factories = [factory for factory in factories if not factory.is_full()]
        if unemployed_factories and not self.employed:
            factory = random.choice(unemployed_factories)
            factory.hire_worker(self)
            self.employed = True

    def buy_production(self, factories, avg_price):
        self.need = int(self.skill * random.randint(1, 2))
        self.need = min(self.need, int(self.money / avg_price))
        self.need = max(self.need,1)
        random.shuffle(factories)
        for f in factories:
            flag = f.sell_production(self, self.need)
            if flag:
                break

    def improve_skills(self):
        if self.money > 5 and random.uniform(0, 1) < 0.2 and not self.employed:
            self.money -= 5
            self.skill *= 1.2


class Factory:
    def __init__(self, id, production_capacity, price, produce_effectivity, salary):
        self.id = id
        self.production_capacity = production_capacity
        self.price = price
        self.workers = []
        self.store = 0
        self.money = 100
        self.money_history = deque()
        self.money_history.append(self.money)
        self.salary = salary
        self.produce_effectivity = produce_effectivity
        self.technical_level = 1

    def is_full(self):
        return len(self.workers) >= int((self.production_capacity - self.store) / self.produce_effectivity)

    def hire_worker(self, worker):
        if not self.is_full():
            self.workers.append(worker)
            worker.employed = True
            worker.salary = self.salary * worker.skill

    def provide_salary(self):
        for w in self.workers:
            w.money += self.salary
            self.money -= self.salary

    def fire_worker(self):
        if len(self.workers) > int((self.production_capacity - self.store) / self.produce_effectivity):
            random.shuffle(self.workers)
            self.workers = sorted(self.workers, key=lambda x: x.skill)
            fire_workers = self.workers[0:len(self.workers) - int(
                (self.production_capacity - self.store) / self.produce_effectivity)]
            for w in fire_workers:
                w.employed = False
            self.workers = self.workers[
                           len(self.workers) - int((self.production_capacity - self.store) / self.produce_effectivity):]

    def sell_production(self, worker, need_num):
        if (worker.money > self.price * need_num or need_num == 1) and self.store >= need_num:
            self.store -= need_num
            self.money += self.price * need_num
            worker.money -= self.price * need_num
            return True

        return False

    def adjust_price_productivity(self, demand, production):
        if demand > production:
            self.price += 0.1 * random.randint(0, 1)
            self.production_capacity += 2 * random.randint(0, 1)
        elif demand < production:
            self.price -= 0.1 * random.randint(0, 1)
            self.production_capacity -= 2 * random.randint(0, 1)
        self.price = max(0.8, self.price)
        self.price = min(1.2, self.price)
        self.production_capacity = max(0, self.production_capacity)

    def produce(self):
        for w in self.workers:
            self.store += w.skill * self.produce_effectivity
        self.store = int(self.store)
        self.provide_salary()

    def enhance_technology(self):
        if random.uniform(0, 1) < 0.1 and self.money > 50:
            self.money -= 50
            self.technical_level *= 1.1
            self.produce_effectivity *= 1.1
        self.innovation_level = min(self.technical_level, 2)
        self.produce_effectivity = min(self.produce_effectivity, 2)


class Government:
    def __init__(self, tax_rate, basic_income):
        self.tax_rate = tax_rate
        self.basic_income = basic_income
        self.help_bankruptcy = 100

    def calculate_taxes(self, workers, factories):
        total_taxes = 0
        for worker in workers:
            if worker.employed:
                total_taxes += worker.salary * self.tax_rate
                worker.money -= worker.salary * self.tax_rate
        for factory in factories:
            old_money = factory.money_history[-1]
            if old_money < factory.money:
                total_taxes += (factory.money - old_money) * self.tax_rate
                factory.money -= (factory.money - old_money) * self.tax_rate
            factory.money_history.append(factory.money)

        return total_taxes

    def provide_basic_income(self, workers):
        for worker in workers:
            if not worker.employed:
                worker.salary = self.basic_income
                worker.money += self.basic_income

    def deal_with_bankruptcy(self, factories):
        for factory in factories:
            if factory.money < 0:
                factory.money += self.help_bankruptcy


def simulate(num_workers, num_factories, num_steps):
    random.seed(1)
    workers = [Worker(i, 5, False) for i in range(num_workers)]
    factories = [Factory(i, production_capacity=random.randint(9, 11), price=random.uniform(0.9, 1.1),
                         produce_effectivity=random.uniform(1.2, 1.5), salary=random.uniform(1.0, 1.1)) for i in
                 range(num_factories)]
    government = Government(0.1, 1.0)

    for step in range(num_steps):
        random.shuffle(workers)
        random.shuffle(factories)
        workers = sorted(workers, key=lambda x: x.skill, reverse=True)
        for worker in workers:
            if not worker.employed:
                worker.find_job(factories)
            worker.improve_skills()
        total_demand = sum([w.need for w in workers])
        total_produce = sum(factory.production_capacity for factory in factories)
        for factory in factories:
            factory.produce()
        avg_price = sum([f.price for f in factories]) / len(factories)
        for worker in workers:
            worker.buy_production(factories, avg_price)
        for factory in factories:
            factory.adjust_price_productivity(total_demand, total_produce)
            factory.fire_worker()
            #factory.enhance_technology()
        government.calculate_taxes(workers, factories)
        government.provide_basic_income(workers)
        # government.deal_with_bankruptcy(factories)
        print(sum([not w.employed for w in workers]) / len(workers))
    unemployed_rate = sum([not w.employed for w in workers]) / len(workers)
    return unemployed_rate

    # Example usage


unemployed_rate = simulate(100, 10, 100)
print(unemployed_rate)
