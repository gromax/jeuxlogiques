from typing import Dict, Tuple

from ortools.sat.python import cp_model

class LoopySolver:
    __size:int
    __constraints:Dict[Tuple[int,int],int]

    def __init__(self, size:int, constraints:Dict[Tuple[int,int], int]):
        self.__size = size
        self.__constraints = constraints

    def __neighbors(self, i:int, j:int):
        """
        itérateur
        """
        for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]:
            ni = i+di
            nj = j+dj
            if 0 <= ni < self.__size and 0 <= nj < self.__size:
                yield ni,nj
    
    def __neighbors_with_ext(self, i:int, j:int):
        """
        itérateur
        """
        for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]:
            ni = i+di
            nj = j+dj
            # ajout de cases fictives autour
            if -1 <= ni <= self.__size and -1 <= nj <= self.__size:
                yield ni,nj

    def solve(self):
        N = self.__size**2
        model = cp_model.CpModel()

        # -------------------------
        # Variables cellules
        # -------------------------

        cells = {}
        for i in range(-1,self.__size+1):
            for j in range(-1,self.__size+1):
                cells[i,j] = model.NewBoolVar(f"c_{i}_{j}")
                if not(0<= i < self.__size and 0 <= j < self.__size):
                    model.Add(cells[i,j] == False)

        # -------------------------
        # contraintes
        # -------------------------
        for (iline,icol),walls in self.__constraints.items():
            # si c[i,j] = 0 il faut que cela fasse walls
            # sinon il faut que cela fasse 4-walls
            s = sum(cells[i,j] for i,j in self.__neighbors_with_ext(iline,icol))
            model.Add( s == walls).OnlyEnforceIf(cells[iline,icol].Not())
            model.Add( s == 4-walls).OnlyEnforceIf(cells[iline,icol])

        #-------------------------
        # nombre de cellules in
        #-------------------------
        n_actives = model.NewIntVar(1, N, f"size")
        model.Add(n_actives == sum(cells.values()))

        # -------------------------
        # flux des cases in
        # -------------------------
        # on ne connaît pas la case racine il faut donc des variables pour cela
        root = {}
        for i in range(self.__size):
            for j in range(self.__size):
                root[i,j] = model.NewBoolVar(f"root_{i}_{j}")

        # Une seule racine
        model.Add(sum(root.values()) == 1)

        # La cellule root doit être active
        for i in range(self.__size):
            for j in range(self.__size):
                model.Add(root[i,j] <= cells[i,j])

        # flux
        # il y en aura deux, un pour le in et un pour le out
        f_in = {}
        for i in range(self.__size):
            for j in range(self.__size):
                for ni,nj in self.__neighbors(i,j):
                    # flux pour in
                    f_in[i,j,ni,nj] = model.NewIntVar(0, N, f"f_in_{i}_{j}_{ni}_{nj}")
                    # flux seulement entre cellules actives
                    model.Add(f_in[i,j,ni,nj] <= N * cells[i,j])
                    model.Add(f_in[i,j,ni,nj] <= N * cells[ni,nj])

        f_out = {}
        for i in range(-1,self.__size+1):
            for j in range(-1,self.__size+1):
                for ni,nj in self.__neighbors_with_ext(i,j):
                    # flux pour out
                    f_out[i,j,ni,nj] = model.NewIntVar(0, N, f"f_out_{i}_{j}_{ni}_{nj}")
                    # flux seulement entre cellules inactives
                    model.Add(f_out[i,j,ni,nj] <= N * cells[i,j].Not())
                    model.Add(f_out[i,j,ni,nj] <= N * cells[ni,nj].Not())

        # -------------------------
        # conservation du flux
        # -------------------------

        # pour le flux in
        for i in range(self.__size):
            for j in range(self.__size):
                incoming = []
                outgoing = []

                for ni,nj in self.__neighbors(i,j):
                    incoming.append(f_in[ni,nj,i,j])
                    outgoing.append(f_in[i,j,ni,nj])

                incoming_sum = sum(incoming)
                outgoing_sum = sum(outgoing)

                model.Add(incoming_sum - outgoing_sum == 1 - n_actives).OnlyEnforceIf(root[i,j])
                model.Add(incoming_sum - outgoing_sum == cells[i,j]).OnlyEnforceIf(root[i,j].Not())

        # pour le flux out, le root est (-1,-1)
        for i in range(-1,self.__size+1):
            for j in range(-1,self.__size+1):
                incoming = []
                outgoing = []

                for ni,nj in self.__neighbors_with_ext(i,j):
                    incoming.append(f_out[ni,nj,i,j])
                    outgoing.append(f_out[i,j,ni,nj])

                incoming_sum = sum(incoming)
                outgoing_sum = sum(outgoing)

                if (i,j) != (-1,-1):
                    # cellule normale
                    model.Add(incoming_sum - outgoing_sum == cells[i,j].Not())
                else:
                    # racine
                    N2 = (self.__size+2)**2
                    model.Add(incoming_sum - outgoing_sum == 1 - N2 + n_actives)

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [[solver.Value(cells[i,j]) for j in range(self.__size)] for i in range(self.__size)]
        return False