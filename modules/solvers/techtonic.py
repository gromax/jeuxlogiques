from ortools.sat.python import cp_model
from typing import Tuple, List, Union, Dict
from modules.primitives.cellgroup import CellGroup

class TechtonicSolver:
    __width:int # largeur
    __height:int # hauteur
    __numbers:Dict[Tuple[int,int],int]
    __zones:List[CellGroup]

    def __init__(self, width:int, height:int, numbers:Dict[Tuple[int, int], int], zones:List[CellGroup]):
        self.__width = width
        self.__height = height
        self.__numbers = numbers
        self.__zones = zones

    def __neighbors(self, i:int, j:int) -> List[Tuple[int,int]]:
        deltas = [(-1,-1), (-1,0), (-1,1),
                  ( 0,-1),          ( 0,1),
                  ( 1,-1), ( 1,0),  ( 1,1)]
        return [(i+di, j+dj) for di,dj in deltas if 0 <= i+di < self.__height and 0 <= j+dj < self.__width]

    def solve(self) -> Union[List[List[int]], False]:
        model = cp_model.CpModel()
        # -------------------------
        # cellules
        # -------------------------
        c = {}
        for z in self.__zones:
            L = []
            S = z.size
            for i,j in z.coords():
                c[i,j] = model.NewIntVar(1, S, f"c_{i}_{j}")
                if (i,j) in self.__numbers:
                    model.Add(c[i,j] == self.__numbers[i,j])
                L.append(c[i,j])
            model.AddAllDifferent(L)

        # -------------------------
        # voisinage
        # -------------------------
        for i in range(self.__height):
            for j in range(self.__width):
                for (ni,nj) in self.__neighbors(i,j):
                    model.Add(c[i,j] != c[ni,nj])

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !!")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [[solver.Value(c[i,j]) for j in range(self.__width)] for i in range(self.__height)]
        return False