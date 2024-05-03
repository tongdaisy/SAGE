# traffic scenario that support go straight/ change direction
import math
import random


class Lane:
    def __init__(self, x, y, width, height, allow_dirction, speed_limit):
        # 0 to right, 1 to up, 2 to left, 3 to down
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.allow_direction = allow_dirction
        self.speed_limit = speed_limit


class Road:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lanes = []

    def add_lane(self, lane):
        self.lanes.append(lane)


class RoadMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.roads = []
        self.intersections = []
        self.vehicles = []
        self.obstacles = []
        self.traffic_accidents = []

    def add_road(self, road):
        self.roads.append(road)

    def add_intersection(self, intersection):
        self.intersections.append(intersection)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def add_traffic_accident(self, accident):
        self.traffic_accidents.append(accident)

    def get_nearest_intersection(self, x, y):
        min_distance = float('inf')
        nearest_intersection = None
        for intersection in self.intersections:
            distance = (x - intersection.x) ** 2 + (y - intersection.y) ** 2
            if distance < min_distance:
                min_distance = distance
                nearest_intersection = intersection
        return nearest_intersection


class Vehicle:
    def __init__(self, x, y, speed, direction, speed_limit):
        # 0 to right, 1 to up, 2 to left, 3 to down
        self.x = x
        self.y = y
        self.speed = min(speed, speed_limit)
        self.direction = direction

    def move(self, signal, x, y):
        new_x = self.x
        new_y = self.y
        if signal != 1:
            if self.direction == 0:
                new_x += self.speed
                if self.x < x and new_x >= x:
                    self.stop(self.x, self.y)
                    return
            if self.direction == 2:
                new_x -= self.speed
                if self.x > x and new_x <= x:
                    self.stop(self.x, self.y)
                    return
        if signal != 0:
            if self.direction == 1:
                new_y -= self.speed
                if self.y > y and new_y <= y:
                    self.stop(self.x, self.y)
                    return
            if self.direction == 3:
                new_y += self.speed
                if self.y < y and new_y >= y:
                    self.stop(self.x, self.y)
                    return
        if self.direction == 0:
            self.x += self.speed
        if self.direction == 2:
            self.x -= self.speed
        if self.direction == 1:
            self.y -= self.speed
        if self.direction == 3:
            self.y += self.speed

    def check_collision(self, v):
        accident = None
        # Implement collision checking logic here
        if self.x == v.x and self.y == v.y and self.direction != v.direction and (
                self.direction + 2) % 4 != v.direction:
            severity = v.speed * self.speed
            accident = TrafficAccident(self.x, self.y, severity)
        return accident

    def stop(self, x, y):
        self.x = x
        self.y = y

    def change_direction(self, road_map, turn_direction, signal):
        inter = road_map.get_nearest_intersection(self.x, self.y)
        # judge whether close to inter
        x = inter.x
        y = inter.y
        new_x = self.x
        new_y = self.y
        close_flag = False
        if self.direction == 0:
            new_x += self.speed
            if self.x < x and new_x >= x:
                close_flag = True
        if self.direction == 2:
            new_x -= self.speed
            if self.x > x and new_x <= x:
                close_flag = True
        if self.direction == 1:
            new_y -= self.speed
            if self.y > y and new_y <= y:
                close_flag = True
        if self.direction == 3:
            new_y += self.speed
            if self.y < y and new_y >= y:
                close_flag = True
        if not close_flag:
            return 0
        # turn_left=0, turn right=1 reverse=2
        if turn_direction == 0:
            self.x = x
            self.y = y
            self.direction = (self.direction + 1) % 4
            return 1
        else:
            # turn right/ reverse
            if (signal == 2 and (self.direction == 1 or self.direction == 3)) or (
                    signal == 3 and (self.direction == 0 or self.direction == 2)):
                self.x = x
                self.y = y
                if turn_direction == 1:
                    self.direction = (self.direction + 3) % 4
                if turn_direction == 2:
                    self.direction = (self.direction + 2) % 4
                return 1
        return 2


class Intersection:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.roads = []
        self.vehicles = []
        self.signal = 0  # 0: 1,3 pass, 1: 0,2 pass; 2:1,3 turn right/revers; 3:0,2 turn right/reverse

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        self.vehicles.remove(vehicle)

    def change_signal(self):
        self.signal = (self.signal + 1) % 4


# Define the TrafficAccident class
class TrafficAccident:
    def __init__(self, x, y, severity):
        self.x = x
        self.y = y
        self.severity = severity


def simulation(num_vehicles=12, steps=10, speed_limit=5):
    random.seed(10)
    # Create a RoadMap object
    road_map = RoadMap(100, 100)

    # Add some roads to the map
    road1 = Road(50, 50, 10, 2)
    road1.add_lane(Lane(50, 50, 10, 1, 1, speed_limit))
    road1.add_lane(Lane(50, 50, 10, 1, 3, speed_limit))
    road_map.add_road(road1)

    road2 = Road(50, 50, 2, 10)
    road2.add_lane(Lane(50, 50, 1, 10, 0, speed_limit))
    road2.add_lane(Lane(50, 50, 1, 10, 2, speed_limit))
    road_map.add_road(road2)

    # Add some intersections to the map
    intersection1 = Intersection(50, 50)
    intersection1.roads.extend([road1, road2])
    road_map.add_intersection(intersection1)

    # Create some vehicles and add them to the map
    for i in range(int(num_vehicles / 4)):
        vehicle = Vehicle(50, random.randint(52, 55), random.randint(1, 2), 1, speed_limit)
        road_map.add_vehicle(vehicle)
        vehicle = Vehicle(50, random.randint(45, 48), random.randint(1, 2), 3, speed_limit)
        road_map.add_vehicle(vehicle)
        vehicle = Vehicle(random.randint(45, 48), 50, random.randint(1, 2), 0, speed_limit)
        road_map.add_vehicle(vehicle)
        vehicle = Vehicle(random.randint(52, 55), 50, random.randint(1, 2), 2, speed_limit)
        road_map.add_vehicle(vehicle)

    # Simulate the traffic flow
    total_accidents = []
    num_change_directions = 0
    for step in range(steps):
        for inter in road_map.intersections:
            inter.change_signal()
        # Update the positions of all vehicles
        for vehicle in road_map.vehicles:
            inter = road_map.get_nearest_intersection(vehicle.x, vehicle.y)
            flag = 0
            if random.uniform(0, 1) < 0.5:
                flag = vehicle.change_direction(road_map, random.randint(0, 2), inter.signal)
            vehicle.move(inter.signal, inter.x, inter.y)
            if flag != 0:
                num_change_directions += 1
        # Check for collisions between vehicles
        for i in range(len(road_map.vehicles)):
            for j in range(i + 1, len(road_map.vehicles)):
                vehicle1 = road_map.vehicles[i]
                vehicle2 = road_map.vehicles[j]
                accident = vehicle1.check_collision(vehicle2)
                if accident is not None:
                    total_accidents.append(accident)
                    road_map.add_traffic_accident(accident)
                    print("Collision detected!", i, j, accident.x, accident.y)

        # Check for traffic accidents
        for accident in road_map.traffic_accidents:
            if accident.severity > 3:
                print("Traffic accident detected!")
    num_accidents = len(total_accidents)

    return num_accidents, num_change_directions


num_accidents, num_change_directions = simulation()
print(num_accidents, num_change_directions)
