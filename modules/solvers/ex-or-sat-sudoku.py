"""
Ceci est un exemple chat-gpt de résolution d'un sudoku
avec le module or-sat de google
"""

from ortools.sat.python import cp_model

model = cp_model.CpModel()

N = 9

# Variables
# on commence par créer des variables entières pouvant prendre de 1 à 9 pour chaque case
grid = [[model.NewIntVar(1, 9, f"x[{i},{j}]") for j in range(N)] for i in range(N)]

# Lignes
# on ajoute la contrainte que toutes les cellules soient différentes sur les lignes
for i in range(N):
    model.AddAllDifferent(grid[i])

# Colonnes
# même chose pour les colonnes
for j in range(N):
    model.AddAllDifferent([grid[i][j] for i in range(N)])

# Blocs 3x3
# même chose pour les zones
for bi in range(3):
    for bj in range(3):
        block = []
        for i in range(3):
            for j in range(3):
                block.append(grid[3*bi+i][3*bj+j])
        model.AddAllDifferent(block)

# Exemple de valeur donnée
# une contrainte directe fixant une valeur
model.Add(grid[0][0] == 5)

# lancement de la résolution
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    for i in range(N):
        print([solver.Value(grid[i][j]) for j in range(N)])