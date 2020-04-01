import gurobipy as gp
from gurobipy import GRB

# Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
x = m.addVar(vtype=GRB.BINARY, name="x")
y = m.addVar(vtype=GRB.BINARY, name="y")
z = m.addVar(vtype=GRB.BINARY, name="z")

# Definition der Zielfunktion
m.setObjective(x + y + 2*z, GRB.MAXIMIZE)

# Hinzufügen von Nebenbedingungen
m.addConstr(0.5*x + y + 2*z <= 3)
m.addConstr(x + y == 1)

# Optimierung
m.optimize()

# Ergebnisausgabe
m.printAttr('X')
m.printAttr('ObjVal')