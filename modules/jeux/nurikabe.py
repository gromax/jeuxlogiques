from typing import Tuple, List, Union, Dict
from modules.htmldecoder.nurikabe import NurikabeHtmlDecoder
from modules.tathamdecoder.nurikabe import TathamNurikabeDecoder
from modules.solvers.nurikabe import Solver
from modules.tex.misc import list_to_showList

class Nurikabe:
    __content:Dict[Tuple[int,int], int]
    __size:int
    __sol:Union[List[bool], False]
    __game_id:str

    def __init__(self, **options):
        assert set(options) <= {"url", "tatham"}, "options incorrectes"
        # pour l'instant seulement avec url
        assert "url" in options or "tatham" in options, "option url ou tatham obligatoire"
        if "url" in options:
            yd = NurikabeHtmlDecoder(options["url"])
            self.__content = yd.content
            self.__size = yd.size
            self.__game_id = yd.game_id
        else:
            yd = TathamNurikabeDecoder(options["tatham"])
            self.__content = yd.content
            self.__size = yd.size
            self.__game_id = yd.game_id
        solver = Solver(self.__size, self.__content)
        self.__sol = solver.solve()

    def tex(self):
        output = [
            "%id = "+self.__game_id,
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(self.__size) + ", " + str(self.__size) + ");",
            "\\draw[line width=.5pt] (0,0) grid[step=1] (" + str(self.__size) + ", " + str(self.__size) + ");"
        ]

        # solution
        if self.__sol is not False:
            output += list_to_showList(
                self.__size,
                self.__size,
                self.__sol,
                cor = True,
                macroname = "showColorList",
                symbol = lambda v: 'k' if v else ' '
            )

        # problème
        output += list_to_showList(
            self.__size,
            self.__size,
            self.__content,
            size = 1
        )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)
