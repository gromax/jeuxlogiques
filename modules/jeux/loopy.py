from typing import List, Dict, Tuple, Union

from modules.tathamdecoder.loopy import TathamLoopyDecoder
from modules.primitives.cellgroup import CellGroup
from modules.solvers.loopy import LoopySolver


class Loopy:
    __game_id:str
    __size:int
    __values:Dict[Tuple[int,int],int]
    __sol:Union[List[List[bool]], False]

    def __init__(self, **options):
        """
        initialise les cellules selon le code fournit
        ex: a22d3c1b3022a3c3a2b02b2b1b31a1d2b signifie que l'on saute 1 case puis 2 puis 2 puis saute 4 cases (d)...
        """
        assert set(options) <= {"tatham"}, "options incorrectes"
        if "tatham" in options:
            tld = TathamLoopyDecoder(options["tatham"])
            self.__game_id = tld.game_id
            self.__size = tld.size
            self.__constraints = tld.constraints
            loopy_solver = LoopySolver(self.__size, self.__constraints)
            self.__sol = loopy_solver.solve()
            return
        raise ValueError("Loopy n'a pas les bons arguments")

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        output = ["%id: "+self.__game_id]
        output.append("\\begin{tikzpicture}[scale=.7]")
        output.append("\\draw[line width=0.5pt] (0,0) grid[step=1] ("+str(self.__size)+","+str(self.__size)+");")
        vals = [f"{icol}/{iline}/{value}" for (iline,icol), value in self.__constraints.items()]
        if len(vals) > 0:
            output.append("\\begin{scope}[shift={(0.5,"+str(self.__size-0.5)+")}, yscale=-1]")
            output.append("\\foreach \\x/\\y/\\c in {" + ", ".join(vals) + "} \\draw (\\x,\\y) node[scale=1.5]{\\c};")
            output.append("\\end{scope}")
        if self.__sol is not False:
            cells = CellGroup("interior")
            for iline in range(self.__size):
                for icol in range(self.__size):
                    if self.__sol[iline][icol]:
                        cells.add_coord(iline,icol)
            output.append("\\ifthenelse{\\showCor=1}{")
            output.append("\\begin{scope}[shift={(0,"+str(self.__size)+")}, yscale=-1]")
            output.append(cells.cadre().tex())
            output.append("\\end{scope}")
            output.append("}{ }")
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

