from typing import Dict, Optional, Set, Tuple, List, Any, Union

from modules.primitives.cadre import Cadre
from modules.primitives.cell import Cell

class CellGroup:
    """
    définit une zone de cellules
    une zone est définie par un tag (une lettre) et des coordonnées
    """

    __tag:str
    __coords:Dict[tuple[int,int], Cell]
    __data:Optional[Any]
    __default_cell:Optional[Cell]

    def __init__(self, tag, **options):
        assert set(options) <= {"default"}
        default_cell = options.get("default")
        assert default_cell is None or isinstance(default_cell, Cell)
        self.__tag = tag
        self.__coords:Dict[tuple[int,int], Cell] = {}
        self.__data = None
        self.__default_cell = default_cell
    
    @classmethod
    def make_from_size(cls, tag:str, size:Union[int, Tuple[int,int]], **options):
        """
        Crée une grille de cellules à la taille donnée
        """
        assert set(options) <= {"default"}
        cells = CellGroup(tag, default = options.get("default"))
        if type(size) is int:
            width = size
            height = size
        else:
            width, height = size
        for iline in range(height):
            for icol in range(width):
                cells[iline, icol] = Cell(iline, icol)
        return cells

    @property
    def data(self):
        return self.__data
    
    @data.setter
    def data(self, data_value:Any):
        self.__data = data_value

    def coords(self, **options) -> list[tuple[int,int]]:
        """
        renvoie la liste des coordonnées de la zone
        """
        assert set(options) <= {"filter"}
        filter = options.get("filter")
        if filter is None:
            return list(self.__coords.keys())
        else:
            return [coord for coord, cell in self.__coords.items() if filter(cell)]

    @property
    def tag(self) -> str:
        """
        renvoie le tag de la zone
        """
        return self.__tag

    def __len__(self) -> int:
        """
        renvoie le nombre de cellules de la zone
        """
        return len(self.__coords)

    def __getitem__(self, key):
        assert type(key) == tuple and len(key) == 2
        line, col = key
        if isinstance(line, slice) or isinstance(col, slice):
            return self.__getitem_with_slice(line, col, True)
        if (line, col) not in self.__coords:
            if self.__default_cell is not None:
                return self.__default_cell
            raise KeyError(f"Coordonnées ({line}, {col}) non présentes dans la zone")
        return self.__coords[key]
    
    def has(self, iline:int, icol:int) -> bool:
        """
        renvoie True si la coordonnée est dans la zone
        """
        return (iline,icol) in self.__coords

    def __getitem_with_slice(self, line:Union[int,slice], col:Union[int,slice], cellgroupwanted=True) -> Union[List[Cell],"CellGroup"]:
        if type(line) == int:
            line = slice(line, line+1, 1)
        if type(col) == int:
            col = slice(col, col+1, 1)
        line_max = max(iline for iline,_ in self.__coords)
        col_max = max(icol for _,icol in self.__coords)
        lines = list(range(0,line_max+1))
        cols = list(range(0,col_max+1))
        if cellgroupwanted:
            output = CellGroup(f"{self.__tag}[{line},{col}]")
        else:
            output = []
        for iline in lines[line]:
            for icol in cols[col]:
                if (iline,icol) in self.__coords:
                    cell = self.__coords[iline,icol]
                    if cellgroupwanted:
                        output.add_coord(iline,icol,cell)
                    else:
                        output.append(cell)
        return output

    def __setitem__(self, key, cell:Cell):
        assert type(key) == tuple and len(key) == 2
        line, col = key
        if (line, col) in self.__coords:
            raise KeyError(f"Coordonnées ({line}, {col}) déjà présentes dans la zone")
        self.__coords[key] = cell

    def init_candidates(self, candidates:list[int]):
        """
        candidates: liste des valeurs possibles pour les cellules de la zone
        élimine les possibilités déjà connues dans la zone
        ajoute les possibilités aux cellules restantes
        """
        for v in self.__coords.values():
            v.reinit(candidates)

    def update_candidates(self):
        """
        élimine les candidats impossibles pour les cellules de la zone
        """
        values_knowns = [v for v in self.values() if v != -1]
        for v in self.__coords.values():
            if not v.known:
                v.remove_possibles(values_knowns)

    def cadre(self) -> Cadre:
        """
        renvoie le cadre de la zone
        """
        c = Cadre()
        for iline, icol in self.__coords:
            c = c + Cadre.square(iline, icol)
        return c

    def subGroup(self, filter):
        z = CellGroup(f"{self.__tag}-filtered")
        d:Dict[Tuple[int,int], Cell] = {}
        for coord, cell in self.__coords.items():
            if filter(cell):
                d[coord] = cell
        z.__coords = d
        return z
    
    def is_connexe(self) -> bool:
        ps = self.cadre().paths(brut = True)
        if len(ps) == 0:
            return True
        if len(ps) > 1:
            return False
        p = [(pt.line,pt.col) for pt in ps[0]]
        if (p[0] == p[-1]):
            p.pop()
        # si répétition, alors auto croisement
        return len(set(p)) == len(p)

    @property
    def size(self) -> int:
        """
        renvoie la taille de la zone (nombre de cellules)
        """
        return len(self.__coords)
    
    def add_coord(self, iline:int, icol:int, cell:Optional[Cell]=None):
        """
        iline: ligne
        icol: colonne
        cell: conteneur pour la valeur de la cellule (optionnel)
        ajoute une cellule à la zone
        """
        assert (iline, icol) not in self.__coords
        if cell is None:
            cell = Cell(iline, icol)
        self.__coords[(iline, icol)] = cell

    def remove_coord(self, iline:int, icol:int):
        """
        iline:ligne
        icol:colonne
        enlève s'il existe la cellule en iline, icol
        """
        assert (iline, icol) not in self.__coords
        del self.__coords[(iline,icol)]

    def cells(self, **options) -> List[Cell]:
        """
        renvoie la liste des cellules de la zone
        """
        assert set(options) <= {"filter","key"}, "Option inconnue"
        filter = options.get("filter")
        key = options.get("key")
        if key is not None:
            assert type(key) == tuple and len(key) == 2
            line, col = key
            cells = self.__getitem_with_slice(line, col, False)
        else:
            cells = self.__coords.values()
        if filter is None:
            return cells
        else:
            return [c for c in cells if filter(c)]

    def has_double(self) -> bool:
        vals = [cell.value for cell in self.__coords.values() if cell.known]
        if len(vals) != len(set(vals)):
            return True
        return False
    
    def getCell(self, iline:int, icol:int) -> Cell:
        """
        renvoie la valeur d'une cellule de la zone
        """
        assert (iline, icol) in self.__coords
        return self.__coords.get((iline,icol))
    
    def getFirstCellCoords(self) -> Tuple[int,int]:
        """
        renvoie les coordonnées de la première cellules en ordre lexicographique
        (première ligne, puis première colonne)
        """
        coords = list(self.__coords.keys())
        minline = min([iline for iline, _ in coords])
        mincol = min([icol for iline, icol in coords if iline == minline])
        return (minline, mincol)
    
    def allKnown(self) -> bool:
        """
        renvoie True si toutes les cellules de la zone ont une valeur connue, False sinon
        """
        return all([v.known for v in self.__coords.values()])
    
    def hasNoValueCell(self) -> bool:
        """
        renvoie True si la zone contient une cellule sans valeur connue, False sinon
        """
        return any([True for v in self.__coords.values() if len(v) == 0])
    
    def values(self) -> Set[int]:
        """
        renvoie la liste des valeurs connues de la zone
        """
        values = [cell.value for cell in self.__coords.values()]
        return {v for v in values if v != -1}
    
    def ordered_values(self) -> List[int]:
        """
        renvoie la liste des valeurs dans l'ordre lexicographique
        """
        lcv = [(iline, icol, cell.value) for (iline,icol), cell in self.__coords.items()]
        lcv.sort() # lexicographique
        _, _, v = zip(*lcv)
        return v

