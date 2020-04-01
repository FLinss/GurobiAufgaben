import gurobipy as gp
from gurobipy import GRB

#### Mengen ####

numberOfDesks = 3
numberOfPersons = 9

desks = range(numberOfDesks)
persons = range(numberOfPersons)

#### Parameter ####

sympathy = [[0, 6, 4, 10, 1, 2, 6, 2, 4],
            [6, 0, 7, 3, 6, 1, 5, 10, 5],
            [4, 7, 0, 10, 6, 3, 10, 1, 4],
            [10, 3, 10, 0, 4, 6, 9, 6, 10],
            [1, 6, 6, 4, 0, 10, 1, 2, 4],
            [2, 1, 3, 6, 10, 0, 9, 7, 7],
            [6, 5, 10, 9, 1, 9, 0, 1, 9],
            [2, 10, 1, 6, 2, 7, 1, 0, 8],
            [4, 5, 4, 10, 4, 7, 9, 8, 0]]

capacity = [4, 3, 2] 

#### Gurobi Modell ####

m = gp.Model()

x = m.addVars(numberOfPersons, numberOfDesks, vtype=GRB.BINARY, name="x")

m.setObjective(
    gp.quicksum(
        gp.quicksum(
            gp.quicksum(
                sympathy[person1][person2] * x[person1, desk] * x[person2, desk]
            for desk in desks)
        for person2 in persons if person2 != person1)
    for person1 in persons),
GRB.MAXIMIZE)

for desk in desks:
    m.addConstr(gp.quicksum(x[person, desk] for person in persons) <= capacity[desk], name="ConstrDesk"+str(desk))

#m.addConstrs((x.sum('*',desk) <= capacity[desk] for desk in desks), name="ConstrDesk")

for person in persons:
    m.addConstr(gp.quicksum(x[person, desk] for desk in desks) == 1, name="ConstrPerson"+str(person))

#m.addConstrs((x.sum(person,'*') == 1 for person in persons), name="ConstrPerson")

m.optimize()

m.printAttr('ObjVal')
m.printAttr('X')

names = ["Anna", "Berti", "Carl", "Dieter", "Emil", "Franz", "Gerd", "Hanna", "Ilse"]

print("\nSitzverteilung\n")
for person in persons:
    for desk in desks:
        if x[person, desk].X > 0:
            print(names[person], "sitzt am Tisch", desk)

for desk in desks:
    print("\nPersonen am Tisch", desk)
    for person1 in range(numberOfPersons-1):
        for person2 in range(person1+1, numberOfPersons):
            if x[person1, desk].X * x[person2, desk].X > 0:
                print(names[person1], "und", names[person2], "haben den Sympathiewert:", sympathy[person1][person2])