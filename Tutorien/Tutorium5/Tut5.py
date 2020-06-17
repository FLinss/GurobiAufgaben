import gurobipy as gp
from gurobipy import GRB
import csv

# Daten einlesen
costPerKm = 2.5

d=[]
ao=[]
posAo=[]
with open("Absatzorte.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.DictReader(csv_file)
     for row in csv_reader:
          d.append(int(row["Bedarf"]))
          ao.append(row["Ort"])
          posAo.append({"X" : int(row["xKoordinate"]), "Y" : int(row["yKoordinate"])})

b=[]
f=[]
so=[]
posSo=[]
with open("Standorte.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.DictReader(csv_file)
     for row in csv_reader:
          b.append(int(row["Kapazität"]))
          f.append(int(row["Fixkosten"]))
          so.append(row["Ort"])
          posSo.append({"X" : int(row["xKoordinate"]), "Y" : int(row["yKoordinate"])})


# Mengen
I_max = len(b)
J_max = len(d)

I = range(I_max)
J = range(J_max)


# Kostenberechnung
c = []
for i in I:
     newRow = []
     for j in J:
          distance = abs(posSo[i]["X"] - posAo[j]["X"]) + abs(posSo[i]["Y"] - posAo[j]["Y"])
          newRow.append(costPerKm * distance)
     c.append(newRow)

# Kurzform:
#c = [[costPerKm * (abs(posSo[i]["X"] - posAo[j]["X"]) + abs(posSo[i]["Y"] - posAo[j]["Y"])) for j in J] for i in I]

# Ausgabe der Kosten
for row in c:
     print(row)

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

#x = m.addVars(I_max, J_max, vtype=GRB.CONTINUOUS, name="x")
#y = m.addVars(I_max, vtype=GRB.BINARY, name="y")


# Definition der Zielfunktion
m.setObjective(gp.quicksum(f[i]*y[i] for i in I) + gp.quicksum(c[i][j]*x[i,j] for j in J for i in I), GRB.MINIMIZE)

# Hinzufügen der Nebenbedingungen
for j in J:
     m.addConstr(gp.quicksum(x[i,j] for i in I) == d[j], "meet_demand_" + str(j))

for i in I:
     m.addConstr(gp.quicksum(x[i,j] for j in J) <= b[i] * y[i], "meet_prod_" + str(i))

# m.addConstrs((x.sum("*", j) == d[j] for j in J), name="nb")
# m.addConstrs((x.sum(i, "*") == b[i] * y[i] for i in I), name="kb")


# Optimierung
m.optimize()


# Ergebnisausgabe:
print("\nOptimale Standortwahl bei mehreren Betriebsstätten\n")

print("Die gesamten Kosten des Transportes betragen", m.getAttr(GRB.Attr.ObjVal), "GE.")

for i in I:
     if y[i].X > 0:
          print("In", so[i], "wird ein Standort errichtet.")
          print("\tFixkosten:", f[i])
          print("\tVariable Kosten:", sum([c[i][j] * x[i,j].X for j in J]))
     else:
          print("In", so[i], "wird KEIN Standort errichtet.")


for i in I:
     for j in J:
          if x[i,j].X > 0:
               print("Von", so[i], "werden", x[i,j].X, "ME\tnach", ao[j], "geliefert, die Transportkosten betragen dabei", c[i][j] * x[i,j].X, "GE.")

for i in I:
     constr = m.getConstrByName("meet_prod_" + str(i))
     print("Nebenbedingung", constr.getAttr(GRB.Attr.ConstrName), "hat einen Schlupf von", constr.getAttr(GRB.Attr.Slack))
