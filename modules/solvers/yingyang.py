from typing import Dict, Tuple, Union

from ortools.sat.python import cp_model

class YingyangSolver:
    __size:int
    __content:Dict[Tuple[int,int],bool]

    def __init__(self, size:int, content:Dict[Tuple[int,int], bool]):
        self.__size = size
        self.__content = content

    def __neighbors(self, i:int, j:int):
        """
        itérateur
        """
        for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]:
            ni = i+di
            nj = j+dj
            if 0 <= ni < self.__size and 0 <= nj < self.__size:
                yield ni,nj
    
    def __get_white(self) -> Tuple[int,int]:
        """
        retourne une case blanche
        """
        for (i,j),v in self.__content.items():
            if v is True:
                return i,j
        raise ValueError("aucune case blanche")


    def __get_black(self) -> Tuple[int,int]:
        """
        retourne une case noire
        """
        for (i,j),v in self.__content.items():
            if v is False:
                return i,j
        raise ValueError("aucune case noire")


    def solve(self) -> Union[Dict[Tuple[int,int],bool], False]:
        N = self.__size**2
        model = cp_model.CpModel()

        # -------------------------
        # Variables cellules
        # -------------------------

        whites = {}
        for i in range(self.__size):
            for j in range(self.__size):
                whites[i,j] = model.NewBoolVar(f"w_{i}_{j}")
                if (i,j) not in self.__content:
                    continue
                model.Add(whites[i,j] == self.__content[i,j])

        #-----------------------------
        # nombre de cellules whites 
        #-----------------------------
        n_whites = model.NewIntVar(1, N, f"size")
        model.Add(n_whites == sum(whites.values()))

        # -------------------------
        # flux des cases whites
        # -------------------------
        # il y a toujours une case blanche qui servira de racine
        f_white = {}
        for i in range(self.__size):
            for j in range(self.__size):
                for ni,nj in self.__neighbors(i,j):
                    # flux pour white
                    f_white[i,j,ni,nj] = model.NewIntVar(0, N, f"f_white_{i}_{j}_{ni}_{nj}")
                    # flux seulement entre cellules blanches
                    model.Add(f_white[i,j,ni,nj] <= N * whites[i,j])
                    model.Add(f_white[i,j,ni,nj] <= N * whites[ni,nj])
    
        f_black = {}
        for i in range(self.__size):
            for j in range(self.__size):
                for ni,nj in self.__neighbors(i,j):
                    # flux pour black
                    f_black[i,j,ni,nj] = model.NewIntVar(0, N, f"f_black_{i}_{j}_{ni}_{nj}")
                    # flux seulement entre cellules noires
                    model.Add(f_black[i,j,ni,nj] <= N * whites[i,j].Not())
                    model.Add(f_black[i,j,ni,nj] <= N * whites[ni,nj].Not())

        # -------------------------
        # conservation du flux
        # -------------------------

        # flux white
        i_root, j_root = self.__get_white()
        for i in range(self.__size):
            for j in range(self.__size):
                incoming = []
                outgoing = []

                for ni,nj in self.__neighbors(i,j):
                    incoming.append(f_white[ni,nj,i,j])
                    outgoing.append(f_white[i,j,ni,nj])

                incoming_sum = sum(incoming)
                outgoing_sum = sum(outgoing)

                if (i,j) != (i_root, j_root):
                    # cellule normale
                    model.Add(incoming_sum - outgoing_sum == whites[i,j])
                else:
                    # racine
                    model.Add(incoming_sum - outgoing_sum == 1 - n_whites)

        # flux black
        i_root, j_root = self.__get_black()
        for i in range(self.__size):
            for j in range(self.__size):
                incoming = []
                outgoing = []

                for ni,nj in self.__neighbors(i,j):
                    incoming.append(f_black[ni,nj,i,j])
                    outgoing.append(f_black[i,j,ni,nj])

                incoming_sum = sum(incoming)
                outgoing_sum = sum(outgoing)

                if (i,j) != (i_root, j_root):
                    # cellule normale
                    model.Add(incoming_sum - outgoing_sum == whites[i,j].Not())
                else:
                    # racine
                    model.Add(incoming_sum - outgoing_sum == 1 - (N-n_whites))


        # ------------------------------------------
        # conservation des carrés 2x2 et diagonales
        # ------------------------------------------
        for i in range(self.__size - 1):
            for j in range(self.__size - 1):
                square = [
                    whites[i, j],
                    whites[i + 1, j],
                    whites[i, j + 1],
                    whites[i + 1, j + 1],
                ]
                # comme il n'y a pas de 2x2 de même couleur, on impose que la somme des cellules soit 1 ou 3
                model.Add(sum(square) >= 1) 
                model.Add(sum(square) <= 3)

                # si deux jetons en diagonale sont noirs par ex
                # on est certain que l'un des deux autres le sera également

                diags = [
                    [whites[i,j], whites[i+1,j+1]],
                    [whites[i+1,j], whites[i,j+1]]
                ]
                for diag in diags:
                    n_diag = model.NewIntVar(0, 2, f"diag")
                    model.Add(n_diag == sum(diag))
                    # si n_diag1 == 2 -> 2 blancs -> sum(square) == 3
                    # si n_diag1 == 0 -> 2 noirs -> sum(square) == 1
                    s2 = model.NewBoolVar("2_whites")
                    s0 = model.NewBoolVar("0_white")
                    model.Add(n_diag == 2).OnlyEnforceIf(s2)
                    model.Add(n_diag != 2).OnlyEnforceIf(s2.Not())
                    model.Add(n_diag == 0).OnlyEnforceIf(s0)
                    model.Add(n_diag != 0).OnlyEnforceIf(s0.Not())

                    model.Add(sum(square) == 3).OnlyEnforceIf(s2)
                    model.Add(sum(square) == 1).OnlyEnforceIf(s0)

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return { (i,j):bool(solver.Value(whites[i,j])) for (i,j) in whites }
        return False