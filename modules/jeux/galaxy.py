from typing import List, Tuple, Union
from modules.primitives.cellgroup import CellGroup
from modules.tathamdecoder.galaxy import TathamGalaxyDecoder
from modules.solvers.galaxy import GalaxySolver

class Galaxy:
    __game_id:str
    __height:int
    __width:int
    __stars:List[Tuple[int,int]]
    __sol:Union[List[List[int]], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seule possibilité : tatham
        assert "tatham" in options
        tgd = TathamGalaxyDecoder(options["tatham"])
        self.__game_id = f"tatham id = {tgd.game_id}"
        self.__height = tgd.height
        self.__width = tgd.width
        self.__stars = tgd.stars
        gs = GalaxySolver(self.__height, self.__width, self.__stars)
        self.__sol = gs.solve()

    def __groups(self):
        assert self.__sol is not False
        groups = {}
        for iline, line in enumerate(self.__sol):
            for icol, k in enumerate(line):
                g:CellGroup = groups.get(k, CellGroup(f"G{k}"))
                g.add_coord(iline,icol)
                if k not in groups:
                    groups[k] = g
        return groups

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        output = ["%id: "+self.__game_id]
        output.append("\\begin{tikzpicture}[scale=.7]")
        output.append("\\draw[line width=0.5pt] (0,0) grid[step=1] ("+str(self.__width)+","+str(self.__height)+");")
        output.append("\\begin{scope}[shift={(0,"+str(self.__height)+")}, yscale=-1]")
        output.append("\\foreach \\x/\\y in {"+",".join(f"{icol/2+.5}/{iline/2+.5}" for iline,icol in self.__stars)+"} \\draw[fill=white] (\\x,\\y) circle(0.3);")
        if self.__sol is not False:
            output.append("\\ifthenelse{\\showCor = 1}{")
            for g in self.__groups().values():
                output.append(g.cadre().tex())
            output.append("}{ }")
        output.append("\\end{scope}")
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

