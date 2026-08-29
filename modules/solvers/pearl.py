from typing import Dict, Tuple, Union, List
from ortools.sat.python import cp_model

from modules.container.pearl import Data

DELTAS = ((-1,0),(0,1),(1,0),(0,-1)) # parcouru HDBG
# j'appelerai address une paire d'index, toujours dans l'ordre
# portant sur deux cases voisines dont les index sont donnés
# désigne ainsi de façon unique un mur de connexion entre ces cases
ADDRESS = Tuple[int,int]

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
        walls:Dict[ADDRESS,"Wall"]
    ):
        self.width = width
        self.height = height
        self.iline = iline
        self.icol = icol
        self.__all_cells = cells
        self.__all_cells[iline,icol] = self
        self.__all_walls = walls

    @property
    def index(self) -> int:
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

    def force_0_or_2(self, clues:Dict[Tuple[int,int],bool], model:cp_model.CpModel):
        """
        force 0 ou 2 cloisons actives pour cette cellule,
        exactement 2 si c'est une cellule avec clue
        """
        addresses = [self.paire_to_address(other) for other in self.neighbors() if other is not None]
        ws = [self.__all_walls[ad].var for ad in addresses if ad in self.__all_walls]
        s = sum(ws)
        if (self.iline,self.icol) in clues:
            model.Add(s == 2)
            if clues[self.iline, self.icol] is False:
                self.__force_white(model)
            else:
                self.__force_black(model)
            return
        is2 = model.NewBoolVar(f"2conns_in #{self.index}")
        model.Add(s == 2).OnlyEnforceIf(is2)
        model.Add(s == 0).OnlyEnforceIf(is2.Not())

    def __get_vert_for_white(self) -> Union[None, List["Wall"]]:
        """
        renvoie les murs haut et bas s'ils existent
        et les coudes possibles dans ces cases car une case blanche doit couder d'un côté au moins
        """
        up = self.up
        bottom = self.bottom
        if up is None or bottom is None:
            return None
        coudes = [
            up.paire_to_wall(up.left),
            up.paire_to_wall(up.right),
            bottom.paire_to_wall(bottom.left),
            bottom.paire_to_wall(bottom.right)
        ]
        walls = [w for w in coudes if w is not None]
        assert len(walls)>0, f"Grille incohérente en #{self.index}"
        return [self.paire_to_wall(up), self.paire_to_wall(bottom)] + walls

    def __get_hor_for_white(self) -> Union[None, List["Wall"]]:
        """
        renvoie les murs gauche et doite s'ils existent
        et les coudes possibles dans ces cases car une case blanche doit couder d'un côté au moins
        """
        left = self.left
        right = self.right
        if left is None or right is None:
            return None
        coudes = [
            left.paire_to_wall(left.up),
            left.paire_to_wall(left.bottom),
            right.paire_to_wall(right.up),
            right.paire_to_wall(right.bottom)
        ]
        walls = [w for w in coudes if w is not None]
        assert len(walls)>0, f"Grille incohérente en #{self.index}"
        return [self.paire_to_wall(left), self.paire_to_wall(right)] + walls


    def __force_white(self, model:cp_model.CpModel):
        """
        force un comportement de cellule blanche
        traversée en ligne blanche avec au moins un coude dans l'une des cases voisines
        """
        # on veut que la connexion soit droite
        cas_hor = self.__get_hor_for_white()
        isHor = model.NewBoolVar(f"#{self.index} is Hor")
        if cas_hor is not None:
            coudes = [w.var for w in cas_hor[2:]]
            model.Add(cas_hor[0].var == True).OnlyEnforceIf(isHor)
            model.Add(cas_hor[1].var == True).OnlyEnforceIf(isHor)
            model.Add(sum(coudes)>=1).OnlyEnforceIf(isHor)
        else:
            model.Add(isHor==False)
        cas_vert = self.__get_vert_for_white()
        if cas_vert is not None:
            coudes = [w.var for w in cas_vert[2:]]
            model.Add(cas_vert[0].var == True).OnlyEnforceIf(isHor.Not())
            model.Add(cas_vert[1].var == True).OnlyEnforceIf(isHor.Not())
            model.Add(sum(coudes)>=1).OnlyEnforceIf(isHor.Not())
        else:
            model.Add(isHor==True)

    def __get_lines_for_black(self) -> List[Union[None, Tuple["Wall", "Wall"]]]:
        """
        renvoie dans l'ordre Haut, Droite, Bas, Gauche, les deux murs à suivre en ligne droite
        si possible, sinon None
        """
        output = []
        for rank in range(4):
            n = self.neighbor(rank)
            if n is None:
                output.append(None)
                continue
            nn = n.neighbor(rank)
            if nn is None:
                output.append(None)
                continue
            paire = (self.paire_to_wall(n), n.paire_to_wall(nn))
            output.append(paire)
        return output

    def __force_black(self, model:cp_model.CpModel):
        """
        force un comportement de case noire
        un coude avec des lignes droites dans les deux cases voisines
        """
        lines = self.__get_lines_for_black()
        boolvars = []
        for rank in range(4):
            v = model.NewBoolVar(f"black_r{rank} in #{self.index}")
            boolvars.append(v)
            p1 = lines[rank]
            p2 = lines[(rank+1)%4]
            if p1 is None or p2 is None:
                # coude impossible
                model.Add(v == False)
                continue
            model.Add(p1[0].var == True).OnlyEnforceIf(v)
            model.Add(p1[1].var == True).OnlyEnforceIf(v)
            model.Add(p2[0].var == True).OnlyEnforceIf(v)
            model.Add(p2[1].var == True).OnlyEnforceIf(v)
        model.Add(sum(boolvars) == 1)

class Wall:
    """
    Définit un mur entre deux cellules
    """
    def __init__(self, cell1:Cell, cell2:Cell, model:cp_model.CpModel):
        self.cell1 = cell1
        self.cell2 = cell2
        self.var = model.NewBoolVar(f"wall {self.address}")

    @property
    def address(self) -> ADDRESS:
        i1 = self.cell1.index
        i2 = self.cell2.index
        return min(i1,i2), max(i1,i2)

    def neighbors(self) -> List["Wall"]:
        preList = self.cell1.walls() + self.cell2.walls()
        return [w for w in preList if w is not None and w != self]

class Solver:
    __width:int
    __height:int
    __clues:Dict[Tuple[int,int],bool]

    def __init__(self, data:Data):
        self.__width = data.width
        self.__height = data.height
        self.__clues = data.clues

    def solve(self) -> Union[List[Tuple[int,int]], False]:
        # on commence par créer la grille de cellules
        model = cp_model.CpModel()
        walls:Dict[ADDRESS, Wall] = {}
        cells:Dict[Tuple[int,int],Cell] = {}
        for iline in range(self.__height):
            for icol in range(self.__width):
                c = Cell(self.__width, self.__height, iline, icol, cells, walls)
        # on crée ensuite les murs
        for cell in cells.values():
            for cell2 in cell.neighbors():
                if cell2 is None:
                    continue
                w = Wall(cell, cell2,model)
                ad = w.address
                if ad not in walls:
                    walls[ad] = w
        
        # le nombres de connexions pour une cellule donnée devrait être 2 ou 0,
        # 2 dans le cas d'une cellule avec clue
        # la fonction assure également le calcul pour les cases noires et blanches
        for cell in cells.values():
            cell.force_0_or_2(self.__clues, model)

        # reste à coder une contrainte de flux sur le parcours
        # nombre de walls actifs
        N = len(walls)
        n_activ_walls = model.NewIntVar(4, N, f"murs actifs")
        model.Add(n_activ_walls == sum(w.var for w in walls.values()))

        # on ne sait pas où est la racine
        root = {}
        for address in walls:
            root[address] = model.NewBoolVar(f"wall #{address} is root")
            # root doit être active
            model.Add(root[address] <= walls[address].var)

        # Une seule racine
        model.Add(sum(root.values()) == 1)

        # flux boucle
        flux = {}
        for address in walls:
            for n in walls[address].neighbors():
                n_address = n.address
                flux[address, n_address] = model.NewIntVar(0, N, f"flux_{address}->{n_address}")
                # flux seulement entre murs actifs
                model.Add(flux[address, n_address] <= N * walls[address].var)
                model.Add(flux[address, n_address] <= N * walls[n_address].var)

        # conservation du flux
        for address in walls:
            incoming = []
            outgoing = []
            for n in walls[address].neighbors():
                n_address = n.address
                incoming.append(flux[n_address,address])
                outgoing.append(flux[address,n_address])
            delta = sum(incoming) - sum(outgoing)
            model.Add(delta == 1 - n_activ_walls).OnlyEnforceIf(root[address])
            model.Add(delta == walls[address].var).OnlyEnforceIf(root[address].Not())

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
            addresses = [w.address for w in walls.values() if bool(solver.Value(w.var))]
            return self.reorder(addresses)
        return False

    def reorder(self, addresses:List[ADDRESS]) -> List[Tuple[int,int]]:
        """
        reçoit une liste de paires d'index qui forment mis bout à bout une boucle
        construit la liste d'index dans l'ordre et produit la liste de (iline,icol)
        correspondante
        """
        addresses = addresses.copy()
        assert len(addresses) > 1
        indexes = list(addresses.pop())
        while len(addresses) > 1:
            # on veut récupérer une paire commençant par l'index output[-1]
            for i, ad in enumerate(addresses):
                if ad[0] == indexes[-1] or ad[1] == indexes[-1]:
                    break
            else:
                # cas où on ne trouve pas...
                raise ValueError("la solution ne boucle pas !")
            newad = ad[1] if ad[0] == indexes[-1] else ad[0]
            indexes.append(newad)
            addresses.pop(i)
        # le maillon restant devrait pointer sur output[0]
        assert addresses[0][1] == indexes[0] and addresses[0][0] == indexes[-1] \
            or addresses[0][0] == indexes[0] and addresses[0][1] == indexes[-1], "À la fin, solution ne boulce pas !"
        coords =  [(index//self.__width,index%self.__width) for index in indexes]
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

