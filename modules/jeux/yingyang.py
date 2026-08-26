from typing import Tuple, List, Union, Dict
from modules.htmldecoder.yingyang import decode_html
from modules.container.yingyang import Data
from modules.solvers.yingyang import Solver
from modules.tex.misc import list_to_showList

class Yingyang:
    __data:Data
    __sol:Union[Dict[Tuple[int,int], bool], False]
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
        w = self.__data.width
        h = self.__data.height
        clues = self.__data.clues
        output = [
            "%id="+self.__game_id,
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=.5pt] (0,0) rectangle (" + str(w) + ", " + str(h) + ");",
            "\\draw[line width=.1pt] (0,0) grid[step=1] (" + str(w) + ", " + str(h) + ");"
        ]

        # solution
        if self.__sol is not False:
            output.append("\\ifthenelse{\\showCor = 1}{")
            hconns, vconns = self.__con()
            output.append("\\connectListH{"+str(w)+"}{"+str(h)+"}{ {"+",".join(hconns)+"} }")
            output.append("\\connectListV{"+str(w)+"}{"+str(h)+"}{ {"+",".join(vconns)+"} }")
            output += list_to_showList(
                w,
                h,
                self.__sol,
                cor = False,
                default = ' ',
                macroname = "showCircleList",
                symbol = lambda v: 'B' if v is True else 'N',
                addDims = [0.3]
            )
            output.append("}{ }")

        # problème
        output += list_to_showList(
            w,
            h,
            clues,
            cor = False,
            default = ' ',
            macroname = "showCircleList",
            symbol = lambda v: 'B' if v is True else 'N',
            addDims = [0.4]
        )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

    def __con(self) -> Tuple[List[str],List[str]]:
        if self.__sol is False:
            return [], []
        hconns = []
        vconns = []
        for i in range(self.__height):
            for j in range(self.__width):
                c = 0
                if i<self.__height-1 and self.__sol[i+1,j] == self.__sol[i,j]:
                    c += 1
                if i>0 and self.__sol[i-1,j] == self.__sol[i,j]:
                    c += 2
                vconns.append(str(c))
                c = 0
                if j<self.__width-1 and self.__sol[i,j+1] == self.__sol[i,j]:
                    c += 1
                if j>0 and self.__sol[i,j-1] == self.__sol[i,j]:
                    c += 2
                hconns.append(str(c))
        return hconns, vconns
