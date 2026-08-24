from typing import Dict, Tuple, Union, List

from ortools.sat.python import cp_model

class UndeadSolver:
    __size:int
    __mirrors:Dict[Tuple[int,int],bool] # True pour left
    __ghosts:int
    __vampires:int
    __zombies:int
    __top:List[int]
    __right:List[int]
    __bottom:List[int]
    __left:List[int]

    def __init__(
            self,
            size:int,
            mirrors:Dict[Tuple[int,int], bool],
            ghosts:int,
            vampires:int,
            zombies:int,
            top:List[int],
            right:List[int],
            bottom:List[int],
            left:List[int]
        ):
        self.__size = size
        self.__ghosts = ghosts
        self.__vampires = vampires
        self.__zombies = zombies
        self.__mirrors = mirrors
        self.__top = top
        self.__right = right
        self.__bottom = bottom
        self.__left = left

    def __in_box(self, i:int, j:int) -> bool:
        """
        renvoie True si (i,j) dans le cadre
        """
        return 0 <= i < self.__size and 0 <= j < self.__size

    def __turn(self, di:int, dj:int, sens:str) -> Tuple[int,int]:
        """
        fait tourner (di,dj) selon sens du miroir L ou R
        """
        if sens == "L":
            return dj,di
        else:
            return -dj,-di

    def __cells_segment(self, start:Tuple[int,int], dir:Tuple[int,int]) -> Tuple[List[Tuple[int,int]], Tuple[int,int]]:
        """
        partant d'une case, dans une certaine direction, suit le parcours jusqu'à la sortie en suivant les mirroirs.
        s'arrête en sortant du cadre où rencontrant un miroir
        renvoie liste cellules rencontrées et position finale
        """
        di,dj = dir
        i,j = start
        L = []
        while (i,j) not in self.__mirrors and self.__in_box(i,j):
            L.append((i,j))
            i += di
            j += dj
        return L, (i,j)
        
    def __cells_path(self, start:Tuple[int,int], dir:Tuple[int,int]) -> List[List[Tuple[int,int]]]:
        """
        renvoie tous les segments d'un miroir à l'autre
        """
        di,dj = dir
        i,j = start
        L = []
        MAX_COUNT = 100
        while self.__in_box(i,j):
            segment, (i,j) = self.__cells_segment((i,j),(di,dj))
            if (i,j) in self.__mirrors:
                sens = "L" if self.__mirrors[i,j] else "R"
                di,dj = self.__turn(di,dj,sens)
                i += di
                j += dj
            L.append(segment)
            MAX_COUNT -= 1
            assert MAX_COUNT > 0, "Trop de réptitions dans cells_path"
        return L

    def solve(self) -> Union[List[List[str]], False]:
        model = cp_model.CpModel()

        # -------------------------
        # Variables undeads
        # -------------------------
        ghost = {}
        vampire = {}
        zombie = {}
        for i in range(self.__size):
            for j in range(self.__size):
                ghost[i,j] = model.NewBoolVar(f"g_{i}_{j}")
                vampire[i,j] = model.NewBoolVar(f"v_{i}_{j}")
                zombie[i,j] = model.NewBoolVar(f"z_{i}_{j}")
                if (i,j) in self.__mirrors:
                    model.Add(ghost[i,j] == False)
                    model.Add(vampire[i,j] == False)
                    model.Add(zombie[i,j] == False)
                    continue
                model.Add(ghost[i,j] == False).OnlyEnforceIf(vampire[i,j])
                model.Add(ghost[i,j] == False).OnlyEnforceIf(zombie[i,j])
                model.Add(vampire[i,j] == False).OnlyEnforceIf(ghost[i,j])
                model.Add(vampire[i,j] == False).OnlyEnforceIf(zombie[i,j])
                model.Add(zombie[i,j] == False).OnlyEnforceIf(ghost[i,j])
                model.Add(zombie[i,j] == False).OnlyEnforceIf(vampire[i,j])
                model.AddBoolOr([ghost[i,j], vampire[i,j], zombie[i,j]])

        #-----------------------------
        # nombre par espèce
        #-----------------------------
        
        model.Add(sum(ghost.values()) == self.__ghosts)
        model.Add(sum(vampire.values()) == self.__vampires)
        model.Add(sum(zombie.values()) == self.__zombies)

        # -------------------------
        # contraintes
        # -------------------------
        constraints = self.__top + self.__right + self.__bottom + self.__left
        starts = [(0,j) for j in range(self.__size)] + \
                 [(i,self.__size-1) for i in range(self.__size)] + \
                 [(self.__size-1,j) for j in range(self.__size)] + \
                 [(i,0) for i in range(self.__size)]
        dirs = [(1,0)]*self.__size + \
               [(0,-1)]*self.__size + \
               [(-1,0)]*self.__size + \
               [(0,1)]*self.__size
        for constraint, start, dir in zip(constraints, starts, dirs):
            path = self.__cells_path(start, dir)
            beforeMiror = path[0]
            afterMiror = sum(path[1:],[])
            # il faut que le nombre vampire + zombie avant
            # + ghost + zombie après donne la contrainte
            undeadsBefore = [zombie[i,j] for (i,j) in beforeMiror] + [vampire[i,j] for (i,j) in beforeMiror]
            undeadsAfter  = [zombie[i,j] for (i,j) in afterMiror] + [ghost[i,j] for (i,j) in afterMiror]
            undeadsAll = undeadsBefore + undeadsAfter
            model.Add(sum(undeadsAll) == constraint)
        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            grid = []
            for i in range(self.__size):
                line = []
                for j in range(self.__size):
                    if solver.Value(ghost[i,j]):
                        line.append("G")
                    elif solver.Value(vampire[i,j]):
                        line.append("V")
                    elif solver.Value(zombie[i,j]):
                        line.append("Z")
                    else:
                        line.append(" ")
                grid.append(line)
            return grid
        return False