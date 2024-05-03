# the US election
import random
import matplotlib.pyplot as plt

class Voter:
    def __init__(self, ideology):
        self.ideology = ideology
        self.vote = None

    def cast_vote(self, candidates):
        distances = [abs(candidate - self.ideology) for candidate in candidates]
        min_distance = min(distances)
        min_indices = [i for i, distance in enumerate(distances) if distance == min_distance]
        self.vote = random.choice(min_indices)

class Election:
    def __init__(self, num_voters, num_candidates):
        self.voters = [Voter(random.uniform(0, 1)) for _ in range(num_voters)]
        self.candidates = [random.uniform(0, 1) for _ in range(num_candidates)]
        self.results = [0] * num_candidates

    def run(self):
        for voter in self.voters:
            voter.cast_vote(self.candidates)
            self.results[voter.vote] += 1

def simulation():

    num_voters = 1000
    num_candidates = 3
    num_iterations = 100

    election = Election(num_voters, num_candidates)
    for _ in range(num_iterations):
        election.run()

simulation()
