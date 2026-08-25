from typing import List, Dict, Tuple, Union

from modules.tathamdecoder.loopy import decoder
from modules.primitives.cellgroup import CellGroup
from modules.solvers.loopy import Solver
from modules.container.loopy import Data
from modules.tex.misc import list_to_showList

class Loopy:
    __data:Data
    __sol:Union[List[bool], False]

    def __init__(self, **options):
        """
        initialise les cellules selon le code fournit
        """
        assert set(options) <= {"tatham"}, "options incorrectes"
        self.__data = decoder(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        w = self.__data.width
        h = self.__data.height
        output = ["%id="+self.__data.game_id]
        output.append("\\begin{tikzpicture}[scale=.7]")
        output.append("\\draw[line width=0.5pt] (0,0) grid[step=1] ("+str(w)+","+str(h)+");")
        output += list_to_showList(
            w,
            h,
            self.__data.clues,
            size = 1.5,
            default = " "
        )
        if self.__sol is not False:
            cells = CellGroup("interior")
            coords = [(index//w, index%w) for (index, value) in enumerate(self.__sol) if value is True]
            cells.add_coords(coords)
            output.append("\\ifthenelse{\\showCor=1}{")
            output.append("\\begin{scope}[shift={(0,"+str(h)+")}, yscale=-1]")
            output.append(cells.cadre().tex())
            output.append("\\end{scope}")
            output.append("}{ }")
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

