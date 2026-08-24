from modules.primitives.coord import Coord

from typing import List, Dict, Tuple, Optional

class Segment:
    """
    définit un segment entre deux points
    """
    __points:Tuple[Coord, Coord]

    def __init__(self, p1:Coord, p2:Coord):
        self.__points = (p1, p2)
    
    def __getitem__(self, key:int) -> Coord:
        """
        renvoie le point d'indice key (0 ou 1) du segment
        permet l'indexation du segment, par exemple s[0] pour le point de départ, s[1] pour le point d'arrivée
        """
        if key not in (0,1):
            raise IndexError("Segment index out of range")
        return self.__points[key]
    
    def __eq__(self, other:"Segment") -> bool:
        """
        renvoie True si self et other représentent le même segment (même points de départ et d'arrivée), False sinon
        """
        return self.__points == other.__points
    
    @property
    def end(self) -> Coord:
        """
        renvoie le point d'arrivée du segment
        """
        return self.__points[1]
    
    @property
    def start(self) -> Coord:
        """
        renvoie le point de départ du segment
        """
        return self.__points[0]
    
    def is_after(self, other:"Segment") -> bool:
        """
        renvoie True si self est après other, c'est à dire que le point de départ de self est égal au point d'arrivée de other
        """
        return self.start == other.end
    
    def is_inline(self, other:"Segment") -> bool:
        """
        renvoie True si self vient après other et
        si les deux vecteurs sont colinaires
        """
        if not self.is_after(other):
            return False
        return (other.end - other.start).colinear(self.end-self.start)
    
    def opposite(self) -> "Segment":
        """
        renvoie le segment opposé à self
        """
        p1, p2 = self.__points
        return Segment(p2, p1)
    
    def __str__(self) -> str:
        """
        renvoie une chaîne représentant le segment
        """
        p1, p2 = self.__points
        return f"{p1} -- {p2}"
    
if __name__ == '__main__':
    a = Coord(4,5)
    b = Coord(4,6)
    c = Coord(4,7)
    d = Coord(2,8)
    assert Segment(a, b) == Segment(a, b)
    assert Segment(a,b) != Segment(c,d)
    assert Segment(a,b).start == a
    assert Segment(a,b).end == b
    assert Segment(a,b).is_after(Segment(c,a))
    assert not Segment(a,b).is_after(Segment(c,d))
    assert Segment(b,c).is_inline(Segment(a,b))
    assert not Segment(b,c).is_inline(Segment(d,b))