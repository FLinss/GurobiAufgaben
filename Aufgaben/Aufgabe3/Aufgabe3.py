import gurobipy as gp
from gurobipy import GRB
import csv



# Parameter
B = {}
B["min"] = []
B["mean"] = []
B["max"] = []
with open("Bedarfe.csv", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        B["min"].append(int(row["min"]))
        B["mean"].append(int(row["mean"]))
        B["max"].append(int(row["max"]))

kL = 2
kB = 400

# Mengen
T_max = len(B["mean"])
T = range(T_max)

#  Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
r = {}
for t in T:
    r[t] = m.addVar(vtype=GRB.INTEGER, lb=0, name="r" + str(t))
y = {}
for t in T:
    y[t] = m.addVar(vtype=GRB.BINARY, name="y" + str(t))
L = {}
for t in range(T_max + 1):
    L[t] = m.addVar(vtype=GRB.INTEGER, lb=0, name="L" + str(t))

# Definition der Zielfunktion
m.setObjective(gp.quicksum(kB * y[t] + kL*L[t+1] for t in T), GRB.MINIMIZE)

# Hinzufügen der Nebenbedingungen
for t in T:
    m.addConstr(L[t+1] == L[t] + r[t] - B["mean"][t], "LB" + str(t))

for t in T:
    m.addConstr(r[t] <= L[t+1] + B["mean"][t], "BM" + str(t))

for t in T:
    m.addConstr(y[t]*1000 >= r[t], "BK" + str(t))

m.addConstr(L[0] == 0, "LAB")
m.addConstr(L[T_max] == 0, "LEB")

m.optimize()
m.printAttr(GRB.Attr.ObjVal)
m.printAttr(GRB.Attr.X)

m.write("model.lp")
m.write("solution.sol")

costs = {}
yResults = {}
LResults = {}
rResults = {}
for key in B.keys():
    for t in T:
        constrLB = m.getConstrByName("LB" + str(t))
        constrLB.setAttr(GRB.Attr.RHS, -B[key][t])
        constrBM = m.getConstrByName("BM" + str(t))
        constrBM.setAttr(GRB.Attr.RHS, B[key][t])
    m.optimize()
    costs[key] = m.ObjVal
    yResults[key] = []
    LResults[key] = []
    rResults[key] = []
    for t in T:
        yResults[key].append(round(y[t].X))
        LResults[key].append(L[t].X)
        rResults[key].append(r[t].X)

print("\nAlle Bedarfe\n")
for key in costs.keys():
    print("Bedarfe:", key)
    print("Kosten:", costs[key])
    print("Bestellungen:", yResults[key])
    print("Lagerbestand:", LResults[key])
    print("Bestellmenge:", rResults[key],"\n")

