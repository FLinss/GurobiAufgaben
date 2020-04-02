import gurobipy as gp
from gurobipy import GRB
import random

numberOfJobs = 100
numberOfCandidates = 100
jobs = range(numberOfJobs)
candidates = range(numberOfCandidates)

random.seed(0)
scorings = {(canditate, job): random.random() for canditate in candidates for job in jobs}

m = gp.Model()

x = m.addVars(numberOfCandidates, numberOfJobs, vtype=GRB.BINARY, name="x")

m.setObjective(
    gp.quicksum(
        gp.quicksum(
            scorings[candidate, job] * x[candidate, job]
            for job in jobs)
        for candidate in candidates), GRB.MAXIMIZE)

m.addConstrs((x.sum('*', job) == 1 for job in jobs), name="job")

m.addConstrs((x.sum(candidate, '*') == 1 for candidate in candidates), name="candidate")

m.optimize()

print()
for candidate in candidates:
    for job in jobs:
        if x[candidate, job].X > 0:
            print("Kandidat", candidate, "wird Job", job, "zugewiesen.")
