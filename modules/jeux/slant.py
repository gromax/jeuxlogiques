from typing import Tuple, List, Union, Dict
from modules.tathamdecoder.slant import TathamSlantDecoder
from modules.solvers.slant import SlantSolver
from modules.tex.misc import list_to_showList

class Slant:
    __game_id:str
    __width:int
    __height:int
    __constraints:Dict[Tuple[int,int], int]
    __sol: Union[List[bool], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__game_id = f"tatham id = {options['tatham']}"
        tsd = TathamSlantDecoder(options["tatham"])
        self.__width = tsd.width
        self.__height = tsd.height
        self.__game_id = tsd.game_id
        self.__constraints = tsd.constraints
        solver = SlantSolver(self.__width, self.__height, self.__constraints)
        self.__sol = solver.solve()

    def tex(self):
        output = [
            "%id = "+self.__game_id,
            "\\medskip",
            "\n"
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(self.__width) + ", " + str(self.__height) + ");",
            "\\draw[line width=0.5pt] (0,0) grid[step=1] (" + str(self.__width) + ", " + str(self.__height) + ");"
        ]

        if self.__sol is not False:
            output += list_to_showList(
                self.__width,
                self.__height,
                self.__sol,
                size = -1,
                cor = True,
                macroname = "slant",
                symbol = lambda v: 'c' if v else 'd'
            )
        output += list_to_showList(
            self.__width+1,
            self.__height+1,
            self.__constraints,
            size = 1,
            macroname = "islands",
            addDims = [0.3]
        )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

