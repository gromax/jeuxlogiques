from typing import List, Union
from modules.htmldecoder.norinori import decode_html
from modules.container.norinori import Data
from modules.solvers.norinori import Solver
from modules.tex.misc import list_to_showList

class Game:
    __data:Data
    __sol:Union[List[bool], False]
    def __init__(self, **options):
        assert set(options) <= {"url", "tatham"}, "options incorrectes"
        # pour l'instant seulement avec url
        assert "url" in options or "tatham" in options, "option url ou tatham obligatoire"
        if "url" in options:
            self.__data = decode_html(options["url"])
        else:
            self.__data = Data.decode(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self):
        game_id = self.__data.game_id
        h = self.__data.height
        w = self.__data.width
        zones = self.__data.zones
        output = [
            "% norinori",
            f"% {game_id}"
            "\\begin{tikzpicture}[scale=1]"
        ]
        if self.__sol is not False:
            output += list_to_showList(
                w,
                h,
                self.__sol,
                cor = True,
                macroname = "showColorList",
                symbol = lambda v: 'k' if v else ' '
            )
        ouput += [
            "\\begin{scope}[shift={(0," + str(h) + ")}, yscale=-1]",
            "\\draw[line width=.5pt] (0,0) grid[step=1] (" + str(w) + ", " + str(h) + ");"
        ]
        for z in zones:
            output.append(z.cadre().tex())
        output.append("\\end{scope}")
        
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)
