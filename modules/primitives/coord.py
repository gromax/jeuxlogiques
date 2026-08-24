from math import sqrt

class Coord:
    """
    Objet représentant une paire de coordonnées dans le plan
    y est dirigé vers le bas, x vers la droite
    permet des calculs vectoriels simples
    """
    __iline:float
    __icol:float

    @classmethod
    def aligned(cls, a:"Coord", b:"Coord", c:"Coord") -> bool:
        """
        renvoie True si les points a, b et c sont alignés, False sinon
        """
        AB = b - a
        AC = c - a
        return AB.colinear(AC)

    @classmethod
    def makexy(cls, x:float, y:float) -> "Coord":
        """
        x: coordonnée x
        y: coordonnée y
        renvoie un objet Coord correspond à icol=x et iline=y
        """
        return Coord(y, x)

    def rot_right(self) -> "Coord":
        """
        renvoie le vecteur tourné de 90° sens horaire
        """
        return Coord(self.x, -self.y)

    def scale(self, a:float) -> "Coord":
        """
        renvoie le vecteur multiplié par a
        """
        return Coord(a*self.__iline, a*self.__icol)
    
    def __add__(self, other:"Coord") -> "Coord":
        """
        renvoie la somme de self et other
        """
        return Coord(self.__iline + other.__iline, self.__icol + other.__icol)
    
    def __sub__(self, other:"Coord") -> "Coord":
        """
        renvoie la différence de self et other
        """
        return Coord(self.__iline - other.__iline, self.__icol - other.__icol)

    def colinear(self, other:"Coord") -> bool:
        """
        renvoie True si self et other sont colinéaires, False sinon
        """
        return self.x*other.y - self.y*other.x == 0

    def norm(self) -> float:
        """
        renvoie la norme du vecteur
        """
        return sqrt(self.x**2 + self.y**2)
    
    def normalized(self) -> "Coord":
        """
        renvoie le vecteur normalisé
        """
        n = self.norm()
        if n == 0:
            return self
        return Coord(self.__iline/n, self.__icol/n)

    def __init__(self, iline:float, icol:float):
        self.__iline = iline
        self.__icol = icol
    
    def __str__(self)->str:
        """
        renvoie une chaîne représentant les coordonnées
        """
        return f"({self.x},{self.y})"
    
    @property
    def x(self)->float:
        """
        renvoie la coordonnée x
        """
        return self.__icol

    @property
    def line(self)->int:
        """
        renvoie l'indice de la ligne
        """
        return int(round(self.__iline, 0))

    @property
    def col(self)->int:
        """
        renvoie l'indice de la colonne
        """
        return int(round(self.__icol,0))

    @property
    def y(self)->float:
        """
        renvoie la coordonnée y
        """
        return self.__iline

    def __eq__(self, other:"Coord") -> bool:
        """
        renvoie True si self et other représentent les mêmes coordonnées
         (même iline et même icol)
         False sinon
        """
        return self.__iline == other.__iline and self.__icol == other.__icol
 

if __name__ == '__main__':
    c = Coord(4,5)
    assert str(c) == "(5,4)"
    d = Coord(4,5)
    assert c == d