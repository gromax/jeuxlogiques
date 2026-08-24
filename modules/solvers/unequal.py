from typing import List, Tuple
from modules.primitives.direction import Direction
from ortools.sat.python import cp_model

class UnequalSolver:
    S:int # taille
    constraints:List[Tuple[int,int,Direction]] # forme i,j,dir (parmi UDLR)
    knowns:List[Tuple[int,int,int]] # forme i,j,value

    def __init__(self, size:int, constraints:List[Tuple[int,int,str]], knowns:List[Tuple[int,int,int]]):
        self.S = size
        self.knowns = knowns
        self.constraints = constraints

    def solve(self):
        model = cp_model.CpModel()

        # -------------------------
        # cellules
        # -------------------------

        c = {}
        for i in range(self.S):
            for j in range(self.S):
                c[i,j] = model.NewIntVar(1, self.S, f"c_{i}_{j}")

        # valeurs connues
        for i,j,k in self.knowns:
            model.Add(c[i,j] == k)

        # valeurs différentes
        for i in range(self.S):
            model.AddAllDifferent([c[i,j] for j in range(self.S)])
            model.AddAllDifferent([c[j,i] for j in range(self.S)])

        # -------------------------
        # contraintes
        # -------------------------
        for i, j, d in self.constraints:
            di, dj = d.delta()
            ni, nj = i+di, j+dj
            model.Add(c[i,j] > c[ni,nj])

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !!")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [[solver.Value(c[i,j]) for j in range(self.S)] for i in range(self.S)]
        return False