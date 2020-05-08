import gurobipy as gp
from gurobipy import GRB
import csv


#### Daten ####

distance=[]
with open("Distanz.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.reader(csv_file)
     for row in csv_reader:
          rowAsInt = [int(item) for item in row]
          distance.append(rowAsInt)

transportAmount=[]
with open("Transport.csv", encoding="utf-8") as csv_file:
     csv_reader = csv.reader(csv_file)
     for row in csv_reader:
          rowAsInt = [int(item) for item in row]
          transportAmount.append(rowAsInt)

#### Mengen ####
numberOfMaschines = len(transportAmount) # oder händisch: 6
maschines = range(numberOfMaschines)
numberOfPlaces = len(distance) # oder händisch: 6
places = range(numberOfPlaces)

# Initialisierung des Modells
m = gp.Model()

# Initialisierung der Variablen
x = m.addVars(numberOfMaschines, numberOfPlaces, vtype=GRB.BINARY, name="x")

#x = {}
#for i in maschines:
#    for j in places:
#        x[i,j] = m.addVar(vtype=GRB.BINARY, name="x"+str(i)+str(j))

# Definition der Zielfunktion
m.setObjective(
    gp.quicksum(
        gp.quicksum(
            gp.quicksum(
                gp.quicksum(
                    transportAmount[h][i] * distance[j][k] * x[h,j] * x[i,k] 
                for i in maschines if i != h)
            for h in maschines) 
        for k in places if k != j) 
    for j in places),
    GRB.MINIMIZE)

# Hinzufügen der Nebenbedingungen
for h in maschines:
    m.addConstr(gp.quicksum(x[h,j] for j in places) == 1, "NB1".format(h))

#m.addConstrs((x.sum(h,'*') == 1 for h in maschines), "NB1")

for j in places:
    m.addConstr(gp.quicksum(x[h,j] for h in maschines) == 1, "NB2[{}]".format(j))

#m.addConstrs((x.sum('*',j) == 1 for j in places), "NB2")

# Optimierung
m.optimize()

# Ergebnisausgabe:

#m.printAttr('ObjVal')
#m.printAttr('X')

print("\nMaschinenzuordnung:\n")

for h in maschines:
    for j in places:
        if x[h,j].X > 0:
            # Extra: Konvertiere Index zu Bezeichnung:
            placeJ = chr(ord('A') + j)
            #Alternativ einfach j ausgeben.
            print("Maschine M" + str(h), "wird Standort", placeJ, "zugeordnet.")

print("\nMaterialfluss:\n")

for h in range(numberOfMaschines-1):
    ''' 
    Um beide Richtungen des Materialsflusses zusammenzufassen werden nur die Werte der oberen Dreiecksmatrix der Distanzen verwendet. 
    Also nur Distanzen bei denen die zweite Maschine einen höheren Index hat als die erste Maschine. 
    Dies ist zulässig, da die Distanzmatrix symmetrisch ist. 
    '''
    for i in range(h+1, numberOfMaschines):
        if i != h:
            for j in places:
                for k in places:
                    if k != j and x[h,j].X * x[i,k].X > 0:
                        print("Zwischen M"+str(h),"und M"+str(i),"fließen", transportAmount[h][i]+transportAmount[i][h], "ME über eine Distanz von", distance[j][k],
                        "EE.")
print("Insgesamter Materialfluss:", m.getAttr(GRB.Attr.ObjVal), "ME*EE")

# Textdatei schreiben
with open("Ergebnis.txt","w", encoding="utf-8") as f:
    f.write("Ergebnis der Layoutgestaltung\n")
    
    f.write("\nMaschinenzuordnung:\n")
    for h in maschines:
        for j in places:
            if x[h,j].X > 0:
                placeJ = chr(ord('A') + j)
                #Alternativ einfach j ausgeben.
                f.write("Maschine M" + str(h) + " wird Standort " + placeJ + " zugeordnet.\n")
    
    f.write("\nMaterialfluss:\n")
    for h in range(numberOfMaschines-1):
        for i in range(h+1, numberOfMaschines):
            if i != h:
                for j in places:
                    for k in places:
                        if k != j and x[h,j].X * x[i,k].X > 0:
                            f.write("Zwischen M" + str(h) + " und M" + str(i) + " fließen " + str(transportAmount[h][i]+transportAmount[i][h])
                            + " ME über eine Distanz von " + str(distance[j][k]) + " EE.\n")
