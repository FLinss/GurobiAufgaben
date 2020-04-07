import gurobipy as gp
from gurobipy import GRB
import csv

# Daten einlesen
costPerKm = 0.75
costperH = 45

d=[]
ao=[]
with open("Tutorien/Tutorium3/Absatzorte.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.DictReader(csv_file)
     for row in csv_reader:
          d.append(int(row["Bedarf"]))
          ao.append(row["Ort"])

b=[]
f=[]
so=[]
with open("Tutorien/Tutorium3/Standorte.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.DictReader(csv_file)
     for row in csv_reader:
          b.append(int(row["Kapazität"]))
          f.append(int(row["Fixkosten"]))
          so.append(row["Ort"])


dur=[]
with open("Tutorien/Tutorium3/Dauer.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.reader(csv_file)
     next(csv_reader)
     for row in csv_reader:
          rowAsInt = [int(item) for item in row[1:]]
          dur.append(rowAsInt)

dist=[]
with open("Tutorien/Tutorium3/Entfernung.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.reader(csv_file)
     next(csv_reader)
     for row in csv_reader:
          rowAsInt = [int(item) for item in row[1:]]
          dist.append(rowAsInt)

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
          newRow.append(costperH * dur[i][j] + costPerKm * dist[i][j])
     c.append(newRow)

# Kurzform:
# c = [[costperH * dur[i][j] + costPerKm * dist[i][j] for j in J] for i in I]

# Dict ist auch möglich, dann wird c mit c[i,j] indiziert anstelle von c[i][j] - Zielfunktion muss an Dict angepasst werden.
#c = {(i,j) : costperH * dur[i][j] + costPerKm * dist[i][j] for i in I for j in J}


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

# Ergebnisausgabe
m.printAttr(GRB.Attr.ObjVal)
m.printAttr(GRB.Attr.X)