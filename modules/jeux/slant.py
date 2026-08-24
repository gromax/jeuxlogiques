from typing import List, Union
from modules.tathamdecoder.slant import decoder
from modules.container.slant import Data
from modules.solvers.slant import SlantSolver
from modules.tex.misc import list_to_showList

class Slant:
    __data:Data
    __sol: Union[List[bool], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__data = decoder(options['tatham'])
        solver = SlantSolver(self.__data)
        self.__sol = solver.solve()

    def tex(self):
        output = [
            "%id = "+self.__data.game_id,
            "\\medskip",
            "\n"
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(self.__data.width) + ", " + str(self.__data.height) + ");",
            "\\draw[line width=0.5pt] (0,0) grid[step=1] (" + str(self.__data.width) + ", " + str(self.__data.height) + ");"
        ]

        if self.__sol is not False:
            output += list_to_showList(
                self.__data.width,
                self.__data.height,
                self.__sol,
                cor = True,
                macroname = "slant",
                symbol = lambda v: 'c' if v else 'd'
            )
        output += list_to_showList(
            self.__data.width+1,
            self.__data.height+1,
            self.__data.clues,
            macroname = "islands",
            addDims = [0.3]
        )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

