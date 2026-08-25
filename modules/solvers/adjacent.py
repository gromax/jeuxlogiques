from typing import List, Union
from modules.primitives.direction import Direction
from ortools.sat.python import cp_model
from modules.container.adjacent import Data

class Solver:
    data:Data # informations de jeu
    def __init__(self, data:Data):
        self.data = data

    def __enforce_adj_constraint(self, model, c, i:int, j:int, down:bool):
        tag = "down" if down else "right"
        (di, dj) = (1,0) if down else (0,1)
        b1 = model.NewBoolVar(f"adj{i}_{j}_{tag}_1")
        b2 = model.NewBoolVar(f"adj{i}_{j}_{tag}_2")

        model.Add(c[i,j] - c[i+di,j+dj] == 1).OnlyEnforceIf(b1)
        model.Add(c[i,j] - c[i+di,j+dj] != 1).OnlyEnforceIf(b1.Not())

        model.Add(c[i,j] - c[i+di,j+dj] == -1).OnlyEnforceIf(b2)
        model.Add(c[i,j] - c[i+di,j+dj] != -1).OnlyEnforceIf(b2.Not())

        model.AddBoolOr([b1, b2])

    def __enforce_not_adj_constraint(self, model, c, i:int, j:int, down:bool):
        tag = "down" if down else "right"
        (di, dj) = (1,0) if down else (0,1)
        model.Add(c[i,j] - c[i+di,j+dj] != 1)
        model.Add(c[i,j] - c[i+di,j+dj] != -1)

    def solve(self) -> Union[List[int], False]:
        model = cp_model.CpModel()
        S = self.data.size
        # -------------------------
        # cellules
        # -------------------------

        c = {}
        for i in range(self.data.size):
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
        for i in range(S-1):
            for j in range(S):
                if self.data.constraints[i,j,Direction.DOWN]:
                    self.__enforce_adj_constraint(model, c, i, j, True)
                else:
                    self.__enforce_not_adj_constraint(model, c, i, j, True)
                
        for i in range(S):
            for j in range(S-1):
                if self.data.constraints[i,j,Direction.RIGHT]:
                    self.__enforce_adj_constraint(model, c, i, j, False)
                else:
                    self.__enforce_not_adj_constraint(model, c, i, j, False)

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