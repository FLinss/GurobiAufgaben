import gurobipy as gp
from gurobipy import GRB

#### Mengen ####
K_max = 8
J_max = 2
I_max = 3
Z_max = 3 # Vorlaufperioden: 0, 1, 2

K = range(K_max)
J = range(J_max)
I = range(I_max)
Z = range(Z_max)


#### Daten ####
kL = [20,50]
u = [7,8,9]
 
r = [[0,45,30,40,30,50,10,60],
	 [0,0,25,30,25,30,20,30]]
	
b = [[100,100,100,100,100,100,100,100],
	 [150,150,150,150,150,150,150,150],
	 [120,120,120,120,120,120,120,120]]
	
f = [[[1,0,0],[0,4,0],[0,0,0]],
	 [[2,0,0],[0,3,0],[0,4,3]]]

Umax = [[100,100,100,100,100,100,100,100],
     [100,100,100,100,100,100,100,100],
	 [100,100,100,100,100,100,100,100]]

# Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
x = m.addVars(J_max, K_max, vtype=GRB.INTEGER, name="x")
xL = m.addVars(J_max, K_max, vtype=GRB.INTEGER, name="xL")
U = m.addVars(I_max, K_max, vtype=GRB.INTEGER, name="U")

# Definition der Zielfunktion
m.setObjective(
    gp.quicksum(kL[j] * xL[j,k] for j in J for k in K) 
    + gp.quicksum(u[i] * U[i,k] for i in I for k in K),
    GRB.MINIMIZE)

# Hinzufügen der Nebenbedingungen
for j in J:
    m.addConstr(xL[j,0] == x[j,0] - r[j][0], name="LAE"+str(j))

for j in J:
    for k in K: 
        if k > 0:
            m.addConstr(xL[j,k] == xL[j,k-1] + x[j,k] - r[j][k], name="LB"+str(j)+str(k))

for i in I:
    for k in K:
        if k <= K_max-Z_max:
            m.addConstr(gp.quicksum(f[j][i][z] * x[j,k+z] for j in J for z in Z) - U[i,k] <= b[i][k], name="Kap"+str(i)+str(k))


for k in K:
    for i in I:
        m.addConstr(U[i,k] <= Umax[i][k], name="Zusatz"+str(k)+str(i))

# Optimierung
m.optimize()

# Ergebnisausgabe:
m.printAttr("objVal")
m.printAttr("X")

print("\nErgebnisse der Hauptproduktionsprogrammplanung \n")
print("Die minimalen Kosten betragen", m.getAttr(GRB.Attr.ObjVal),"GE.")

for j in J:
        for k in K:
            print("Von Produkt", j, "wird in Periode", k, " ", x[j,k].X, "Einheiten hergestellt.")

# Kapazitätsschlupf    
for k in K:
    if k <= K_max - Z_max:
        capaConstr = m.getConstrByName("Kap0"+str(k))
        print("In Periode", k, "weist die Kapazität einen Schlupf von", capaConstr.Slack, "ME auf.")

# Überstunden
overtime = sum(U[i,k].X for i in I for k in K)
print("Insgesamt wurden", overtime, "Überstunden gemacht.")

#Lagerkosten
storageCosts = sum(xL[j,k].X * kL[j] for j in J for k in K)
print("Die Lagerkosten betragen insgesamt", storageCosts, "GE.")
