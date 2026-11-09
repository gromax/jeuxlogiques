from typing import Dict, List, Tuple, Union
from ortools.sat.python import cp_model
from modules.container.norinori import Data
from modules.primitives.cellgroup import CellGroup

class Solver:
    __width:int
    __height:int
    __zones:List[CellGroup]

    def __init__(self, data:Data):
        self.__width = data.width
        self.__height = data.height
        self.__zones = data.zones

    def __neighbors(self, index:int) -> List[int]:
        """
        itérateur
        """
        DELTAS = [(1,0),(-1,0),(0,1),(0,-1)]
        iline = index // self.__width
        icol = index % self.__width
        return [
            (iline+dline)*self.__width + (icol+dcol)
            for (dline,dcol) in DELTAS
            if 0 <= iline + dline < self.__height and 0 <= icol + dcol < self.__width
        ]
    
    def solve(self) -> Union[List[bool], False]:
        N = self.__height * self.__width
        model = cp_model.CpModel()

        # -------------------------
        # Variables cellules
        # -------------------------
        cells = [
            model.new_bool_var(f"cell {i}") for i in range(N)
        ]

        # 2 on par zone
        for z in self.__zones:
            zcells = [cells[iline*self.__width+icol] for (iline,icol) in z.coords()]
            model.Add(sum(zcells) == 2)

        # une cellule on a exactement 1 voisine on
        for index, c in enumerate(cells):
            ncells = [cells[i] for i in self.__neighbors(index)]
            model.Add(sum(ncells)==1).OnlyEnforceIf(cells[index])

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [bool(solver.Value(c)) for c in cells]
        return False
    