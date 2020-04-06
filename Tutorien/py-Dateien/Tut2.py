import gurobipy as gp
from gurobipy import GRB

# Parameter
d = [200, 250, 150, 300, 100]
b = [400, 350, 600]
f = [60000, 60000, 80000]
c = [[270, 170, 400, 450, 300],
     [320, 290, 490, 230, 120],
     [120, 390, 240, 230, 370]]

# Mengen
I_max = len(b)
J_max = len(d)

I = range(I_max)
J = range(J_max)

# Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
x = {}
for i in I:
     for j in J:
          x[i,j] = m.addVar(vtype=GRB.CONTINUOUS, name="x_"+str(i)+str(j))
y = {}
for i in I:
     y[i] = m.addVar(vtype=GRB.BINARY, name="y_"+str(i))

# Definition der Zielfunktion
m.setObjective(gp.quicksum(f[i]*y[i] for i in I) + gp.quicksum(c[i][j]*x[i,j] for j in J for i in I), GRB.MINIMIZE)
# m.setObjective(60000*y[0] + 60000*y[1] + 80000*y[2] 
# + 270*x[0,0] + 170*x[0,1] + 400*x[0,2] + 450*x[0,3] + 300*x[0,4]
# + 320*x[1,0] + 280*x[1,1] + 490*x[1,2] + 230*x[1,3] + 120*x[1,4]
# + 120*x[2,0] + 390*x[2,1] + 240*x[2,2] + 230*x[2,3] + 370*x[2,4], GRB.MINIMIZE)

# Hinzufügen der Nebenbedingungen
#for j in J:
#     m.addConstr(gp.quicksum(x[i,j] for i in I) == d[j], "nb_"+str(j))
m.addConstr(x[0,0] + x[1,0] + x[2,0] == 200, "nb_0")
m.addConstr(x[0,1] + x[1,1] + x[2,1] == 250, "nb_1")
m.addConstr(x[0,2] + x[1,2] + x[2,2] == 150, "nb_2")
m.addConstr(x[0,3] + x[1,3] + x[2,3] == 300, "nb_3")
m.addConstr(x[0,4] + x[1,4] + x[2,4] == 100, "nb_4")

#for i in I:
#     m.addConstr(gp.quicksum(x[i,j] for i in I) <= b[i] * y[i], "kb_"+str(j))
m.addConstr(x[0,0] + x[0,1] + x[0,2] + x[0,3] + x[0,4] <= 400 * y[0], "kb_0")
m.addConstr(x[1,0] + x[1,1] + x[1,2] + x[1,3] + x[1,4] <= 350 * y[1], "kb_1")
m.addConstr(x[2,0] + x[2,1] + x[2,2] + x[2,3] + x[2,4] <= 600 * y[2], "kb_2")

# Optimierung
m.optimize()

# Ergebnisausgabe
m.printAttr(GRB.Attr.ObjVal)
m.printAttr(GRB.Attr.X)
