from typing import List, Union
from modules.primitives.direction import Direction
from modules.solvers.adjacent import Solver
from modules.tex.misc import list_to_showList
from modules.container.adjacent import Data

class Adjacent:
    """
    Grille de jeu pour unequal
    """
    __data:Data
    __sol:Union[List[int], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__data = Data.decode(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def __adj_symbols(self) -> List[str]:
        output = []
        # seulement les Right et Down (car en doublons)
        for (iline,icol,d), b in self.__data.constraints.items():
            if not b:
                continue
            if d == Direction.UP or d == Direction.LEFT:
                continue
            output.append(f"{icol}/{iline}/{d.tex_angle()}")
        return output

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        S = self.__data.size
        output = ["% "+self.__data.game_id]
        output.append("\\begin{tikzpicture}[scale=1.5]")
        output.append("\\inequalGrid{"+str(S)+"}")
        output.append("\\begin{scope}[shift={(0.5,"+str(S-0.5)+")}, yscale=-1]")

        adjSymbols = self.__adj_symbols()
        if len(adjSymbols)>0:
            output.append("  \\foreach \\x/\\y/\\r in {" + ", ".join(adjSymbols) + "} {")
            output.append("    \\begin{scope}[shift={(\\x,\\y)}, rotate=\\r] \\draw[line width=4pt, black!50!white] (.5,-.3) --++ (0,.6);\\end{scope}")
            output.append("  }")
        output.append("\\end{scope}")

        output += list_to_showList(S, S, self.__data.knowns,
            size = 1.5
        )
        if self.__sol is not False:
            output += list_to_showList(S, S, self.__sol,
                size = 1.5,
                cor = True
            )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

