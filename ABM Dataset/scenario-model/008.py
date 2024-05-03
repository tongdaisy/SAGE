#covid resource allocation

import random


class Agent:
    """Agent that represent either patient or staff.
    Represented by transmission rate of COVID-19, and
    holds a journey represenetd by a list of locations.
    """
    def __init__(self,
                 role,
                 infected,
                 transmission_rate,
                 curr_coord,
                 curr_location,
                 journey,
                 epsilon=0.3):
        """
        role - str, E.g. "patient", "staff"
        infected - bool
        transmission_rate - float, [0,1]
        curr_coord - tup, (y,x)
        curr_location - Location node
        journey - List of Location nodes
        epsilon - float, [0,1]
        """
        self.role = role
        self.infected = infected
        self.transmission_rate = transmission_rate
        self.curr_coord = curr_coord
        self.curr_location = curr_location
        self.journey = journey
        self.epsilon = epsilon
        self.time_spent = 0
        self.loc_idx = 0

    def risk_transmission(self):
        """Risk transmission.
        Returns True if previously uninfected and now infected.
        Returns False if uninfected, or already infected.
        """
        if not self.infected and random.random() < self.transmission_rate:
            self.infected = True
            return True
        return False

    def get_next_location(self):
        """Get next location node given current location and journey."""
        if self.loc_idx < len(self.journey) - 1:
            return self.journey[self.loc_idx + 1]
        else:
            return None

    def get_next_coord(self):
        """Get the next coordinate with some random probability."""
        coord = self.curr_coord
        location = self.curr_location
        journey = self.journey
        next_location = self.get_next_location()
        next_coord = location.get_adj_room_coord(next_location)

        if next_location is None:
            return None

        # Go to the next location if reached
        if coord == next_coord and random.random() > self.epsilon and self.time_spent > location.time_required:
            self.curr_location = next_location
            self.loc_idx += 1
            self.time_spent = 0
            return next_location.get_adj_room_coord(location)

        dx = next_coord[0] - coord[0]
        dy = next_coord[1] - coord[1]

        # Next location w.r.t. x-axis
        if dx == 0:
            ix = 0
        elif dx > 0:
            ix = 1
        else:
            ix = -1

        # Next location w.r.t. y-axis
        if dy == 0:
            iy = 0
        elif dy > 0:
            iy = 1
        else:
            iy = -1

        # Random walk at the probability of epsilon OR if process incomplete
        if self.time_spent < self.curr_location.time_required or random.random() < self.epsilon:
            ix = random.choice([0, 1, -1])
            iy = random.choice([0, 1, -1])
        self.time_spent += 1

        # Location bounds
        bx = location.size[0]
        by = location.size[1]
        return min(bx, max(0, coord[0] + ix)), min(by, max(0, coord[1] + iy))

    def move(self):
        new_coord = self.get_next_coord()
        if new_coord is None:
            return None
        self.curr_coord = new_coord
        return new_coord


class Location:
    """Location node that is connected to other locations.
    Represented by a 2D array and linked to other locations via dictionary.
    """
    def __init__(self, name, size=(10,10), time_required=10, position=(0,0)):
        self.name = name
        self.size = size
        self.adj_rooms = {}
        self.time_required = time_required
        self.position = position

    def add_adj_room(self, coord, node):
        self.adj_rooms[coord] = node

    def get_adj_room_coord(self, node):
        for coord, room in self.adj_rooms.items():
            if room == node:
                return coord
        return None

    def __repr__(self):
        str_adj_rooms = ", ".join([room.name + str(coord) for coord, room in self.adj_rooms.items()])
        return "====================\n" \
            + "Location: " + self.name + '\n' \
            + "Size: " + str(self.size) + '\n' \
            + "Adjacent rooms:\n\t" + str_adj_rooms


class Simulation:
    def __init__(self, location, agents, epoch=20):
        """
        location - Location node, usually the entrance
        agents - List of Agents
        """
        self.location = location
        self.agents = agents
        self.t = 0
        self.statistics = {
            'transmissions': 0,
            'agents': 0,
        }
        self.total_transmissions = 0

    def print_state(self):
        print(f"==========State(t={self.t})==========")
        for agent in self.agents:
            curr_location = agent.curr_location
            next_location = agent.get_next_location()
            if next_location:
                print(f"{agent.role} "
                      f"from {curr_location.name}{agent.curr_coord} "
                      f"to {next_location.name}{curr_location.get_adj_room_coord(next_location)}, "
                      f"infected: {agent.infected}.")
            else:
                print(f"{agent.role} "
                      f"from {curr_location.name}{agent.curr_coord} "
                      f"to exit, "
                      f"infected: {agent.infected}.")

    def print_statistics(self):
        print("==========Statistics==========")
        for key, value in self.statistics.items():
            print(f"{key}: {value}")

    def step(self, verbose=False):
        self.t += 1

        # Contact Tracer = {location_name: {(x,y): [Agent]}}
        contact_tracer = {}

        # Every agent takes a step
        for agent in self.agents:
            # If agent has nowhere else to go, remove the agent
            if agent.move() is None:
                self.agents.remove(agent)
                continue
            # Trace location of agent
            location_name = agent.curr_location.name
            if location_name not in contact_tracer:
                contact_tracer[location_name] = {}
            coordinate = agent.curr_coord
            if coordinate not in contact_tracer[location_name]:
                contact_tracer[location_name][coordinate] = []
            contact_tracer[location_name][coordinate].append(agent)

        # Check if any agent is in contact with another
        for location_name in contact_tracer:
            for coordinate in contact_tracer[location_name]:
                contacts = contact_tracer[location_name][coordinate]

                # If contact is transmissible, risk transmission
                if len(contacts) > 1 and any([agent.infected for agent in contacts]):
                    for agent in contacts:
                        if agent.risk_transmission():
                            self.statistics['transmissions'] += 1
        if verbose:
            self.print_state()

    def compute_statistics(self):
        self.statistics['average_transmissions'] = self.statistics['transmissions']/self.statistics['agents']

    def run(self, agent_factory, epoch=50, renderer=None, verbose=False):
        # Render environment
        if renderer:
            renderer.render()

        for t in range(epoch):
            # Generate agents at specified rate
            agent = agent_factory.create_agent(t)
            if agent is not None:
                self.agents.append(agent)
                self.statistics['agents'] += 1

            # Take an environment step
            self.step(verbose=verbose)

            # Update render
            if renderer:
                renderer.update(self.agents)

        self.compute_statistics()
        if verbose:
            self.print_statistics()


class AgentFactory:
    def __init__(self, creation_rate, infected_rate, transmission_rate, journeys, entrance):
        self.creation_rate = creation_rate
        self.infected_rate = infected_rate
        self.transmission_rate = transmission_rate
        self.agents = []
        self.journeys = journeys
        self.entrance = entrance

    def create_agent(self, t):
        created = True if random.random() < self.creation_rate else False
        if created:
            infected = True if random.random() < self.infected_rate else False
            agent = Agent(role="Patient",
                          infected=infected,
                          transmission_rate=self.transmission_rate,
                          curr_coord=(9, 5),
                          curr_location=self.entrance,
                          journey=random.choice(self.journeys),
                          epsilon=0.2)
            self.agents.append(agent)
            return agent


if __name__ == "__main__":
    entrance = Location("Entrance", size=(10,10))
    pharmacy = Location("Pharmacy", size=(5,5))
    registration = Location("Registration", size=(2,2))
    entrance.add_adj_room(coord=(0,0), node=pharmacy)
    entrance.add_adj_room(coord=(1,1), node=registration)
    print(entrance)
    print(pharmacy)