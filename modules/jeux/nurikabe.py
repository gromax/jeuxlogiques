from typing import List, Union
from modules.htmldecoder.nurikabe import decode_html
from modules.container.nurikabe import Data
from modules.solvers.nurikabe import Solver
from modules.tex.misc import list_to_showList

class Nurikabe:
    __data:Data
    __sol:Union[List[bool], False]

    def __init__(self, **options):
        assert set(options) <= {"url", "tatham"}, "options incorrectes"
        assert "url" in options or "tatham" in options, "option url ou tatham obligatoire"
        if "url" in options:
            self.__data = decode_html(options["url"])
        else:
            self.__data = Data.decode(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self):
        w = self.__data.width
        h = self.__data.height
        output = [
            "%id="+self.__game_id,
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(w) + ", " + str(h) + ");",
            "\\draw[line width=.5pt] (0,0) grid[step=1] (" + str(w) + ", " + str(h) + ");"
        ]

        # solution
        if self.__sol is not False:
            output += list_to_showList(
                w,
                h,
                self.__sol,
                cor = True,
                macroname = "showColorList",
                symbol = lambda v: 'k' if v else ' '
            )

        # problème
        output += list_to_showList(
            w,
            h,
            self.__data.clues,
            size = 1
        )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)
