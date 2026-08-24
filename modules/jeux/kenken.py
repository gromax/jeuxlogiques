from typing import Tuple, List, Union
from modules.tathamdecoder.kenken import TathamKenkenDecoder
from modules.solvers.kenken import KenkenSolver

from modules.primitives.cellgroup import CellGroup

class Kenken:
    __game_id:str
    __constraints:List[Tuple[List[Tuple[int, int]], str, int]]
    __zones:List[CellGroup]
    __size:int
    __sol:Union[List[List[int]], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__game_id = f"tatham id = {options['tatham']}"
        tkd = TathamKenkenDecoder(options["tatham"])
        self.__constraints = tkd.constraints
        self.__size = tkd.size
        self.__zones = tkd.zones
        kenSolver = KenkenSolver(self.__size, self.__constraints)
        self.__sol = kenSolver.solve()


    def __operToTex(self, operName:str, operValue:int) -> str:
        if operName == 'd':
            op = "\\div"
        elif operName == "a":
            op = "+"
        elif operName == "s":
            op = "-"
        else:
            op = "\\times"
        light = f"{operValue}{op}"
        return "$\\bm{" + light +"}$"

    def tex(self):
        output = [
            "%id = "+self.__game_id,
            "\\begin{tikzpicture}[scale=1]",
            "\\begin{scope}[shift={(0," + str(self.__size) + ")}, yscale=-1]",
            "\\draw[line width=.5pt] (0,0) grid[step=1] (" + str(self.__size) + ", " + str(self.__size) + ");"
        ]
        for z in self.__zones:
            output.append(z.cadre().tex())
        for z in self.__zones:
            oper, value = z.data
            opTex = self.__operToTex(oper, value)
            iline, icol = z.getFirstCellCoords()
            tagStr = f"\\draw ({icol},{iline}) node[below right, scale=0.8]{{ {opTex} }};"
            output.append(tagStr)
        output.append("\\end{scope}")
        
        if self.__sol is not False:
            tags = list(map(str, sum(self.__sol, [])))
            texTags = ",\n".join([",".join(tags[i:i+self.__size]) for i in range(0, self.__size**2, self.__size)])
            output.append("\\ifthenelse{\\showCor = 1}{")
            output.append("\\showList{"+str(self.__size)+"}{"+str(self.__size)+"}{ {")
            output.append(texTags)
            output.append("} }{1.5}")
            output.append("}{ }")
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)
