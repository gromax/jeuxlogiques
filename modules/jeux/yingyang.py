from typing import Tuple, List, Union, Dict
from modules.htmldecoder.yingyang import YingyangHtmlDecoder
from modules.tathamdecoder.yingyang import TathamYingYangDecoder
from modules.solvers.yingyang import YingyangSolver
from modules.tex.misc import list_to_showList

class Yingyang:
    __content:Dict[Tuple[int,int], bool]
    __size:int
    __sol:Union[Dict[Tuple[int,int], bool], False]
    __game_id:str

    def __init__(self, **options):
        assert set(options) <= {"url", "tatham"}, "options incorrectes"
        # pour l'instant seulement avec url
        assert "url" in options or "tatham" in options, "option url ou tatham obligatoire"
        if "url" in options:
            yd = YingyangHtmlDecoder(options["url"])
            self.__content = yd.content
            self.__size = yd.size
            self.__game_id = yd.game_id
        else:
            yd = TathamYingYangDecoder(options["tatham"])
            self.__content = yd.content
            self.__size = yd.size
            self.__game_id = yd.game_id
        yingyanngSolver = YingyangSolver(self.__size, self.__content)
        self.__sol = yingyanngSolver.solve()

    def tex(self):
        output = [
            "%id = "+self.__game_id,
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=.5pt] (0,0) rectangle (" + str(self.__size) + ", " + str(self.__size) + ");",
            "\\draw[line width=.1pt] (0,0) grid[step=1] (" + str(self.__size) + ", " + str(self.__size) + ");"
        ]

        # solution
        if self.__sol is not False:
            output.append("\\ifthenelse{\\showCor = 1}{")
            hconns, vconns = self.__con()
            output.append("\\connectListH{"+str(self.__size)+"}{ {"+",".join(hconns)+"} }")
            output.append("\\connectListV{"+str(self.__size)+"}{ {"+",".join(vconns)+"} }")
            output += list_to_showList(
                self.__size,
                self.__size,
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
            self.__size,
            self.__size,
            self.__content,
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
        for i in range(self.__size):
            for j in range(self.__size):
                c = 0
                if i<self.__size-1 and self.__sol[i+1,j] == self.__sol[i,j]:
                    c += 1
                if i>0 and self.__sol[i-1,j] == self.__sol[i,j]:
                    c += 2
                vconns.append(str(c))
                c = 0
                if j<self.__size-1 and self.__sol[i,j+1] == self.__sol[i,j]:
                    c += 1
                if j>0 and self.__sol[i,j-1] == self.__sol[i,j]:
                    c += 2
                hconns.append(str(c))
        return hconns, vconns
