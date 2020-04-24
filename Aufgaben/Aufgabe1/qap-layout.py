import gurobipy as gp
from gurobipy import GRB


#### Mengen ####
numberOfMaschines = 6
maschines = range(numberOfMaschines)
numberOfPlaces = 6
places = range(numberOfPlaces)


#### Daten ####

distance = [[0, 4, 7, 3, 4, 8],
            [4, 0, 3, 5, 8, 4],
            [7, 3, 0, 4, 7, 3],
            [3, 5, 4, 0, 3, 5],
            [4, 8, 7, 3, 0, 4],
            [8, 4, 3, 5, 4, 0]]

'''
distance = [[0, 4, 7, 3, 4, 8],
            [4, 0, 3, 5, 8, 4],
            [7, 3, 0, 4, 7, 3],
            [3, 5, 4, 0, 3, 5],
            [4, 8, 7, 3, 0, 4],
            [8, 4, 3, 5, 4, 0]]
distance2 = [[0, 1, 1, 2, 2], 
            [1, 0, 2, 1, 3],
            [1, 2, 0, 1, 1],
            [2, 1, 1, 0, 2],
            [2, 3, 1, 2, 0]]
distance = [[0, 1, 1],
            [1, 0, 2],
            [1, 2, 0]]
'''

transportAmount = [[0, 3, 6, 9, 8, 3],
                   [3, 0, 2, 1, 3, 2],
                   [6, 2, 0, 4, 0, 1],
                   [9, 1, 4, 0, 3, 4],
                   [8, 3, 0, 3, 0, 5],
                   [3, 2, 1, 4, 5, 0]]
'''
transportAmount2 = [[0, 4, 5, 2, 1],
                   [4, 0, 2, 3, 0],
                   [5, 2, 0, 0, 6],
                   [2, 3, 0, 0, 1],
                   [1, 0, 6, 1, 0]]
transportAmount = [[0, 2, 3],
                   [2, 0, 1],
                   [3, 1, 0]]
'''

m = gp.Model()

x = m.addVars(numberOfMaschines, numberOfPlaces, vtype=GRB.BINARY, name="x")

#x = {}
#for i in maschines:
#    for j in places:
#        x[i,j] = m.addVar(vtype=GRB.BINARY, name="x[{},{}]".format(i,j))


# Integrierung der Variablen
m.update()

# Asymmetrisch:
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

for h in maschines:
    m.addConstr(gp.quicksum(x[h,j] for j in places) == 1, "NB1[{}]".format(h))

#m.addConstrs((x.sum(h,'*') == 1 for h in maschines), "NB1")

for j in places:
    m.addConstr(gp.quicksum(x[h,j] for h in maschines) == 1, "NB2[{}]".format(j))

#m.addConstrs((x.sum('*',j) == 1 for j in places), "NB2")

#m.addConstr(x[0,3] == 1)
#m.addConstr(x[1,2] == 1)
#m.addConstr(x[2,1] == 1)
#m.addConstr(x[3,4] == 1)
#m.addConstr(x[4,0] == 1)
#m.addConstr(x[5,5] == 1)

m.write("A1.lp")
m.optimize()

m.printAttr('ObjVal')
m.printAttr('X')

print("\nMaschinenzuordnung:\n")

for h in maschines:
    for j in places:
        if x[h,j].X > 0:
            # Extra: Konvertiere Index zu Bezeichnung:
            placeJ = chr(ord('A') + j)
            #Alternativ einfach j ausgeben.
            print("Maschine M{} wird Standort {} zugeordnet.".format(h, placeJ))

print("\nMaterialfluss:\n")

material=0
for h in range(numberOfMaschines-1):
    for i in range(h+1, numberOfMaschines):
        if i != h:
            for j in places:
                for k in places:
                    if k != j and x[h,j].X * x[i,k].X > 0:
                        print("Zwischen M{} und M{} fließen {} ME über eine Distanz von {} EE".format(
                            h, i, transportAmount[h][i]+transportAmount[i][h], distance[j][k]))
                        material += (transportAmount[h][i]) * distance[j][k]
print("Insgesamter Materialfluss: {} ME*EE".format(m.getAttr(GRB.Attr.ObjVal)),"\n")
print(material)
