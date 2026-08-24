from typing import List, Union, Dict, Tuple
from modules.htmldecoder.thermometres import HtmlDecoder
from modules.tathamdecoder.thermometres import decoder
from modules.container.thermometres import Data
from modules.solvers.thermometres import Solver
from modules.tex.misc import sideItems, list_to_showList

class Thermometres:
    """
    Grille de jeu pour unequal
    """
    __data:Data
    __sol:Union[List[bool], False]

    def __init__(self, **options):
        assert set(options) <= {"url", "html","tatham"}, "options incorrectes"
        # pour l'instant seulement avec internet
        if "url" in options:
            self.__data = HtmlDecoder(options["url"]).data
        elif "html" in options:
            self.__data = HtmlDecoder.decode(options["html"])
        elif "tatham" in options:
            self.__data = decoder(options["tatham"])
        else:
            raise ValueError("Aucun paramètre valide")
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        H = self.__data.height
        W = self.__data.width

        output = [
            f"%id={self.__data.game_id}",
            "\\begin{tikzpicture}[scale=1.2]",
        ]
        output += sideItems(
            W,
            H,
            self.__data.top,
            self.__data.right,
            [],
            [],
            size = 1.5,
        )

        if self.__sol is not False:
            output += list_to_showList(
                W,
                H,
                self.__sol,
                cor = True,
                macroname = "showColorList",
                symbol = lambda item:'r' if item else ''
            )

        output += list_to_showList(
            W,
            H,
            self.__thermo_grid(),
            macroname = "showListThermo",
        )

        output += [
            "\\draw[line width=1pt] (0,0) rectangle (" + str(W) + "," + str(H) +");",
            "\\draw[line width=0.5pt] (0,0) grid[step=1] (" + str(W) + "," + str(H) + ");",
        ]

        output.append("\\end{tikzpicture}")
        return "%\n".join(output)
    
    def __thermo_grid(self) -> Dict[Tuple[int,int], str]:
        out = {}
        cas = {
            ( 0, 0,-1, 0):"S/0",
            ( 0, 0, 1, 0):"S/180",
            ( 0, 0, 0, 1):"S/-90",
            ( 0, 0, 0,-1):"S/90",
            ( 1, 0, 0, 0):"E/0",
            (-1, 0, 0, 0):"E/180",
            ( 0, 1, 0, 0):"E/90",
            ( 0,-1, 0, 0):"E/-90",
            ( 0,-1, 0,-1):"D/90",
            ( 0, 1, 0, 1):"D/90",
            ( 1, 0, 1, 0):"D/0",
            (-1, 0,-1, 0):"D/0",
            ( 1, 0, 0, 1):"C/0",
            ( 0,-1,-1, 0):"C/0",
            ( 0, 1,-1, 0):"C/90",
            ( 1, 0, 0,-1):"C/90",
            (-1, 0, 0,-1):"C/180",
            ( 0, 1, 1, 0):"C/180",
            (-1, 0, 0, 1):"C/-90",
            ( 0,-1, 1, 0):"C/-90",
        }
        for thermo in self.__data.thermometres:
            assert len(thermo) >= 2
            for index in range(len(thermo)):
                i_current, j_current = thermo[index]
                i_prev, j_prev = thermo[index-1] if index > 0 else (i_current,j_current)
                i_next, j_next = thermo[index + 1] if index < len(thermo) - 1 else (i_current,j_current)
                di_prev, dj_prev = (i_current-i_prev, j_current-j_prev)
                di_next, dj_next = (i_next-i_current, j_next-j_current)
                symbol = cas.get((di_prev,dj_prev,di_next,dj_next),'')
                out[i_current,j_current] = symbol
        return out