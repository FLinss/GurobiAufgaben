import gurobipy as gp
from gurobipy import GRB

g = [10, 20]

a = [[6, 2],
    [10, 10],
    [1, 4]]

T = [480, 1000, 280]

I_max = 3
J_max = 2

I = range(I_max)
J = range(J_max)

# Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
x={}
for j in J:
    x[j] = m.addVar(obj=g[j], name="x"+str(j))
#x = m.addVars(J_max, obj=g, name="x")

# Definition der Zielfunktion
m.modelSense = GRB.MAXIMIZE
#m.setObjective(gp.quicksum(g[j] * x[j] for j in J),GRB.MAXIMIZE)

# Hinzufügen von Nebenbedingungen
for i in I:
    m.addConstr(gp.quicksum(a[i][j] * x[j] for j in J) <= T[i], name="c"+str(i))
#m.addConstrs(gp.quicksum(a[i][j] * x[j] for j in J) <= T[i] for i in I)

# Optimierung
m.optimize()

# Ergebnisausgabe
m.printAttr(GRB.Attr.X)
m.printAttr(GRB.Attr.ObjVal)
