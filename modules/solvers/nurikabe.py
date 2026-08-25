from typing import Dict, List, Tuple, Union
from ortools.sat.python import cp_model
from modules.container.nurikabe import Data

class Solver:
    __width:int
    __height:int
    __clues:Dict[Tuple[int,int],int]

    def __init__(self, data:Data):
        self.__width = data.width
        self.__height = data.height
        self.__clues = data.clues

    def __neighbors(self, i:int, j:int):
        """
        itérateur
        """
        for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]:
            ni = i+di
            nj = j+dj
            if 0 <= ni < self.__height and 0 <= nj < self.__width:
                yield ni,nj
    
    def solve(self) -> Union[List[bool], False]:
        N = self.__height * self.__width
        Islands = len(self.__clues)
        posIslands = list(self.__clues.keys())
        sizeIslands = list(self.__clues.values())

        model = cp_model.CpModel()

        # -------------------------
        # Variables cellules
        # -------------------------
        cell = {}
        river = {}
        for i in range(self.__height):
            for j in range(self.__width):
                cell[i,j] = model.NewIntVar(0,Islands,f"c_{i}_{j}")
                if (i,j) in self.__clues:
                    index = posIslands.index((i,j))
                    model.Add(cell[i,j] == index+1)
                river[i,j] = model.NewBoolVar(f"r_{i}_{j}")
                model.Add(cell[i,j]==0).OnlyEnforceIf(river[i,j])
                model.Add(cell[i,j]!=0).OnlyEnforceIf(river[i,j].Not())

        # -------------------------
        # 2 voisins numérotés => rivière
        # -------------------------
        for key in self.__two_numbers():
            model.Add(river[key] == True)

        #-----------------------------
        # nombre de cellules rivière 
        #-----------------------------
        n_river = model.NewIntVar(1, N, f"river size")
        model.Add(n_river == sum(river.values()))

        # -------------------------
        # flux des cases rivière
        # -------------------------
        # on ne connaît pas la case racine il faut donc des variables pour cela
        root = {}
        for i in range(self.__height):
            for j in range(self.__width):
                root[i,j] = model.NewBoolVar(f"river root is ({i},{j})")
                # case numérotée pas sur la rivière
                if (i,j) in self.__clues:
                    model.Add(root[i,j] == False)

        # Une seule racine
        model.Add(sum(root.values()) == 1)

        # La cellule root doit être active
        for i in range(self.__height):
            for j in range(self.__width):
                model.Add(root[i,j] <= river[i,j])

        # flux river
        f_river = {}
        for i in range(self.__height):
            for j in range(self.__width):
                for ni,nj in self.__neighbors(i,j):
                    # flux pour river
                    f_river[i,j,ni,nj] = model.NewIntVar(0, N, f"f_river_{i}_{j}_{ni}_{nj}")
                    # flux seulement entre cellules de la rivière
                    model.Add(f_river[i,j,ni,nj] <= N * river[i,j])
                    model.Add(f_river[i,j,ni,nj] <= N * river[ni,nj])

        # -------------------------
        # conservation du flux rivière
        # -------------------------

        for i in range(self.__height):
            for j in range(self.__width):
                incoming = []
                outgoing = []

                for ni,nj in self.__neighbors(i,j):
                    incoming.append(f_river[ni,nj,i,j])
                    outgoing.append(f_river[i,j,ni,nj])

                incoming_sum = sum(incoming)
                outgoing_sum = sum(outgoing)

                model.Add(incoming_sum - outgoing_sum == 1 - n_river).OnlyEnforceIf(root[i,j])
                model.Add(incoming_sum - outgoing_sum == river[i,j]).OnlyEnforceIf(root[i,j].Not())
        


        # -------------------------
        # pas de mare 2x2
        # -------------------------

        for i in range(self.__height - 1):
            for j in range(self.__width - 1):
                mare = [
                    river[i, j],
                    river[i + 1, j],
                    river[i, j + 1],
                    river[i + 1, j + 1],
                ]
                model.Add(sum(mare) <= 3)

        #-------------------------------
        # Deux îles ne se touchent pas
        #-----------------------------
        for i in range(self.__size):
            for j in range(self.__size):
                if i<self.__size-1:
                    # doivent être égaux ou de produit nul
                    c_eq = model.NewBoolVar("eq")
                    c_a0 = model.NewBoolVar("a0")
                    c_b0 = model.NewBoolVar("b0")

                    model.Add(cell[i,j] == cell[i+1,j]).OnlyEnforceIf(c_eq)
                    model.Add(cell[i,j] == 0).OnlyEnforceIf(c_a0)
                    model.Add(cell[i+1,j] == 0).OnlyEnforceIf(c_b0)
                    model.AddBoolOr([c_eq, c_a0, c_b0])
                if j<self.__size-1:
                    # doivent être égaux ou de produit nul
                    c_eq = model.NewBoolVar("eq")
                    c_a0 = model.NewBoolVar("a0")
                    c_b0 = model.NewBoolVar("b0")

                    model.Add(cell[i,j] == cell[i,j+1]).OnlyEnforceIf(c_eq)
                    model.Add(cell[i,j] == 0).OnlyEnforceIf(c_a0)
                    model.Add(cell[i,j+1] == 0).OnlyEnforceIf(c_b0)
                    model.AddBoolOr([c_eq, c_a0, c_b0])

        #-------------------------------
        # flux pour les îles
        #-------------------------------
        is_on_island = {}
        f_island = {}
        for island_i in range(Islands):
            S = sizeIslands[island_i]
            i_root, j_root = posIslands[island_i]
            # -------------------------
            # Appartenance aux îles
            # -------------------------
            for i in range(self.__height):
                for j in range(self.__width):
                    is_on_island[island_i, i, j] = model.NewBoolVar(f"ison_{island_i}_{i}_{j}")
                    if (i,j) == (i_root, j_root):
                        model.Add(is_on_island[island_i, i, j] == True)
                    elif (i,j) in self.__clues or self.__dist(i_root,j_root,i,j)>=S:
                        model.Add(is_on_island[island_i, i, j] == False)
                    model.Add(cell[i,j] == island_i+1).OnlyEnforceIf(is_on_island[island_i, i, j])
                    model.Add(cell[i,j] != island_i+1).OnlyEnforceIf(is_on_island[island_i, i, j].Not())
                    
            # -------------------------
            # Création des flux
            # -------------------------
            for i in range(self.__height):
                for j in range(self.__width):
                    for ni,nj in self.__neighbors(i,j):
                        # flux pour l'île
                        f_island[island_i,i,j,ni,nj] = model.NewIntVar(0, S, f"f_island_{island_i}_{i}_{j}_{ni}_{nj}")
                        # flux seulement entre cellules d'une même île
                        model.Add(f_island[island_i,i,j,ni,nj] <= S * is_on_island[island_i,i,j])
                        model.Add(f_island[island_i,i,j,ni,nj] <= S * is_on_island[island_i,ni,nj])
            
            # -------------------------
            # conservation du flux
            # -------------------------
            for i in range(self.__height):
                for j in range(self.__width):
                    incoming = []
                    outgoing = []

                    for ni,nj in self.__neighbors(i,j):
                        incoming.append(f_island[island_i,ni,nj,i,j])
                        outgoing.append(f_island[island_i,i,j,ni,nj])

                    incoming_sum = sum(incoming)
                    outgoing_sum = sum(outgoing)

                    if (i,j) != (i_root, j_root):
                        # cellule normale
                        model.Add(incoming_sum - outgoing_sum == is_on_island[island_i,i,j])
                    else:
                        # racine
                        model.Add(incoming_sum - outgoing_sum == 1 - S)

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [solver.Value(river[index//self.__width,index%self.__width]) for index in range(N)]
        return False
    
    def __two_numbers(self) -> List[Tuple[int,int]]:
        """
        retourne la liste des cases ayant 2 voisins numérotés
        """
        output = []
        for i in range(self.__height):
            for j in range(self.__width):
                if (i,j) in self.__clues:
                    continue
                count = 0
                for ni,nj in self.__neighbors(i,j):
                    if (ni,nj) in self.__clues:
                        count += 1
                if count == 2:
                    output.append((i,j))
        return output
    
    def __dist(self, i:int, j:int, ni:int, nj:int) -> int:
        """
        renvoie une distance 1 entre (i,j) et (ni,nj)
        """
        return abs(i-ni) + abs(j-nj)