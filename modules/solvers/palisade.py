from typing import Dict, Tuple, List, Union
from modules.container.palisade import Data
from ortools.sat.python import cp_model

DELTAS = ((1,0),(-1,0),(0,1),(0,-1))
class Solver:
    __width:int
    __height:int
    __zoneSize:int
    __clues:Dict[Tuple[int,int],int]

    def __init__(self, data:Data):
        self.__width = data.width
        self.__height = data.height
        self.__zoneSize = data.zoneSize
        self.__clues = data.clues

    def __neighbors(self, i:int, j:int, with_ext:bool)->List[Tuple[int,int]]:
        """
        voisins
        """
        pos = [(i+di, j+dj) for (di,dj) in DELTAS]
        if with_ext:
            return [(ni,nj) if 0 <= ni < self.__height and 0 <= nj < self.__width else (-1,-1) for (ni,nj) in pos]
        return [(ni,nj) for (ni,nj) in pos if 0 <= ni < self.__height and 0 <= nj < self.__width]

    def solve(self) -> Union[List[int],False]:
        N = self.__height * self.__width
        NZ = N // self.__zoneSize # nombres de zones
        model = cp_model.CpModel()

        # -------------------------
        # Variables cellules
        # -------------------------
        cells = {}
        # cellule extérieure, sera la zone 0
        cells[(-1,-1)] = model.NewIntVar(0,NZ,f"c_ext")
        model.Add(cells[-1,-1] == 0)

        for iline in range(self.__height):
            for icol in range(self.__width):
                cells[iline,icol] = model.NewIntVar(1,NZ,f"c_{iline}_{icol}")

        # -------------------------
        # contraintes
        # -------------------------
        for (iline,icol), clue in self.__clues.items():
            walls = []
            for niline, nicol in self.__neighbors(iline,icol,True):
                wall = model.NewBoolVar(f"wall_({iline},{icol})-({niline},{nicol})")
                model.Add(cells[iline,icol] == cells[niline,nicol]).OnlyEnforceIf(wall.Not())
                model.Add(cells[iline,icol] != cells[niline,nicol]).OnlyEnforceIf(wall)
                walls.append(wall)
            model.Add(sum(walls) == clue)

        #-------------------------
        # nombre de cellules par zone
        #-------------------------
        zones = {}
        for iZone in range(1,NZ+1):
            im_in_Zone = []
            for iline in range(self.__height):
                for icol in range(self.__width):
                    im_in = model.NewBoolVar(f"({iline},{icol}) in #{iZone}")
                    im_in_Zone.append(im_in)
                    zones[iline,icol,iZone] = im_in
                    model.Add(cells[iline,icol]==iZone).OnlyEnforceIf(im_in)
                    model.Add(cells[iline,icol]!=iZone).OnlyEnforceIf(im_in.Not())
            model.Add(sum(im_in_Zone) == self.__zoneSize)

        # -------------------------
        # flux des zones
        # -------------------------
        # on ne connaît pas la case racine il faut donc une racine par zone
        roots = {}
        for iZone in range(1,NZ+1):
            roots_of_Zone = []
            for iline in range(self.__height):
                for icol in range(self.__width):
                    r = model.NewBoolVar(f"({iline},{icol}) is #{iZone} root")
                    roots[iline,icol,iZone] = r
                    model.Add(r <= zones[iline,icol,iZone])
                    roots_of_Zone.append(r)
            # Une seule racine pour chaque zone
            model.Add(sum(roots_of_Zone) == 1)

        # il y a un flux par zone
        flux = {}
        for iZone in range(1,NZ+1):
            for iline in range(self.__height):
                for icol in range(self.__width):
                    for niline,nicol in self.__neighbors(iline,icol,False):
                        flux[iline,icol,niline,nicol,iZone] = model.NewIntVar(0, self.__zoneSize, f"flux({iline},{icol})->({niline},{nicol}) pour #{iZone}")
                        # flux seulement entre cellules actives
                        model.Add(flux[iline,icol,niline,nicol,iZone] <= self.__zoneSize * zones[iline,icol,iZone])
                        model.Add(flux[iline,icol,niline,nicol,iZone] <= self.__zoneSize * zones[niline,nicol,iZone])
        # -------------------------
        # conservation du flux
        # -------------------------
        for iZone in range(1,NZ+1):
            for iline in range(self.__height):
                for icol in range(self.__width):
                    incoming = []
                    outgoing = []

                    for niline,nicol in self.__neighbors(iline,icol,False):
                        incoming.append(flux[niline,nicol,iline,icol,iZone])
                        outgoing.append(flux[iline,icol,niline,nicol,iZone])

                    delta = sum(incoming) - sum(outgoing)
                    model.Add(delta == 1 - self.__zoneSize).OnlyEnforceIf(roots[iline,icol,iZone])
                    model.Add(delta == zones[iline,icol,iZone]).OnlyEnforceIf(roots[iline,icol,iZone].Not())
        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [int(solver.Value(cells[i//self.__width,i%self.__width])) for i in range(N)]
        return False