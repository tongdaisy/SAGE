#the situation and waste food


import random 
import copy
import pandas as pd

class Store():
    def __init__(self):
        self.shelves = pd.DataFrame(columns= [
            'Type', 
            'Servings', 
            'Expiration Min.', 
            'Expiration Max.',
            'Price',
            'kg',
            'kcal_kg',
            'Inedible Parts'
            ])
        self.stock_shelves()
        self.inventory = []
    
    def stock_shelves(self):
        food_types = [
            "Meat & Fish", 
            "Dairy & Eggs", 
            "Fruits & Vegetables", 
            "Dry Foods & Baked Goods", 
            "Snacks, Condiments, Liquids, Oils, Grease, & Other", 
            'Store-Prepared Items' 
            ]
        for food_type in food_types:
            self.shelves = self.shelves.append(self.food_data(food_type=food_type, servings=6), ignore_index=True)
            self.shelves = self.shelves.append(self.food_data(food_type=food_type, servings=12), ignore_index=True)
            self.shelves = self.shelves.append(self.food_data(food_type=food_type, servings=20), ignore_index=True)

    def food_data(self, food_type: str, servings:int):
        ''' RGO - 
        Could make price smaller per kg for things with more 
        servings to improve accuracy to a real market'''
        inedible_parts = 0
        if food_type == 'Meat & Fish':
            exp_min = 4 # days 
            exp_max = 11 # days
            kg = 0.09*servings # assume 90g meat per serving
            price = 6*2.2*kg # assume $6/lb to total for kg
            kcal_kg = 2240 # assume 2240 kcal per kg of meat
            inedible_parts = 0.1
        elif food_type == 'Dairy & Eggs':
            exp_min = 7 # days 
            exp_max = 28 # days
            kg = 0.109*servings # assume 109g dairy&egg per serving
            price = 6*16/27*2.2*kg # assume $6/27oz to total for kg
            kcal_kg = 1810 # assume 1810 kcal per kg of dairy&eggs
            inedible_parts = 0.1
        elif food_type == 'Fruits & Vegetables':
            exp_min = 5 # days 
            exp_max = 15 # days
            kg = 0.116*servings # assume 116g f,v per serving
            price = 3.62*2.2*kg # assume $3.62/lb to total for kg
            kcal_kg = 790 # assume 790 kcal per kg of f,v
        elif food_type == 'Dry Foods & Baked Goods':
            exp_min = 7 # days 
            exp_max = 8*7 # days
            kg = 0.065*servings # assume 65g per serving
            price = 1.5*2.2*kg # assume $1.50/lb to total for kg
            kcal_kg = 3360 # assume 3360 kcal per kg
        elif food_type == 'Snacks, Condiments, Liquids, Oils, Grease, & Other':
            exp_min = 7 # days 
            exp_max = 8*7 # days
            kg = 0.095*servings # assume 95g per serving
            price = 3.3*2.2*kg # assume $3.30/lb to total for kg
            kcal_kg = 2790 # assume 2790 kcal per kg
        elif food_type == 'Store-Prepared Items':
            exp_min = 2 # days 
            exp_max = 7 # days
            kg = 0.095*servings # assume 95g per serving
            price = 0.33*16*2.2*kg # assume $0.33/oz to total for kg
            kcal_kg = 2790 # assume 2790 kcal per kg
        else:
            raise ValueError(f"{food_type}is not a listed Food Type")
        new_food = {
            'Type': food_type, 
            'Servings': servings, 
            'Expiration Min.': exp_min, 
            'Expiration Max.': exp_max,
            'Price': price,
            'kg': kg,
            'kcal_kg': kcal_kg,
            'Inedible Parts': inedible_parts
            }
        return new_food

class Food():
    def __init__(self, food_data:dict):
        self.type = food_data['Type']
        self.kg = food_data['kg']
        self.servings = food_data['Servings']
        self.expiration_time = random.randint(food_data['Expiration Min.'], food_data['Expiration Max.'])
        self.price_kg = food_data['Price']/self.kg
        self.inedible_parts = food_data['Inedible Parts']
        self.frozen = False
        self.serving_size = self.kg/self.servings
        self.kcal_kg = food_data['kcal_kg']
    def decay(self):
        if self.frozen == False:
            self.expiration_time -= 1

class CookedFood(Food):
    def __init__(self, composition: dict, kg: float, kcal_per_kg: float):
        self.composition = composition
        self.type = 'Cooked, Prepared Items, & Leftovers'
        self.kg = kg
        self.kcal_kg = kcal_per_kg
        self.expiration_time = random.uniform(4, 11)
        self.frozen = False

class House():
    ''' could make a house function for deciding the
    days tasks including amrits intention work'''
    def __init__(self,id: int, store: Store):
        self.id = id
        self.store = store
        self.adults = random.randint(1,3)
        self.dependents = random.randint(0,2)
        self.kcal_day = self.adults*random.gauss(2144, 1308) + self.dependents*random.gauss(1800,1434)
        self.pantry = [] # food pre prep/cook
        self.fridge = [] # food post cook
        self.kitchen = [] # food post prep
        self.waste_bin = [] # food wasted
        self.stomach = [] #food eaten
        self.shopping_frequency = random.randint(1,7) #days between shopping trips
        self.time_available_for_meal_prep = [2, 0.5, 0.5, 0.5, 0.5, 1, 2] # time available for cooking each day of the week, not yet utilized
        self.budget = 20 #dollars, not used
    
    def shop(self):
        # randomly selects frequency*2 items from the store
        # set seed with random_state= int
        basket = self.store.shelves.sample(n=2*self.shopping_frequency)
        for i in range(len(basket)):
            item_info = basket.iloc[i].to_dict()
            food = Food(item_info)
            self.store.inventory.append(copy.deepcopy(food))
            if food.type == 'Store-Prepared Items':
                self.fridge.append(food)
            else:
                self.pantry.append(food)
    
    def prep(self, food: Food, servings: int):
        if food.expiration_time <= 0:
            self.waste({
                'Type': food.type,
                'kg': food.kg,
                'House': self.id
            })
            return
        prepped = copy.deepcopy(food)
        prepped.servings = servings
        if food.servings > servings:
            food.servings -= servings
            food.kg -= servings*food.serving_size
        else:
            servings = food.servings
            self.pantry.remove(food)
            del food
        if prepped.inedible_parts > 0:
            waste_kg = prepped.kg/prepped.inedible_parts
            prepped.kg /= (1-prepped.inedible_parts) # remove the inedible parts
            prepped.serving_size /= (1-prepped.inedible_parts) # adjust the serving size accordingly
            waste_data = {
                'Type': 'Inedible Parts',
                'kg': waste_kg,
                'House': self.id
            }
            self.waste(waste_data= waste_data)
        self.kitchen.append(prepped) # add the prepped food to be cooked or eaten from the kitchen

    def waste(self, waste_data: dict):
        '''RGO - make so that if it is cooked it breaks up waste
        into all of it's parts with a column to denote whether 
        it was on it's own when wasted or cooked'''
        self.waste_bin.append(Waste(waste_data=waste_data))

    def cook(self):
        kg = 0
        composition = {
            'Meat & Fish': 0,
            'Dairy & Eggs':0,
            'Fruits & Vegetables':0,
            'Dry Foods & Baked Goods':0,
            'Snacks, Condiments, Liquids, Oils, Grease, & Other':0
        }
        kcal = 0
        if len(self.pantry) < 4:
            self.shop
        for i in range(random.randint(2,5)):
            self.prep(random.choice(self.pantry), random.randint(1, 4))
        for food in self.kitchen:
            kg += food.kg
            composition[food.type] += food.kg
            kcal += food.kcal_kg * food.kg
            self.kitchen.remove(food)
            del food
        if kg == 0: # only occurs if all the food they grabbed to cook is bad
            self.eat()
            return
        for key, value in composition.items():
            composition[key] /= kg
        self.fridge.append(CookedFood(composition= composition, kg= kg, kcal_per_kg= kcal/kg))

    def eat(self):
        ''' currently just picks the most recent item from the 
        fridge, assumes they stop eating once the daily kcal need is met,
        assume that store prepped food gets eaten first'''
        kcal_today = self.kcal_day
        for food in reversed(self.fridge):
            if food.expiration_time > 0:
                if food.type == 'Store-Prepared Items':
                    if kcal_today >= food.kcal_kg*food.kg:
                        kcal_today -= food.kcal_kg*food.kg 
                        self.fridge.remove(food)
                        self.stomach.append(food)
                    else:
                        eaten_food = copy.deepcopy(food)
                        food.kg -= kcal_today/food.kcal_kg
                        eaten_food.kg = kcal_today/eaten_food.kcal_kg
                        kcal_today = 0
                    if kcal_today == 0:
                        return 
            else:
                self.waste({
                    'kg': food.kg,
                    'Type': food.type,
                    'House': self.id
                })
                self.fridge.remove(food)
                del food
        for food in reversed(self.fridge):
            if food.expiration_time > 0:
                if kcal_today >= food.kcal_kg*food.kg:
                    kcal_today -= food.kcal_kg*food.kg 
                    self.fridge.remove(food)
                    self.stomach.append(food)
                else:
                    eaten_food = copy.deepcopy(food)
                    food.kg -= kcal_today/food.kcal_kg
                    eaten_food.kg = kcal_today/eaten_food.kcal_kg
                    kcal_today = 0
                if kcal_today == 0:
                    return 
            else:
                self.waste({
                    'kg': food.kg,
                    'Type': food.type,
                    'House': self.id
                })
                self.fridge.remove(food)
                del food
class Waste():
    def __init__(self, waste_data:dict):
        self.kg = waste_data['kg']
        self.type = waste_data['Type']
        self.house_id = waste_data['House']

import pandas as pd
def init(num_of_houses=100):
    # Store data for tidiverse later
    global bought_food
    bought_food = pd.DataFrame(columns=[
        'Type', 
        'Servings', 
        'Expiration time',
        'Price',
        'kg',
        'kcal_kg',
        'Inedible Parts',
        'Day Bought',
        'House'
    ])
    global eaten_food
    eaten_food = pd.DataFrame(columns=[
        'Type',
        'Part of Home-Cooked Meal',
        'kg',
        'kcal',
        'price',
        'expiration time',
        'House',
        'Day Eaten'
    ])
    global wasted_food
    wasted_food = pd.DataFrame(columns=[
        'Type',
        'kg',
        #'Cooked at home', - to be implemented ln 69,71,72
        'House',
        'Day Wasted'
    ])
    #----------------------------
    # Create a store and all of the houses
    store = Store()
    global houses
    houses = []
    for i in range(num_of_houses):
        house = House(id=i, store= store)
        houses.append(house)
        house.shop()
    #----------------------------

def simulation(days=54):
    for day in range(days):
        for house in houses:
            if day % house.shopping_frequency == 0:
                house.shop()
            house.cook()
            house.eat()
            collect_data(day=day, house= house)
            for food in house.fridge:
                food.decay()
            for food in house.pantry:
                food.decay()

def collect_data(day:int, house:House):
    # food bought
    for food in house.store.inventory:
        bought_food.loc[len(bought_food)] = {
        'Type': food.type, 
        'Servings': food.servings, 
        'Expiration time': food.expiration_time,
        'Price': food.price_kg*food.kg,
        'kg':food.kg,
        'kcal_kg': food.kcal_kg,
        'Inedible Parts': food.inedible_parts,
        'Day Bought': day,
        'House': house.id
        }
        house.store.inventory.remove(food)
        del food
    for waste in house.waste_bin:
        wasted_food.loc[len(wasted_food)] = {
        'Type':waste.type,
        #'Part of Home-Cooked Meal', - to be implemented
        'kg': waste.kg,
        #'kcal', - to be implemented ln 
        #'price', - to be implemented
        'House': house.id,
        'Day Wasted': day
        }
        house.waste_bin.remove(waste)
        del waste
    for food in house.stomach:
        eaten_food.loc[len(eaten_food)] = {
        'Type':food.type,
        #'Part of Home-Cooked Meal',
        'kg': food.kg,
        'kcal':food.kcal_kg*food.kg,
        #'price':food.price_kg*food.kg, - not yet implemented
        'expiration time':food.expiration_time,
        'House':house.id,
        'Day Eaten':day
        }
        house.stomach.remove(food)
        del food

def data_to_csv(trial=1):
    bought_food.to_csv(f'bought_food_{trial}.csv')
    eaten_food.to_csv(f'eaten_food_{trial}.csv')
    wasted_food.to_csv(f'wasted_food_{trial}.csv')


init(num_of_houses=10)
#simulation()
#data_to_csv()