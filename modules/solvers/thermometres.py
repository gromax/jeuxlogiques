from typing import List, Union
from ortools.sat.python import cp_model
from modules.container.thermometres import Data

class Solver:
    data:Data # informations de jeu
    def __init__(self, data:Data):
        self.data = data

    def solve(self) -> Union[List[bool], False]:
        model = cp_model.CpModel()
        W = self.data.width
        H = self.data.height

        # -------------------------
        # cellules
        # -------------------------

        c = {}
        for i in range(H):
            for j in range(W):
                c[i,j] = model.NewBoolVar(f"c_{i}_{j}")

        # -------------------------
        # indices latéraux
        # -------------------------

        for i in range(H):
            model.Add(sum(c[i,j] for j in range(W)) == self.data.right[i])
        for j in range(W):
            model.Add(sum(c[i,j] for i in range(H)) == self.data.top[j])

        # -------------------------
        # bonne continuité des thermomètres
        # -------------------------
        for thermo in self.data.thermometres:
            for index in range(len(thermo)-1):
                i,j = thermo[index]
                ni,nj = thermo[index+1]
                # si c[ni,nj] => c[i,j]
                model.Add(c[i,j]==True).OnlyEnforceIf(c[ni,nj])
                # not c[i,j] => not c[ni,nj] est la contraposée.
                # inutile de l'ajouter

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !!")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [bool(solver.Value(c[index//W,index%W])) for index in range(H*W)]
        return False