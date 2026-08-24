from typing import Optional, Union, Set, List, Any, Tuple

class Cell:
    """
    représente une valeur d'une cellule d'une grille type sudoku
    value : la valeur actuelle de la cellule, -1 si elle n'est pas encore connue
    candidates : les valeurs possibles pour cette cellule, si elle n'est pas encore connue
    initial : la valeur initiale de la cellule, -1 si elle n'est pas donnée
    """

    __initial:int
    __candidates:Set[int]
    __cached_candidates:Optional[Set[int]]
    __iline:int
    __icol:int
    data:Any # à usage divers

    def __init__(self, iline:int, icol:int, initial:int = -1):
        self.__initial = initial
        self.__candidates = set() if initial == -1 else {initial}
        self.__cached_candidates = None
        self.__iline = iline
        self.__icol = icol
        self.data = None

    @property
    def iline(self)->int:
        return self.__iline
    
    @property
    def icol(self)->int:
        return self.__icol

    @property
    def pos(self) -> Tuple[int,int]:
        return self.__iline, self.__icol

    def __len__(self):
        """
        renvoie le nombre de valeurs possibles pour cette cellule
        """
        return len(self.__candidates)

    def set_initial(self, initial:int):
        """
        Fixe la valeur initial
        """
        assert initial != -1
        self.__initial = initial
        self.__candidates = {initial}
        self.__cached_candidates = None

    @property
    def value(self) -> int:
        """
        renvoie la valeur actuelle de la cellule, -1 si elle n'est pas encore connue
        """
        if (len(self.__candidates) != 1):
            return -1
        return next(iter(self.__candidates))

    @value.setter
    def value(self, value:int):
        assert self.__initial == -1 or self.__initial == value, "Cannot change the value of a cell with an initial value"
        self.__candidates = {value}

    @property
    def candidates(self) -> Set[int]:
        """
        renvoie l'ensemble des valeurs possibles pour cette cellule
        """
        return self.__candidates.copy()

    def has(self, candidate:int) -> bool:
        """
        renvoie True si le candidat proposé est possible
        """
        return candidate in self.__candidates

    def remove_candidate(self, val:int):
        """
        retire une valeur possible pour cette cellule
        """
        self.__candidates.discard(val)
    
    def remove_possibles(self, values:List[int]):
        """
        retire les valeurs des possibilités d'une cellule
        """
        for v in values:
            self.__candidates.discard(v)

    def add_candidate(self, candidate:int):
        self.__candidates.add(candidate)

    def reinit(self, values:list[int]):
        """
        réinitialise les valeurs possibles pour cette cellule
        """
        if (self.__initial != -1):
            self.__candidates = {self.__initial}
        else:
            self.__candidates = set(values)

    def __eq__(self, other:Union[int, "Cell"]) -> bool:
        """
        renvoie True si self et other représentent la même valeur de cellule
         (même valeur actuelle, même valeur initiale, mêmes possibles)
         False sinon
        """
        if isinstance(other, int):
            return self.value == other
        return other.value == self.value

    @property
    def known(self) -> bool:
        """
        renvoie True si la valeur de la cellule est connue, False sinon
        """
        return len(self.__candidates) == 1
    
    @property
    def is_initial(self) -> bool:
        """
        renvoie True si la valeur de la cellule est une valeur initiale, False sinon
        """
        return self.__initial != -1

    def __str__(self) -> str:
        """
        renvoie une chaîne représentant la valeur de la cellule, '?' si elle n'est pas encore connue
        """
        return str(self.value) if self.known else '?'

    def next(self) -> bool:
        """
        assigne la prochaine valeur possible et renvoie les valeurs laissées de côté
        si il y en a une, False sinon
        met en cache les valeurs possibles mises de côté
        """
        if len(self.__candidates) == 0:
            return False
        v = next(iter(self.__candidates))
        p = self.__candidates.copy()
        p.remove(v)
        self.value = v
        self.__cached_candidates = p
        return True
    
    def uncache(self):
        """
        réinitialise les valeurs possibles à celles mises de côté par next()
        """
        assert self.__cached_candidates is not None, "No cached possibles to uncache"
        self.__candidates = self.__cached_candidates
        self.__cached_candidates = None
