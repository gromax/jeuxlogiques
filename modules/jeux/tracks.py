from typing import List, Tuple, Union
from modules.container.tracks import Data
from modules.solvers.tracks import Solver
from modules.tex.misc import sideItems, list_command_raw

class Game:
    __data:Data
    __sol:Union[Tuple[List[bool], List[int]], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seule possibilité : tatham
        assert "tatham" in options
        self.__data = Data.decode(options["tatham"])
        s = Solver(self.__data)
        self.__sol = s.solve()

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        w = self.__data.width
        h = self.__data.height
        output = ["%id="+self.__data.game_id]
        output.append("\\begin{tikzpicture}[scale=.7]")
        output.append("\\draw[line width=0.5pt] (0,0) grid[step=1] ("+str(w)+","+str(h)+");")

        # valeurs sur les bords
        output += sideItems(
            w,
            h,
            self.__data.top,
            self.__data.right,
            self.__data.bottom,
            self.__data.left,
            symbol = lambda item:str(item) if item != -1 else "",
            size=1
        )

        # solution
        if self.__sol is not False:
            path = " -- ".join(f"({j},{i})" for (i,j) in self.__sol) + ";"
            output.append("\\ifthenelse{\\showCor = 1}{")
            output.append("\\begin{scope}[shift={(0.5,"+str(h-0.5)+")}, yscale=-1]")
            output.append("\\clip (-.5,-.5) rectangle ("+str(w-.5)+","+str(h-.5)+");")
            output.append("\\draw[line width=8pt, black!50] "+path)
            output.append("\\end{scope}")
            output.append("}{ }")

        # rails donnés
        def symb(pos,item):
            i,j = pos
            d1, d2 = item
            y,x = d1.delta()
            t,z = d2.delta()
            return f"{x/2+j}/{y/2+i}/{(z-x)/2}/{(t-y)/2}"
        output += list_command_raw(
            w,
            h,
            [symb(pos,item) for pos,item in self.__data.rails.items()],
            varname = "\\x/\\y/\\z/\\t",
            commands = ["\\draw[line width=8pt, black] (\\x,\\y) -| ++(\\z,\\t);"]
        )

        output.append("\\end{tikzpicture}")
        return "%\n".join(output)