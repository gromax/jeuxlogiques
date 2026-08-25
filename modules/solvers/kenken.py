from ortools.sat.python import cp_model
from typing import Tuple, List, Union

class Solver:
    S:int # taille
    constraints:List[Tuple[List[Tuple[int, int]], str, int]] # forme [ ( [(i,j), ...], op, k), ... ]

    def __init__(self, size:int, constraints:List[Tuple[List[Tuple[int, int]], str, int]]):
        self.S = size
        self.constraints = constraints
    
    def solve(self) -> Union[List[List[int]], False]:
        model = cp_model.CpModel()
        # -------------------------
        # cellules
        # -------------------------

        c = {}
        for i in range(self.S):
            for j in range(self.S):
                c[i,j] = model.NewIntVar(1, self.S, f"c_{i}_{j}")

        # valeurs différentes
        for i in range(self.S):
            model.AddAllDifferent([c[i,j] for j in range(self.S)])
            model.AddAllDifferent([c[j,i] for j in range(self.S)])

        # -------------------------
        # contraintes
        # -------------------------
        for cellscoords, op, k in self.constraints:
            cells = [c[i,j] for (i,j) in cellscoords]
            if op == 'a':
                model.Add(sum(cells) == k)
            elif op == 's':
                assert len(cells) == 2, "contraintes de soustraction seulement pour 2 cellules"
                a, b = cells
                diff = model.NewIntVar(-self.S, self.S, "diff")
                model.Add(diff == a - b)
                model.AddAbsEquality(k, diff) 
            elif op == 'm':
                # on introduit une variable pour le produit
                prod = model.NewIntVar(1,self.S**len(cells), "prod")
                model.AddMultiplicationEquality(prod, cells)
                model.Add(prod == k)
            elif op == 'd':
                assert len(cells) == 2, "contraintes de division seulement pour 2 cellules"
                # on introduit une variable pour le quotient
                a, b = cells
                c1 = model.NewBoolVar("a_eq_kb")
                c2 = model.NewBoolVar("b_eq_ka")
                model.Add(a == k * b).OnlyEnforceIf(c1)
                model.Add(b == k * a).OnlyEnforceIf(c2)
                model.AddBoolOr([c1, c2])

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