"""
Ceci est un exemple chat-gpt de résolution avec or-sat
avec une problématique de connexité
"""

from ortools.sat.python import cp_model

H = 5
W = 5

model = cp_model.CpModel()

# Variables cellule
# Dans ce problème les cases doivent être à 1 ou 0
# selon si elles sont à l'intérieur ou à l'extérieur
x = {}
for i in range(H):
    for j in range(W):
        x[i,j] = model.NewBoolVar(f"x_{i}_{j}")

# Variables racine
# les cases à 1 doivent être connexes. Il faut donc vérifier la connexité.
# Pour cela on utilise une méthode dite de flux
# et il faux une cellule de départ.
root = {}
for i in range(H):
    for j in range(W):
        root[i,j] = model.NewBoolVar(f"root_{i}_{j}")

# Une seule racine
# il ne doit y avoir qu'une seule racine
model.Add(sum(root.values()) == 1)

# La racine doit être active
# en effet, la contrainte pécédentes fixe qu'il y a une certaine cellule
# [i,j] qui est True. En fixant root[i,j] <= x[i,j], on a
# forcément pour la root x[i,j] == True
for i in range(H):
    for j in range(W):
        model.Add(root[i,j] <= x[i,j])

# Fonction voisins
# il s'agit d'un générateur. C'est le rôle de yield
# ainsi on pourra faire quelque chose comme
# for i2, j2 in neignbors(i,j)
def neighbors(i,j):
    for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]:
        ni = i+di
        nj = j+dj
        if 0 <= ni < H and 0 <= nj < W:
            yield ni,nj

# L'idée du flux est que l'on choisit une cellule racine r
# (r vaut pour une paire de coords)
# et le flux est une valriable f(u->v) [u et v aussi coords]
# représentant le flux d'eau de u à v

# le flux représente la quantité de celulles qui seront arrosée par une cellule donnée
# donc au min c'est 0 et au max c'est HW (et même HW-1)

# la contrainte avant dernière ci-dessous indique que seule une cellule active a un flux sortant
# en effet si x[i,j] = 0, on aura f[i,j]->[i2,j2] <= 0
# et la dernière indique que seule une cellule active a un flux entrant
# en effet si x[i2,j2] = 0, on aura f[i,j]->[i2,j2] <= 0

# Variables flux
f = {}
for i in range(H):
    for j in range(W):
        for ni,nj in neighbors(i,j):
            f[i,j,ni,nj] = model.NewIntVar(0, H*W, f"f_{i}_{j}_{ni}_{nj}")

            # flux seulement entre cellules actives
            model.Add(f[i,j,ni,nj] <= H*W * x[i,j])
            model.Add(f[i,j,ni,nj] <= H*W * x[ni,nj])

# on veut une variable représentant le nombre d'actives.
# on la crée donc
# Nombre total de cellules actives
total_active = model.NewIntVar(0, H*W, "total_active")
model.Add(total_active == sum(x.values()))


# on impose déjà la conservation de flux : flux entrant - flux sortant = 1
# sauf pour la racine

# on voit ici que si [i,j] n'est ni root ni active,
# de toute façon, incoming et outgoing valent 0 et on a bien 0 == 0
# si [i,j] est active mais par root, la contrainte devient
# in - out == 1
# enfin si [i,j] est root, elle est forcément active
# donc la contrainte devient
# in - out = 1 - Nactive

# Conservation du flux
for i in range(H):
    for j in range(W):

        incoming = []
        outgoing = []

        for ni,nj in neighbors(i,j):
            incoming.append(f[ni,nj,i,j])
            outgoing.append(f[i,j,ni,nj])

        incoming_sum = sum(incoming)
        outgoing_sum = sum(outgoing)

        # cellule normale
        model.Add(incoming_sum - outgoing_sum == x[i,j] - root[i,j] * total_active)

# Ainsi, comme chaque cellule conserve 1 pour elle et que root produit N-1, 
# si la contrainte est satisfaite c'est forcément que toute les active reçoivent du flux

# Solve
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10

status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for i in range(H):
        row = []
        for j in range(W):
            row.append(solver.Value(x[i,j]))
        print(row)