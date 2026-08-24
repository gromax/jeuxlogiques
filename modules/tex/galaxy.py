from typing import List, Tuple, Union
from modules.primitives.cellgroup import CellGroup

class TexGalaxy:
    __game_id:str
    __height:int
    __width:int
    __stars:List[Tuple[int,int]]
    __sol:Union[List[List[int]], False]

    def __init__(self, game_id:str, height:int, width:int, stars:List[Tuple[int,int]], sol:Union[List[List[int]], False]):
        self.__game_id = game_id
        self.__height = height
        self.__width = width
        self.__stars = stars
        self.__sol = sol

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

