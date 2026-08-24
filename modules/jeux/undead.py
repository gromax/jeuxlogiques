from typing import Tuple, List, Union, Dict
from modules.tathamdecoder.undead import TathamUndeadDecoder
from modules.solvers.undead import UndeadSolver
from modules.tex.misc import sideItems

class Undead:
    __game_id:str
    __top:List[int]
    __right:List[int]
    __bottom:List[int]
    __left:List[int]
    __ghosts:int
    __vampires:int
    __zombies:int
    __mirrors:Dict[Tuple[int,int], bool]
    __size:int
    __sol: Union[List[List[str]], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__game_id = f"tatham id = {options['tatham']}"
        tud = TathamUndeadDecoder(options["tatham"])
        self.__top = tud.top
        self.__right = tud.right
        self.__bottom = tud.bottom
        self.__left = tud.left
        self.__ghosts = tud.ghosts
        self.__vampires = tud.vampires
        self.__zombies = tud.zombies
        self.__mirrors = tud.mirrors
        self.__size = tud.size
        s = UndeadSolver(
            self.__size,
            self.__mirrors,
            self.__ghosts,
            self.__vampires,
            self.__zombies,
            self.__top,
            self.__right,
            self.__bottom,
            self.__left
        )
        self.__sol = s.solve()

    def tex(self):
        output = [
            "%id = "+self.__game_id,
            f"{{\\Large G = {self.__ghosts} \\quad V = {self.__vampires} \\quad Z = {self.__zombies} }}",
            "\\medskip",
            "\n"
            "\\begin{tikzpicture}[scale=1]",
            "\\draw[line width=1pt] (0,0) rectangle (" + str(self.__size) + ", " + str(self.__size) + ");",
            "\\draw[line width=0.2pt] (0,0) grid[step=1] (" + str(self.__size) + ", " + str(self.__size) + ");"
        ]
        output += self.__listMirorStr()
        output += sideItems(
            self.__size,
            self.__size,
            self.__top,
            self.__right,
            self.__bottom,
            self.__left,
            size = 1.5
        )
        output += self.__sol_tex()
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

    def __listMirorStr(self) -> List[str]:
        L = ["\\undead{" + str(self.__size) + "}{ {"]
        for i in range(self.__size):
            line = []
            for j in range(self.__size):
                if (i,j) not in self.__mirrors:
                    line.append(" ")
                elif self.__mirrors[i,j]:
                    line.append("L")
                else:
                    line.append("R")
            L.append(",".join(line)+',')
        L.append("} }{ 1 }")
        return L
    
    def __sol_tex(self) -> List[str]:
        if self.__sol is False:
            return []
        L = [
            "\\ifthenelse{\\showCor = 1}{"
            "\\showList{"+ str(self.__size) +  "}{"+str(self.__size)+"}{ {"
        ]
        for line in self.__sol:
            L.append(",".join(line)+',')
        L.append("} }{ 1 }")
        L.append("}{ }")
        return L