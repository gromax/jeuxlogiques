from typing import List, Tuple
from modules.primitives.coord import Coord
from modules.primitives.segment import Segment

class Cadre:
    """
    définit un cadre tracé dans l'ordre horaire
    """

    __segments:List[Segment]

    def __init__(self):
        self.__segments:List[Segment] = []

    def add_segment(self, s:Segment):
        """
        ajoute un segment au cadre
        si le segment opposé est déjà présent, il est supprimé
        """
        sopp = s.opposite()
        if sopp in self.__segments:
            self.__segments.remove(sopp)
        else:
            self.__segments.append(s)

    def add_segment_coord(self, iline1:int, icol1:int, iline2:int, icol2:int):
        """
        ajoute un segment défini par ses coordonnées
        """
        c1 = Coord(iline1, icol1)
        c2 = Coord(iline2, icol2)
        s = Segment(c1, c2)
        self.add_segment(s)

    @classmethod
    def square(cls, iline:int, icol:int) -> "Cadre":
        """
        renvoie le cadre d'une cellule définie par ses coordonnées line, col
        """
        c = Cadre()
        c.add_segment_coord(iline, icol, iline, icol+1)
        c.add_segment_coord(iline, icol+1, iline+1, icol+1)
        c.add_segment_coord(iline+1, icol+1, iline+1, icol)
        c.add_segment_coord(iline+1, icol, iline, icol)
        return c
    
    def __add__(self, other:"Cadre") -> "Cadre":
        """
        concatène deux cadres
        """
        c = Cadre()
        c.__segments = self.__segments.copy()
        for s in other.__segments:
            c.add_segment(s)
        return c

    def __sub__(self, other:"Cadre") -> "Cadre":
        """
        soustrait un cadre d'un autre
        """
        c = Cadre()
        c.__segments = self.__segments.copy()
        for s in other.__segments:
            c.add_segment(s.opposite())
        return c

    def opposite(self) -> "Cadre":
        """
        renvoie le cadre opposé
        """
        c = Cadre()
        for s in self.__segments:
            c.add_segment(s.opposite())
        return c

    def __index_with_start_point(self, start:Coord, segs:List[Segment])->int:
        """
        renvoie l'index du premier segment de segs qui commence par start, ou -1 si aucun
        """
        for i, s in enumerate(segs):
            if s.start == start:
                return i
        return -1
            
    def paths(self, **options) -> List[List[Coord]]:
        """
        renvoie une liste de liste de coordonnées.
        chaque sous liste est un chemin correspondant à un cadre, fermé ou pas.
        """
        assert set(options) <= {"brut"}
        brut = (options.get("brut") == True)
        segs = self.__segments.copy()
        paths = []
        current_path = None
        while segs != []:
            if current_path is None:
                s = segs.pop()
                current_path = [s.start, s.end]
                continue
            inext = self.__index_with_start_point(current_path[-1], segs)
            if inext == -1:
                paths.append(current_path)
                current_path = None
            current_path.append(segs.pop(inext).end)
            if current_path[-1] == current_path[0]:
                paths.append(current_path)
                current_path = None
        if brut:
            return paths
        return [self.__reduce_path(p) for p in paths]
    
    def __reduce_path(self, path:List[Coord]) -> List[Coord]:
        """
        path: liste de coordonnées formant un chemin fermé ou pas
        renvoie une liste de coordonnées formant le même chemin, mais en supprimant les points alignés
         et en supprimant le point de départ s'il est aligné avec les deux points suivants
        """
        if len(path) < 3:
            return path
        n = len(path)
        new_path = path[0:1] # on garde le premier point, on va ajouter les suivants (ou pas)
        for i in range(1,n-1):
            a,b,c = path[i-1:i+2]
            if Coord.aligned(a, b, c):
                continue
            new_path.append(b)
        new_path.append(path[-1])
        # à ce stade, on a supprimé les points intérieurs alignés,
        # mais conservé les extrémités
        if len(new_path) < 4 or new_path[0] != new_path[-1]:
            return new_path
        # il faut voir si la première extrémité est un coin
        new_path.pop()
        b = new_path[0]
        c = new_path[1]
        a = new_path[-1]
        if Coord.aligned(a,b,c):
            # on peut supprimer le premier
            new_path.pop(0)
        new_path.append(new_path[0])
        return new_path
    
    def __margin_path(self, path:List[Coord], margin:float) -> List[Coord]:
        """
        path: liste de coordonnées formant un chemin fermé ou pas
        margin: distance à laquelle on veut décaler le chemin
        renvoie une liste de coordonnées formant un chemin parallèle à path, à distance margin, et qui se trouve du côté droit de path
        """
        if len(path) <= 2:
            return path
        new_path = path.copy()
        
        loop = (path[0] == path[-1])
        if loop:
            new_path.pop()
        n = len(new_path)
        for i in range(n - int(not loop)):
            a = new_path[i]
            b = new_path[(i+1)%n]
            vec = (b-a).normalized().rot_right().scale(margin)
            new_path[i] = (a + vec)
            new_path[(i+1)%n] = (b + vec)
        if loop:
            new_path.append(new_path[0])
        return new_path

    def tex(self, **options) -> str:
        """
        renvoie le code tex pour le cadre
        options:
          style de ligne après le draw
          width: épaisseur de la ligne (ex: "2pt")
          dashed: si True, la ligne est en pointillés
        """
        assert set(options) <= {"style", "width", "dashed", "margin"}
        styles = []
        if options.get("style"):
            styles.append(options.get("style"))
        if len(styles) == 0 or options.get("width"):
            width = options.get("width", "2pt")
            styles.append(f"line width={width}")
        if options.get("dashed"):
            styles.append("dashed")
        margin = options.get("margin", 0)
       
        n = len(self.__segments)
        if n == 0:
            return ""
        paths = self.paths()
        if margin!=0:
            paths = [self.__margin_path(p, margin) for p in paths]
        all_lines = []
        for p in paths:
            pts = [str(pt) for pt in p]
            if pts[0] == pts[-1]:
                pts[-1] = "cycle"
            current_line = f"\\draw[{", ".join(styles)}] {" -- ".join(pts)};"
            all_lines.append(current_line)
        return "\n".join(all_lines)
    
if __name__ =='__main__':
    c1 = Cadre.square(2,0)
    c2 = Cadre.square(2,1)
    c3 = Cadre.square(2,2)
    c4 = Cadre.square(2,3)
    c5 = Cadre.square(1,1)
    c = c1  + c2  + c3 + c4 + c5
    print(c.tex(margin=.1, dashed=True))
