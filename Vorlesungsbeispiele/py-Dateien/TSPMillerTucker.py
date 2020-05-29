# Modified example of the gurobi TSP example.

import sys
import math
import random
import gurobipy as gp
from gurobipy import GRB


# Ermittlung der Tour aus gegebenen Kanten
def tour(edges):
    unvisited = list(range(n))
    thiscycle = []
    neighbors = unvisited
    while unvisited: # Solange erfüllt, wie Elemente in unvisited sind
        current = neighbors[0]
        thiscycle.append(current)
        unvisited.remove(current)
        neighbors = [j for i, j in edges.select(current, '*')
                        if j in unvisited]
    return thiscycle


# Argument einlesen
if len(sys.argv) < 2:
    print('Usage: tsp.py npoints')
    sys.exit(1)
n = int(sys.argv[1])

# Erzeuge n zufällige Punkte (bzw. Knoten)

random.seed(1)
points = [(random.randint(0, 100), random.randint(0, 100)) for i in range(n)]

# Dictionary für euklidische Distanzen zwischen den Knoten

dist = {(i, j):
        math.sqrt(sum((points[i][k]-points[j][k])**2 for k in range(2)))
        for i in range(n) for j in range(n) if j != i}

m = gp.Model()

# Erzeuge Variablen

# Jede Kante (i,j) wird durch eine binäre Entscheidungsvariable vars[i,j] repräsentiert
vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')

# Jeder Knoten (außer der erste) bekommt eine ganzzahlige Variable zur Unterbindung von Subzyklen
uVars = m.addVars(range(1,n), ub=n, vtype=GRB.INTEGER,name='u')


# Nebenbedingungen:

# Jeder Knoten darf genau eine ausgehende Kante haben
m.addConstrs(vars.sum(i, '*') == 1 for i in range(n))
# Jeder Knoten darf genau eine eingehende Kante haben
m.addConstrs(vars.sum('*', j) == 1 for j in range(n))

# Unterbindung der Subzyklen:
for i in range(1,n):
    for j in range(1,n):
        if i!=j:
            m.addConstr(uVars[i] - uVars[j] + n * vars[i,j] + (n-2) * vars[j,i] <= n - 1)

# Optimierung des Modells:

m.Params.threads = 2
#m.Params.timeLimit = 300

m.optimize()
m.printAttr("X")

# Ermittlung der optimalen Tour:

vals = m.getAttr('x', vars) # Gibt Tupledict zurück jedoch sind die Values nun das Attribut X des Keys (i,j).
selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)
# selected beinhaltet alle Kanten, die in der Lösung vorhanden sind
tour = tour(selected)
assert len(tour) == n

print('')
print('Optimal tour: %s' % str(tour))
print('Optimal cost: %g' % m.objVal)
print('')

# Visualisierung

import matplotlib.pyplot as plt
tour = tour + [tour[0]]
plt.figure(figsize=(4,3),dpi=150) # Definition der Größe und Auflösung
# Zeichnen der Tourkanten:
for i in range(len(tour)-1):
    cur=tour[i]
    nex=tour[i+1]
    plt.plot([points[cur][0],points[nex][0]],[points[cur][1],points[nex][1]],'k-',lw=1) # k- bedeutet schwarz, durchgezogene Linie mit Stärke (lw) gleich 1
# Zeichnen der Knoten:
for i in range(len(tour)):
    plt.plot(points[tour[i]][0],points[tour[i]][1],'ro',markersize=5) # Rote, Kreise mit Stärke 5
plt.grid()
plt.autoscale()
plt.show()
