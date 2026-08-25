from typing import List, Tuple, Union
from modules.tathamdecoder.unequal import TathamUnequalDecoder
from modules.solvers.unequal import Solver
from modules.primitives.direction import Direction

class Unequal:
    """
    Grille de jeu pour unequal
    """
    __knowns:List[Tuple[int,int,int]]
    __constraints:List[Tuple[int,int,Direction]]
    __size:int
    __sol:Union[List[List[int]], False]
    __game_id:str

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # je suppose que c'est du tatham
        assert "tatham" in options
        tud = TathamUnequalDecoder(options["tatham"])
        self.__game_id = f"tatham id = {options["tatham"]}"
        self.__size = tud.size
        self.__knowns = tud.knowns
        self.__constraints = tud.constraints
        solver = Solver(self.__size, self.__constraints, self.__knowns)
        self.__sol = solver.solve()

    def __ineq_symbol(self, constraint:Tuple[int,int,Direction]) -> str:
        iline,icol,d = constraint
        return f"{icol}/{iline}/{d.tex_angle()}"

    def __ineq_symbols(self) -> str:
        return ", ".join(self.__ineq_symbol(c) for c in self.__constraints)

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        output = ["%id: "+self.__game_id]
        output.append("\\begin{tikzpicture}[scale=1.5]")
        output.append("\\inequalGrid{"+str(self.__size)+"}")
        output.append("\\begin{scope}[shift={(0.5,"+str(self.__size-0.5)+")}, yscale=-1]")
        output.append("  \\foreach \\x/\\y/\\r in {" + self.__ineq_symbols() + "} {")
        output.append("    \\begin{scope}[shift={(\\x,\\y)}, rotate=\\r] \\draw[line width=2pt] (.4,-.2) --++ (.2,.2) --++ (-.2,.2);\\end{scope}")
        output.append("  }")
        if len(self.__knowns)>0:
            knowns = "{" + ", ".join([f"{icol}/{iline}/{k}" for iline, icol, k in self.__knowns]) + "}"
            output.append("\\foreach \\x/\\y/\\k in "+knowns+" \\draw (\\x,\\y) node[scale=1.5]{\\k};")
        output.append("\\end{scope}")
        if self.__sol is not False:
            tags = list(map(str, sum(self.__sol, [])))
            texTags = ",\n".join([",".join(tags[i:i+self.__size]) for i in range(0, self.__size**2, self.__size)])
            output.append("\\ifthenelse{\\showCor = 1}{")
            output.append("\\showList{"+str(self.__size)+"}{"+str(self.__size)+"}{ {")
            output.append(texTags)
            output.append("} }{1.5}")
            output.append("}{ }")

        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

