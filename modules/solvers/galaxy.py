from typing import List, Tuple
from container.galaxy import Data
from ortools.sat.python import cp_model

class GalaxySolver:
    H:int
    W:int
    stars:List[Tuple[int,int]]

    def __init__(self, data:Data):
        self.H = data.height
        self.W = data.width
        self.stars = data.stars

    def __sticked_to_star(self, iStar:int) -> List[Tuple[int,int]]:
        """
        Liste des (i,j) des cells collées à une étoile
        """
        lineStar, colStar = self.stars[iStar]
        lines = [lineStar//2] if lineStar%2 == 0 else [lineStar//2, lineStar//2+1]
        cols = [colStar//2] if colStar%2 == 0 else [colStar//2, colStar//2+1]
        output = []
        for line in lines:
            for col in cols:
                output.append((line,col))
        return output
    
    def __root_cell_for_star(self, iStar:int) -> Tuple[int,int]:
        """
        (i,j) de la première cellule collée à une étoile
        """
        return self.__sticked_to_star(iStar)[0]

    def __neighbors(self, i:int, j:int):
        """
        itérateur
        """
        for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]:
            ni = i+di
            nj = j+dj
            if 0 <= ni < self.H and 0 <= nj < self.W:
                yield ni,nj

    def solve(self):
        G = len(self.stars)
        N = self.H * self.W
        model = cp_model.CpModel()

        # -------------------------
        # Variables galaxie
        # -------------------------

        g = {}
        for i in range(self.H):
            for j in range(self.W):
                g[i,j] = model.NewIntVar(0, G-1, f"g_{i}_{j}")

        # chaque étoile collé à une étoile
        # appartient à sa galaxie
        for k in range(G):
            for iline, icol in self.__sticked_to_star(k):
                model.Add(g[iline,icol] == k)

        # -------------------------
        # Symétrie centrale
        # -------------------------
        is_gal = {}
        for i in range(self.H):
            for j in range(self.W):
                for k,(si,sj) in enumerate(self.stars):
                    i2 = si - i # si est l'indice *2 !
                    j2 = sj - j

                    b = model.NewBoolVar(f"is_{i}_{j}_{k}")
                    is_gal[i,j,k] = b
                    # OnlyEnforceIf traduit une implication
                    # la contrainte n'est demandée que si b brai
                    model.Add(g[i,j] == k).OnlyEnforceIf(b)
                    model.Add(g[i,j] != k).OnlyEnforceIf(b.Not())

                    if 0 <= i2 < self.H and 0 <= j2 < self.W:
                        model.Add(g[i2,j2] == k).OnlyEnforceIf(b)
                    else:
                        model.Add(g[i,j] != k)

        # -------------------------
        # taille des galaxies
        # -------------------------

        size = []
        for k in range(G):
            cells = []
            for i in range(self.H):
                for j in range(self.W):
                    cells.append(is_gal[i,j,k])
            s = model.NewIntVar(1, N, f"size_{k}")
            model.Add(s == sum(cells))
            size.append(s)
            # donc size[k] est la taille d'une galaxie

        # -------------------------
        # flux
        # -------------------------

        # il faut autant de flux qu'il y a de galaxies
        f = {}
        for k in range(G):
            for i in range(self.H):
                for j in range(self.W):
                    for ni,nj in self.__neighbors(i,j):
                        f[k,i,j,ni,nj] = model.NewIntVar(0, N, f"f_{k}_{i}_{j}_{ni}_{nj}")
                       
                        model.Add(f[k,i,j,ni,nj] <= N * is_gal[i,j,k])
                        model.Add(f[k,i,j,ni,nj] <= N * is_gal[ni,nj,k])

        # -------------------------
        # conservation du flux
        # -------------------------

        for k in range(G):
            ri, rj = self.__root_cell_for_star(k)
            for i in range(self.H):
                for j in range(self.W):
                    incoming = []
                    outgoing = []
                    for ni,nj in self.__neighbors(i,j):
                        incoming.append(f[k,ni,nj,i,j])
                        outgoing.append(f[k,i,j,ni,nj])

                    incoming_sum = sum(incoming)
                    outgoing_sum = sum(outgoing)

                    if (i,j) == (ri,rj):
                        model.Add(outgoing_sum - incoming_sum == size[k]-1)
                    else:
                        model.Add(incoming_sum - outgoing_sum == is_gal[i,j,k])

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)

        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [[solver.Value(g[i,j]) for j in range(self.W)] for i in range(self.H)]
        return False