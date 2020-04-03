import gurobipy as gp
from gurobipy import GRB

# Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
xB = m.addVar(vtype=GRB.CONTINUOUS, ub=600, name="x_B")
xK = m.addVar(vtype=GRB.CONTINUOUS, ub=200, name="x_K")
xL = m.addVar(vtype=GRB.CONTINUOUS, ub=50, name="x_L")
xT = m.addVar(vtype=GRB.CONTINUOUS, ub=150, name="x_T")

# Definition der Zielfunktion
m.setObjective(4.5*xB + 3.5*xK + 2.3*xL + 3.2*xT, GRB.MAXIMIZE)

# Hinzufügen von Nebenbedingungen
m.addConstr(6*xB + 3*xK + 3*xL + 4*xT <= 3900,"nb_I")
m.addConstr(2*xB + 2.5*xK + 2.5*xL + 3*xT <= 3900, "nb_II")
m.addConstr(2.5*xB + 3*xK + 1.5*xL + 3*xT <= 3900, "nb_III")

# Optimierung
m.optimize()

# Ergebnisausgabe
m.printAttr(GRB.Attr.ObjVal)
m.printAttr(GRB.Attr.X)
