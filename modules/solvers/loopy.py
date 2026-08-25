from typing import Dict, Tuple, List, Union
from modules.container.loopy import Data
from ortools.sat.python import cp_model

DELTAS = ((1,0),(-1,0),(0,1),(0,-1))
class Solver:
    __width:int
    __height:int
    __clues:Dict[Tuple[int,int],int]

    def __init__(self, data:Data):
        self.__width = data.width
        self.__height = data.height
        self.__clues = data.clues

    def __neighbors(self, i:int, j:int, with_ext:bool) -> List[Tuple[int,int]]:
        """
        voisins
        """
        pos = [(i+di, j+dj) for (di,dj) in DELTAS]
        if with_ext:
            return [(ni,nj) if 0 <= ni < self.__height and 0 <= nj < self.__width else (-1,-1) for (ni,nj) in pos]
        return [(ni,nj) for (ni,nj) in pos if 0 <= ni < self.__height and 0 <= nj < self.__width]

    def __is_border(self, i:int, j:int) -> bool:
        return i==0 or j==0 or i==self.__height-1 or j==self.__width-1

    def solve(self) -> Union[List[bool],False]:
        N = self.__height * self.__width
        model = cp_model.CpModel()

        # -------------------------
        # Variables cellules
        # -------------------------

        cells = {}
        # cellule extérieure
        cells[(-1,-1)] = model.NewBoolVar(f"c_ext")
        model.Add(cells[-1,-1] == False)

        for iline in range(self.__height):
            for icol in range(self.__width):
                cells[iline,icol] = model.NewBoolVar(f"c_{iline}_{icol}")

        # -------------------------
        # contraintes
        # -------------------------
        for (iline,icol), walls in self.__clues.items():
            # si c[i,j] = 0 il faut que cela fasse walls
            # sinon il faut que cela fasse 4-walls
            s = sum(cells[i,j] for i,j in self.__neighbors(iline,icol,True))
            model.Add(s == walls).OnlyEnforceIf(cells[iline,icol].Not())
            model.Add(s == 4-walls).OnlyEnforceIf(cells[iline,icol])

        #-------------------------
        # nombre de cellules in
        #-------------------------
        n_actives = model.NewIntVar(1, N, "size in")
        model.Add(n_actives == sum(cells.values()))

        # -------------------------
        # flux des cases in
        # -------------------------
        # on ne connaît pas la case racine il faut donc des variables pour cela
        root = {}
        for iline in range(self.__height):
            for icol in range(self.__width):
                root[iline,icol] = model.NewBoolVar(f"root_{iline}_{icol}")

        # Une seule racine
        model.Add(sum(root.values()) == 1)

        # La cellule root doit être active
        for iline in range(self.__height):
            for icol in range(self.__width):
                model.Add(root[iline,icol] <= cells[iline,icol])

        # flux
        # il y en aura deux, un pour le in et un pour le out
        f_in = {}
        for iline in range(self.__height):
            for icol in range(self.__width):
                for niline,nicol in self.__neighbors(iline,icol,False):
                    # flux pour in
                    f_in[iline,icol,niline,nicol] = model.NewIntVar(0, N, f"f_in({iline},{icol})->({niline},{nicol})")
                    # flux seulement entre cellules actives
                    model.Add(f_in[iline,icol,niline,nicol] <= N * cells[iline,icol])
                    model.Add(f_in[iline,icol,niline,nicol] <= N * cells[niline,nicol])

        f_out = {}
        for iline in range(self.__height):
            for icol in range(self.__width):
                for niline,nicol in self.__neighbors(iline,icol, False):
                    # flux pour out
                    f_out[iline,icol,niline,nicol] = model.NewIntVar(0, N, f"f_out({iline},{icol})->({niline},{nicol})")
                    # flux seulement entre cellules inactives
                    model.Add(f_out[iline,icol,niline,nicol] <= N * cells[iline,icol].Not())
                    model.Add(f_out[iline,icol,niline,nicol] <= N * cells[niline,nicol].Not())
                if self.__is_border(iline,icol):
                    # flux venant du bord
                    f_out[-1,-1,iline,icol] = model.NewIntVar(0, N, f"f_out(ext)->({iline},{icol})")
                    # flux seulement vers cellules inactives
                    model.Add(f_out[-1,-1,iline,icol] <= N * cells[iline,icol].Not())

        # -------------------------
        # conservation du flux
        # -------------------------

        # pour le flux in
        for iline in range(self.__height):
            for icol in range(self.__width):
                incoming = []
                outgoing = []

                for niline,nicol in self.__neighbors(iline,icol,False):
                    incoming.append(f_in[niline,nicol,iline,icol])
                    outgoing.append(f_in[iline,icol,niline,nicol])

                delta = sum(incoming) - sum(outgoing)
                model.Add(delta == 1 - n_actives).OnlyEnforceIf(root[iline,icol])
                model.Add(delta == cells[iline,icol]).OnlyEnforceIf(root[iline,icol].Not())

        # pour le flux out, le root est (-1,-1)
        outgoing_root = []
        for iline in range(self.__height):
            for icol in range(self.__width):
                incoming = []
                outgoing = []
                for niline,nicol in self.__neighbors(iline,icol,False):
                    incoming.append(f_out[niline,nicol,iline,icol])
                    outgoing.append(f_out[iline,icol,niline,nicol])
                if self.__is_border(iline,icol):
                    incoming.append(f_out[-1,-1,iline,icol])
                    outgoing_root.append(f_out[-1,-1,iline,icol])
                delta = sum(incoming) - sum(outgoing)
                model.Add(delta == cells[iline,icol].Not())
        # racine
        model.Add(-sum(outgoing_root) == 1 - (N+1) + n_actives)

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [bool(solver.Value(cells[i//self.__width,i%self.__width])) for i in range(N)]
        return False