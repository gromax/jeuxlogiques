from typing import List, Tuple, Dict, Union
from ortools.sat.python import cp_model
from modules.container.towers import Data

class Solver:
    data:Data # informations de jeu
    def __init__(self, data:Data):
        self.data = data

    def solve(self) -> Union[List[int], False]:
        model = cp_model.CpModel()
        S = self.data.size

        # -------------------------
        # cellules
        # -------------------------

        c = {}
        for i in range(S):
            for j in range(S):
                c[i,j] = model.NewIntVar(1, S, f"c_{i}_{j}")

        # valeurs connues
        for (i,j) in self.data.knowns:
            model.Add(c[i,j] == self.data.knowns[i,j])

        # valeurs différentes
        for i in range(S):
            model.AddAllDifferent([c[i,j] for j in range(S)])
            model.AddAllDifferent([c[j,i] for j in range(S)])

        # -------------------------
        # contraintes
        # -------------------------
        # booléens disant qu'une case est supérieure à une autre
        sup = {}
        for index in range(S**2):
            i, j = index//S, index%S
            for index2 in range(S**2):
                if index == index2:
                    continue
                i2, j2 = index2//S, index2%S
                if i2 != i and j2 != j:
                    continue
                sup[i,j,i2,j2] = model.NewBoolVar(f"({i},{j})>({i2},{j2})")
                model.Add(c[i,j] > c[i2,j2]).OnlyEnforceIf(sup[i,j,i2,j2])
                model.Add(c[i,j] < c[i2,j2]).OnlyEnforceIf(sup[i,j,i2,j2].Not())

        # créer pour chaque case et dans chaque direction une variable disant si elle est la plus grande dans cette direction
        # (starti, startj,di,dj) top, bottom, left, right
        sights = [(0,j,1,0) for j in range(S)] + \
                 [(S-1,j,-1,0) for j in range(S)] + \
                 [(i,0,0,1) for i in range(S)] + \
                 [(i,S-1,0,-1) for i in range(S)]
        
        for (starti, startj, di, dj), clue in zip(sights, self.data.clues):
            if clue <= 0:
                continue
            seens = []
            for k in range(0,S):
                i = starti + di*k
                j = startj + dj*k
                s = model.NewBoolVar(f"({i},{j})_seen_from_({starti-di},{startj-dj})")
                if k == 0:
                    model.Add(s == True)
                else:
                    in_front_of_ij = [sup[i,j,i-m*di,j-m*dj] for m in range(1,k+1) ]
                    in_front_of_ij_not = [sup[i,j,i-m*di,j-m*dj].Not() for m in range(1,k+1) ]
                    model.AddBoolAnd(in_front_of_ij).OnlyEnforceIf(s)
                    model.AddBoolOr(in_front_of_ij_not).OnlyEnforceIf(s.Not())
                seens.append(s)
            model.Add(sum(seens) == clue)

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !!")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [solver.Value(c[index//S,index%S]) for index in range(S**2)]
        return False