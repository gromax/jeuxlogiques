from typing import Union, Tuple, Dict
from modules.container.bridges import Data

from ortools.sat.python import cp_model

class Solver:
    __data:Data

    def __init__(self, data:Data):
        self.__data = data

    def solve(self) -> Union[Dict[Tuple[int,int], int], False]:
        """
        Cherche la grille solution.
        Renvoie un dictionnaire :
          clé = (indice début, indice fin)
          valeur = nombres de ponts
        """
        islands = self.__data.islands_as_dict()
        w = self.__data.width
        h = self.__data.height
        
        model = cp_model.CpModel()

        # -------------------------
        # chercher les connexions entre îles
        # -------------------------
        connexion_value = {}
        connexion_exists = {}
        bridges_from_island = {(i,j):[] for (i,j) in islands}

        cList = self.__data.connexions

        for i1,j1,i2,j2 in cList:
            v = model.NewIntVar(0, self.__data.max_bridges, f"c_value_({i1},{j1})--({i2},{j2})")
            b = model.NewBoolVar(f"c_exists_({i1},{j1})--({i2},{j2})")
            connexion_value[(i1,j1,i2,j2)] = v
            connexion_exists[(i1,j1,i2,j2)] = b
            model.Add(v >= 0).OnlyEnforceIf(b)
            model.Add(v == 0).OnlyEnforceIf(b.Not())
            bridges_from_island[i1,j1].append(v)
            bridges_from_island[i2,j2].append(v)
        
        for (i,j),k in islands.items():
            model.Add(sum(bridges_from_island[i,j])==k)
        
        # -------------------------
        # interdire les croisements de ponts
        # -------------------------
        for index1 in range(len(cList)):
            for index2 in range(index1+1,len(cList)):
                # voir s'il y a croisement
                # ne peut arriver que perpendiculairement
                i1,j1,i2,j2 = cList[index1]
                i3,j3,i4,j4 = cList[index2]
                # on a toujours i1=i2 xou j1=j2, toujours i3=i4 xou j3=j4
                # si i1=i2 et i3=i4, deux horizontaux et la condition sur les i échouera
                # si j1=j2 et j3=j3, deux verticaux et la condition sur les j échouera
                # si i1=i2 et j3 = j4, c'est la première moitié qui est pertinente
                # si j1=j2 et i3=i4, c'est la seconde moitié
                if min(i3,i4)<i1<max(i3,i4) and min(j1,j2)<j3<max(j1,j2) or min(j3,j4)<j1<max(j3,j4) and min(i1,i2)<i3<max(i1,i2):
                    # croisement, il faut empêcher que les deux soient vrais
                    b1 = connexion_exists[i1,j1,i2,j2]
                    b2 = connexion_exists[i3,j3,i4,j4]
                    model.AddBoolOr([b1.Not(), b2.Not()])
        

        # -------------------------
        # flux pour îles connexes
        # -------------------------
        neighbors = self.__data.neighborhood()
        flux = {}
        N = len(islands)

        for (i1,j1) in islands:
            for (i2,j2) in neighbors[i1,j1]:
                flux[i1,j1,i2,j2] = model.NewIntVar(0, N-1, f"flux_({i1},{j1})->({i2},{j2})")
                # flux seulement si connecté
                adress_bridge = (i1,j1,i2,j2) if i1 < i2 or j1 < j2 else (i2,j2,i1,j1)
                b = connexion_exists[adress_bridge]
                model.Add(flux[i1,j1,i2,j2] <= N * b)

        # île root sera la première
        iRoot, jRoot = list(islands.keys())[0]
        
        # -------------------------
        # conservation du flux
        # -------------------------

        for (i1,j1) in islands:
            incoming = []
            outgoing = []

            for i2,j2 in neighbors[i1,j1]:
                incoming.append(flux[i2,j2,i1,j1])
                outgoing.append(flux[i1,j1,i2,j2])

            if (i1,j1)==(iRoot,jRoot):
                model.Add(sum(incoming) == 0)
                model.Add(sum(outgoing) == N - 1)
            else:
                bilan = sum(incoming) - sum(outgoing)
                model.Add(bilan == 1)
        
        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return {(i1*w+j1, i2*w+j2):solver.Value(v) for (i1,j1,i2,j2),v in connexion_value.items()}
        return False