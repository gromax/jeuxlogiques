from typing import List, Union
from modules.tathamdecoder.undead import decoder
from modules.solvers.undead import Solver
from modules.container.undead import Data
from modules.tex.misc import sideItems, list_to_showList

class Undead:
    __data:Data
    __sol: Union[List[str], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__data = decoder(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self):
        output = [
            "%id = "+self.__data.game_id,
            f"{{\\Large G = {self.__data.ghosts} \\quad V = {self.__data.vampires} \\quad Z = {self.__data.zombies} }}",
            "\\medskip",
            "\n"
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(self.__data.width) + ", " + str(self.__data.height) + ");",
            "\\draw[line width=0.2pt] (0,0) grid[step=1] (" + str(self.__data.width) + ", " + str(self.__data.height) + ");"
        ]
        output += list_to_showList(
            self.__data.width,
            self.__data.height,
            self.__data.mirrors,
            default = " ",
            symbol = lambda item: "L" if item is True else "R",
            macroname = "undead",
        )
        output += sideItems(
            self.__data.width,
            self.__data.height,
            self.__data.top,
            self.__data.right,
            self.__data.bottom,
            self.__data.left,
            size = 1.5
        )
        if self.__sol is not False:
            output += list_to_showList(
                self.__data.width,
                self.__data.height,
                self.__sol,
                size = 1,
                cor = True
            )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)
