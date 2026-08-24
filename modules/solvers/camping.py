from typing import List, Union, Tuple
from modules.container.camping import Data
from modules.primitives.direction import Direction

from ortools.sat.python import cp_model

class Solver:
    __data:Data

    def __init__(self, data:Data):
        self.__data = data

    def __neighbors(self, i:int, j:int):
        deltas = [(-1,-1), (-1,0), (-1,1),
                  ( 0,-1),         ( 0,1),
                  ( 1,-1), ( 1,0), ( 1,1)]
        return [(i+di, j+dj) for di,dj in deltas]
    
    def __ranked_neighbor(self, i:int, j:int, rank:int):
        # h d b g
        deltas = [(-1,0), (0,1), (1,0), (0,-1)]
        di,dj = deltas[rank]
        return (i+di, j+dj)

    def __side_neighbors(self, i:int, j:int) -> List[int]:
        deltas = [(-1,0), (0,1), (1,0), (0,-1)]
        return [(i+di, j+dj) for di,dj in deltas]

    def solve(self) -> Union[Tuple[List[bool],List[int]], False]:
        """
        Cherche la grille solution.
        Renvoie une paire constituée de :
          Une liste de booléesn donnant la position des tentes
          Une liste de directions indiquant pour chaque arbre, la direction de la tente associée
        """
        LDir = list(Direction)
        model = cp_model.CpModel()
        width = self.__data.width
        height = self.__data.height

        # -------------------------
        # Variables cellules
        # -------------------------
        c = {}

        for i in range(height):
            line = []
            for j in range(width):
                c[i,j] = model.NewBoolVar(f"c_{i}_{j}")
                line.append(c[i,j])
                if i*width + j in self.__data.trees:
                    model.Add(c[i,j]==False) # pas de tente sur un arbre
                ns = self.__side_neighbors(i,j)
                ntrees = len([(ni,nj) for (ni,nj) in ns if ni*width + nj in self.__data.trees])
                if ntrees == 0:
                    model.Add(c[i,j]==False) # pas de tente si pas d'arbre voisin
            model.Add(sum(line) == self.__data.right[i]) # nombre par ligne

        for j in range(width):
            col = []
            for i in range(height):
                col.append(c[i,j])
            model.Add(sum(col) == self.__data.top[j]) # nombre par colonne

        # j'ajoute des cases ext pour les effets de bord
        c_ext = model.NewBoolVar(f"c_ext")
        model.Add(c_ext == False)
        for i in range(height):
            c[i,-1] =  c_ext
            c[i,width] =  c_ext
        for j in range(-1,width+1):
            c[-1,j] = c_ext
            c[height,j] = c_ext

        # -------------------------
        # deux tentes ne se touchent pas
        # -------------------------
        for i in range(height):
            for j in range(width):
                for (ni,nj) in self.__neighbors(i,j):
                    model.Add(c[i,j] + c[ni,nj] <= 1)

        # -------------------------
        # tout arbre doit avoir au moins une tente voisine
        # -------------------------
        for index in self.__data.trees:
            i = index // width
            j = index % width
            model.Add(sum([c[ni,nj] for ni,nj in self.__side_neighbors(i,j)]) >= 1)

        # ---------------------------------------
        # chaque arbre doit posséder une tente
        # ---------------------------------------
        # on donnera un indice 1-4 pour h,d,b,g
        indexesForTrees = []
        deltas = [d.delta() for d in LDir]
        for rank, index in enumerate(self.__data.trees):
            i = index // width
            j = index % width
            v = model.NewIntVar(0, len(LDir)-1, f"tent_for_tree_{rank}")
            candidates = [c[i+di, j+dj] for (di,dj) in deltas]
            model.AddElement(v, candidates, 1)
            indexTent = model.NewIntVar(0, height*width-1 , f"indexTent_for_tree_{rank}")
            indexesForTrees.append(indexTent)
            dirs = [model.NewBoolVar(d.label) for d in LDir]
            model.Add(sum(dirs) == 1)
            for k, d in enumerate(dirs):
                model.Add(v == k).OnlyEnforceIf(d)
                di, dj = LDir[k].delta()
                model.Add(indexTent == (i+di)*width + j+dj).OnlyEnforceIf(d)
        model.AddAllDifferent(indexesForTrees)

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return (
                [bool(solver.Value(c[index//width,index%width])) for index in range(width*height)],
                [solver.Value(index) for index in indexesForTrees]
            )
        return False