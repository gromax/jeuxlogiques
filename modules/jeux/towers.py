from typing import List

from modules.container.towers import Data
from modules.tathamdecoder.towers import decoder
from modules.solvers.towers import Solver
from modules.tex.misc import list_to_showList, sideItems
from typing import List, Union

class Towers:
    __data:Data
    __sol:Union[List[int], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__data = decoder(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        S = self.__data.size

        output = [
            "%"+self.__data.game_id,
            "\\begin{tikzpicture}[scale=1.2]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(S) + "," + str(S) +");",
            "\\draw[line width=0.5pt] (0,0) grid[step=1] (" + str(S) + "," + str(S) + ");",
        ]
        output += sideItems(
            S,
            S,
            self.__data.top,
            self.__data.right,
            self.__data.bottom,
            self.__data.left,
            size = 1.5,
            symbol = lambda item: str(item) if item > 0 else ""
        )
        output += list_to_showList(
            S,
            S,
            self.__data.knowns,
            size = 1.5
        )

        if self.__sol is not False:
            output += list_to_showList(
                S,
                S,
                self.__sol,
                size = 1.2,
                cor = True,
                exclude = self.__data.knowns
            )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)




