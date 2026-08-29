from typing import Dict, Tuple, Union, List
from ortools.sat.python import cp_model
from modules.primitives.direction import Direction
from modules.container.tracks import Data

DELTAS = ((-1,0),(0,1),(1,0),(0,-1)) # parcouru HDBG
# j'appelerai address une paire d'index, toujours dans l'ordre
# portant sur deux cases voisines dont les index sont donnés
# désigne ainsi de façon unique un mur de connexion entre ces cases
ADDRESS = Tuple[int,int]
Symbol = Tuple[Direction,Direction]

class Cell:
    """
    objet qui sera chargé de chercher les voisinages
    """
    def __init__(
        self,
        width:int,
        height:int,
        iline:int,
        icol:int,
        cells:Dict[Tuple[int,int],"Cell"],
        walls:Dict[ADDRESS,"Wall"],
        model:cp_model.CpModel,
        isEnd:bool
    ):
        self.width = width
        self.height = height
        self.iline = iline
        self.icol = icol
        self.__all_cells = cells
        self.__all_cells[iline,icol] = self
        self.__all_walls = walls
        self.var = model.NewBoolVar(f"cell ({iline},{icol})")
        self.__isEnd = isEnd
        if isEnd:
            self.__ends_rank = len([c for c in self.__all_cells.values() if c.__isEnd])
        else:
            self.__ends_rank = -1

    @property
    def index(self) -> int:
        if self.__isEnd:
            return -self.__ends_rank
        return self.iline*self.width + self.icol

    @property
    def left(self) -> Union["Cell",None]:
        if (self.iline, self.icol-1) in self.__all_cells:
            return self.__all_cells[self.iline, self.icol-1]
        else:
            return None
        
    @property
    def right(self) -> Union["Cell",None]:
        if (self.iline, self.icol+1) in self.__all_cells:
            return self.__all_cells[self.iline, self.icol+1]
        else:
            return None

    @property
    def up(self) -> Union["Cell",None]:
        if (self.iline-1, self.icol) in self.__all_cells:
            return self.__all_cells[self.iline-1, self.icol]
        else:
            return None
        
    @property
    def bottom(self) -> Union["Cell",None]:
        if (self.iline+1, self.icol) in self.__all_cells:
            return self.__all_cells[self.iline+1, self.icol]
        else:
            return None

    def neighbors(self) -> List[Union["Cell", None]]:
        return [self.up, self.right, self.bottom, self.left]

    def neighbor(self, rank:int) -> Union["Cell", None]:
        assert 0 <= rank < 4
        return self.neighbors()[rank]

    def walls(self) -> List[Union["Wall",None]]:
        return [self.paire_to_wall(n) for n in self.neighbors()]

    def paire_to_address(self, other:Union["Cell",None]) -> Union[ADDRESS,None]:
        if other is None:
            return None
        i1 = self.index
        i2 = other.index
        return min(i1,i2), max(i1,i2)

    def paire_to_wall(self, other:Union["Cell",None]) -> Union["Wall",None]:
        address = self.paire_to_address(other)
        if address is None or address not in self.__all_walls:
            return None
        return self.__all_walls[address]

    def force_walls_number(self, rails:Dict[Tuple[int,int],Symbol], model:cp_model.CpModel):
        """
        force le nombre de murs en fonction des cas.
        Pour ends, est 1,
        Pour symbol, est 2
        sinon 0 ou 2
        et si >0, la cellule est on
        """
        if self.__isEnd:
            # le seul mur est actif + la cellule aussi
            model.Add(self.var == True)
            for w in self.walls():
                if w is not None:
                    model.Add(w.var == True)
        elif (self.iline,self.icol) in rails:
            symb = rails[self.iline, self.icol]
            # cellule active
            model.Add(self.var == True)
            # on a alors exactement deux murs actifs dépendant des directions
            for dir in symb:
                di, dj = dir.delta()
                n_ij = self.iline + di, self.icol+dj
                assert n_ij in self.__all_cells
                n = self.__all_cells[n_ij]
                w = self.paire_to_wall(n)
                model.Add(w.var == True)
        else:
            # cas ordinaire, on devrait voir 0 ou 2 murs actifs et si la cellule
            # est active alors c'est 2
            ws = [w.var for w in self.walls() if w is not None]
            s = sum(ws)
            model.Add(s == 2).OnlyEnforceIf(self.var)
            model.Add(s == 0).OnlyEnforceIf(self.var.Not())

class Wall:
    """
    Définit un mur entre deux cellules
    """
    def __init__(self, cell1:Cell, cell2:Cell, model:cp_model.CpModel):
        self.cell1 = cell1
        self.cell2 = cell2
        self.var = model.NewBoolVar(f"wall {self.address}")
        # si le mur est actif, les cellules doivent l'être
        model.Add(cell1.var == True).OnlyEnforceIf(self.var)
        model.Add(cell2.var == True).OnlyEnforceIf(self.var)

    @property
    def address(self) -> ADDRESS:
        i1 = self.cell1.index
        i2 = self.cell2.index
        return min(i1,i2), max(i1,i2)

    def neighbors(self) -> Tuple[Cell, Cell]:
        return (self.cell1, self.cell2)

    def has_cell(self, cell:Cell) -> bool:
        return self.cell1 == cell or self.cell2 == cell

    def other_cell(self, cell:Cell) -> bool:
        if self.cell1 == cell:
            return self.cell2
        elif self.cell2 == cell:
            return self.cell1
        else:
            raise ValueError(f"Wall [{self.address}] n'a pas la cellule {cell.index}")

class Solver:
    __width:int
    __height:int
    __clues:List[int]
    __rails:Dict[Tuple[int,int], Symbol]
    __AB:Tuple[int,int]

    def __init__(self, data:Data):
        self.__width = data.width
        self.__height = data.height
        self.__clues = data.clues
        self.__rails = data.rails
        self.__AB = data.AB

    def __getEndCellCoord(self, index:int) -> Tuple[int,int]:
        """
        Crée les cellules sur aux extrémités
        """
        if index < self.__width:
            # colonne
            return (self.__height, index)
        else:
            # ligne
            return (index-self.__width, -1)


    def solve(self) -> Union[List[Tuple[int,int]], False]:
        # on commence par créer la grille de cellules
        model = cp_model.CpModel()
        walls:Dict[ADDRESS, Wall] = {}
        cells:Dict[Tuple[int,int],Cell] = {}
        for iline in range(self.__height):
            for icol in range(self.__width):
                c = Cell(self.__width, self.__height, iline, icol, cells, walls, model, False)
        # nous ajouts une cellA et une cellB pour les sorties
        ends = []
        for index in self.__AB:
            iline, icol = self.__getEndCellCoord(index)
            c = Cell(self.__width, self.__height, iline, icol, cells, walls, model, True)
            ends.append(c)
        # on crée ensuite les murs
        for cell in cells.values():
            for cell2 in cell.neighbors():
                if cell2 is None:
                    continue
                w = Wall(cell, cell2,model)
                ad = w.address
                if ad not in walls:
                    walls[ad] = w
        # le nombres de connexions pour une cellule donnée devrait être 2 ou 0 ou 1,
        for cell in cells.values():
            cell.force_walls_number(self.__rails, model)

        # il faut coder les contraintes relatives aux clues
        for index, clue in enumerate(self.__clues):
            if clue < 0:
                continue
            if index < self.__width:
                # c'est une colonne
                col = [cells[i,index].var for i in range(self.__height)]
                s = sum(col)
                model.Add(s == clue)
            else:
                # c'est une ligne
                lig = [cells[index-self.__width,j].var for j in range(self.__width)]
                s = sum(lig)
                model.Add(s == clue)

        # reste à coder une contrainte de flux sur le parcours
        # nombre de cells actives
        N = len(cells)
        n_activ_cells = model.NewIntVar(2, N, f"cells actives")
        model.Add(n_activ_cells == sum(c.var for c in cells.values()))

        # la racine est la première entrée
        root_cell = ends[0]
        # flux boucle
        flux = {}
        for c in cells.values():
            for n in c.neighbors():
                if n is None:
                    continue
                flux[c.index, n.index] = model.NewIntVar(0, N, f"flux_{c.index}->{n.index}")
                # flux seulement si mur actif
                w = c.paire_to_wall(n)
                model.Add(flux[c.index, n.index] <= N * w.var)
                model.Add(flux[c.index, n.index] <= N * w.var)

        # conservation du flux
        for c in cells.values():
            incoming = []
            outgoing = []
            for n in c.neighbors():
                if n is None:
                    continue
                incoming.append(flux[n.index,c.index])
                outgoing.append(flux[c.index,n.index])
            delta = sum(incoming) - sum(outgoing)
            if c == root_cell:
                model.Add(delta == 1 - n_activ_cells)
            else:
                model.Add(delta == c.var)

        # comme chaque case connecte 2 ou 0, on a la garantie d'avoir une ou plusieurs boucles
        # le flux assure la connexité donc l'unicité de la boucle

        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            # il suffit de parcourir les addresses 
            activ_walls = [w for w in walls.values() if bool(solver.Value(w.var))]
            return self.reorder(ends[0], activ_walls)
        return False

    def reorder(self, start_cell:Cell, activ_walls:List[Wall]) -> List[Tuple[int,int]]:
        """
        reçoit une liste de paires d'index qui forment mis bout à bout une boucle
        construit la liste d'index dans l'ordre et produit la liste de (iline,icol)
        correspondante
        """
        assert len(activ_walls) > 0
        # on doit absolument partir de la position ends
        cells = [start_cell]
        while len(activ_walls) > 0:
            # on veut récupérer une paire commençant par l'index output[-1]
            for i, w in enumerate(activ_walls):
                if w.has_cell(cells[-1]):
                    break
            else:
                # cas où on ne trouve pas...
                raise ValueError("la solution ne boucle pas !")
            new_cell = w.other_cell(cells[-1])
            cells.append(new_cell)
            activ_walls.pop(i)
        coords =  [(c.iline, c.icol) for c in cells]
        # on peut filtrer encore les coords pour les lignes droites
        output = coords[:2]
        for coord in coords[2:]:
            # si a une même coordonnée avec les 2 précédents, peut remplacer le précédent
            if coord[0] == output[-1][0] == output[-2][0] \
              or coord[1] == output[-1][1] == output[-2][1]:
                output[-1] = coord
            else:
                output.append(coord)
        return output

