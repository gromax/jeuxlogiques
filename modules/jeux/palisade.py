from typing import List, Dict, Tuple, Union

from modules.primitives.cellgroup import CellGroup
from modules.solvers.palisade import Solver
from modules.container.palisade import Data
from modules.tex.misc import list_to_showList

class Palisade:
    __data:Data
    __sol:Union[List[int], False]

    def __init__(self, **options):
        """
        initialise les cellules selon le code fournit
        """
        assert set(options) <= {"tatham"}, "options incorrectes"
        self.__data = Data.decode(options["tatham"])
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
            # tracer un cadre pour chaque zone
            NZ = self.__data.zoneSize
            output.append("\\ifthenelse{\\showCor=1}{")
            output.append("\\begin{scope}[shift={(0,"+str(h)+")}, yscale=-1]")
            for iZone in range(1, NZ+1):
                cells = CellGroup(f"zone #{iZone}")
                coords = [(index//w, index%w) for (index, value) in enumerate(self.__sol) if value == iZone]
                cells.add_coords(coords)
                output.append(cells.cadre().tex())
            output.append("\\end{scope}")
            output.append("}{ }")
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

