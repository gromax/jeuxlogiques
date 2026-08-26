from typing import List, Union
from modules.container.pearl import Data
from modules.solvers.pearl import Solver
from modules.tex.misc import list_to_showList

class Game:
    __data:Data
    __sol:Union[List[int], False]
    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        self.__data = Data.decode(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self):
        w = self.__data.width
        h = self.__data.height
        clues = self.__data.clues
        output = [
            "%id="+self.__data.game_id,
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=.5pt] (0,0) rectangle (" + str(w) + ", " + str(h) + ");",
            "\\draw[line width=.1pt] (0,0) grid[step=1] (" + str(w) + ", " + str(h) + ");"
        ]

        # solution
        if self.__sol is not False:
            path = " -- ".join(f"({j},{i})" for (i,j) in self.__sol) + " -- cycle;"
            output.append("\\ifthenelse{\\showCor = 1}{")
            output.append("\\begin{scope}[shift={(0.5,"+str(h-0.5)+")}, yscale=-1]")
            output.append("\\draw[line width=2pt] "+path)
            output.append("\\end{scope}")
            output.append("}{ }")

        # problème
        output += list_to_showList(
            w,
            h,
            clues,
            cor = False,
            default = ' ',
            macroname = "showCircleList",
            symbol = lambda v: 'N' if v is True else 'B',
            addDims = [0.3]
        )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)
