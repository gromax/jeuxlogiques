from typing import Tuple, List, Union, Dict
from modules.tathamdecoder.techtonic import TathamTechtonicDecoder
from modules.solvers.techtonic import TechtonicSolver

from modules.primitives.cellgroup import CellGroup

class Techtonic:
    __game_id:str
    __numbers:Dict[Tuple[int, int], int]
    __zones:List[CellGroup]
    __width:int
    __height:int
    __sol:Union[List[List[int]], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__game_id = f"tatham id = {options['tatham']}"
        ttd = TathamTechtonicDecoder(options["tatham"])
        self.__numbers = ttd.numbers
        self.__width = ttd.width
        self.__height = ttd.height
        self.__zones = ttd.zones
        solver = TechtonicSolver(self.__width, self.__height, self.__numbers, self.__zones)
        self.__sol = solver.solve()

    def tex(self):
        output = [
            "%id = "+self.__game_id,
            "\\begin{tikzpicture}[scale=1]",
            "\\begin{scope}[shift={(0," + str(self.__height) + ")}, yscale=-1]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(self.__width) + ", " + str(self.__height) + ");",
            "\\draw[line width=.5pt] (0,0) grid[step=1] (" + str(self.__width) + ", " + str(self.__height) + ");"
        ]
        for z in self.__zones:
            output.append(z.cadre().tex())
        output.append("\\end{scope}")
        output += self.__numbers_to_tex()
        
        output += self.__sol_to_tex()

        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

    def __numbers_to_tex(self) -> List[str]:
        L = ["\\showListYShift{"+ str(self.__width) + "}{"+ str(self.__height) + "}{ {"]
        for i in range(self.__height):
            line = []
            for j in range(self.__width):
                if (i,j) in self.__numbers:
                    line.append(str(self.__numbers[i,j]))
                else:
                    line.append(" ")
            L.append(",".join(line)+',')
        L.append("} }{ 1.5 }")
        return L
    
    def __sol_to_tex(self) -> list[str]:
        if self.__sol is False:
            return []
        L = [
            "\\ifthenelse{\\showCor = 1}{",
            "\\showListYShift{"+ str(self.__width) + "}{"+ str(self.__height) + "}{ {"
        ]
        for i in range(self.__height):
            line = []
            for j in range(self.__width):
                if (i,j) in self.__numbers:
                    # on ne double pas ce qui est déjà écrit par le sujet
                    line.append(" ")
                else:
                    line.append(str(self.__sol[i][j]))
            L.append(",".join(line)+',')
        L.append("} }{ 1 }")
        L.append("}{ }")
        return L
