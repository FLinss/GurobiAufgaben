import gurobipy as gp
from gurobipy import GRB

# Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
x1 = m.addVar(vtype=GRB.CONTINUOUS, obj=10, lb=0, name="x_1")
x2 = m.addVar(vtype=GRB.CONTINUOUS, obj=20, lb=0, name="x_2")

# Definition der Zielfunktion
m.modelSense = GRB.MAXIMIZE

# Hinzufügen von Nebenbedingungen
m.addConstr(6*x1 + 2*x2 <= 480,"nb_I")
m.addConstr(10*x1 + 10*x2 <= 1000, "nb_II")
m.addConstr(x1 + 4*x2 <= 280, "nb_III")

# Optimierung
m.optimize()

# Ergebnisausgabe
m.printAttr(GRB.Attr.X)
m.printAttr(GRB.Attr.ObjVal)
