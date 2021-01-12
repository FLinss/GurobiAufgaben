import gurobipy as gp
from gurobipy import GRB
import csv
import os

# Daten einlesen
costPerKm = 0.75
costperH = 45

d=[]
ao=[]
print(os.getcwd())
with open("Tutorien/Tutorium4/Absatzorte.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.DictReader(csv_file)
     for row in csv_reader:
          d.append(int(row["Bedarf"]))
          ao.append(row["Ort"])

b=[]
f=[]
so=[]
with open("Standorte.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.DictReader(csv_file)
     for row in csv_reader:
          b.append(int(row["Kapazität"]))
          f.append(int(row["Fixkosten"]))
          so.append(row["Ort"])


dur=[]
with open("Dauer.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.reader(csv_file)
     next(csv_reader)
     for row in csv_reader:
          rowAsInt = [int(item) for item in row[1:]]
          dur.append(rowAsInt)

dist=[]
with open("Entfernung.csv", encoding="utf-8") as csv_file:
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
               print("Von", so[i], "werden", x[i,j].X, "ME nach", ao[j], "geliefert, die Transportkosten betragen dabei", c[i][j] * x[i,j].X, "GE.")

with open("Ergebnisausgabe.txt", "w", encoding="utf-8") as file:
     file.write("Optimale Standortwahl bei mehreren Betriebsstätten\n\n")
     file.write("Die gesamten Kosten des Transportes betragen " + str(m.getAttr(GRB.Attr.ObjVal)) + " GE.\n")
     for i in I:
          if y[i].X > 0:
               file.write("In " + so[i] + " wird ein Standort errichtet!\n")
          else:
               file.write("In " + so[i] + " wird KEIN Standort errichtet!\n")
     file.write("\n")
     for i in I:
          for j in J:
               if x[i,j].X > 0:
                    file.write("Von " + so[i] + " werden " + str(x[i,j].X) + " ME nach " + ao[j] +
                    " geliefert, die Transportkosten betragen dabei " + str(c[i][j] * x[i,j].X) + " GE.\n")
