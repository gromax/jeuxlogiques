from typing import List, Union
from modules.tathamdecoder.bridges import decoder
from modules.tex.misc import list_to_showList
from modules.container.bridges import Data
from modules.solvers.bridges import Solver

class Bridges:
    """
    Grille de jeu pour bridges
    """
    __data:Data
    __sol:Union[List[int], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seulement avec tatham
        assert "tatham" in options
        self.__data = decoder(options["tatham"])
        solver = Solver(self.__data)
        self.__sol = solver.solve()

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        w = self.__data.width
        h = self.__data.height
        output = [
            "% "+self.__data.game_id,
            "\\begin{tikzpicture}[scale=1]",
            "%\\begin{scope}[shift={(0.5,0.5)}]",
            f"%\\draw[line width=0.5pt] (0,0) grid[step=1] ({w-1},{h-1});",
            "%\\end{scope}"
        ]
        islands = self.__data.islands_as_dict()

        # affichage des connexion possibles
        connexions = self.__data.connexions
        str_connexions = ",".join(f"{i1}/{j1}/{i2}/{j2}" for i1,j1,i2,j2 in connexions)
        output += [
            "\\begin{scope}[shift={(0.5,{"+ str(self.__data.height - 0.5) + "})}, yscale=-1]",
            "\\foreach \\a/\\b/\\c/\\d in {" + str_connexions + "} {",
            "\\draw[line width=8pt, black!20!white] (\\b,\\a) -- (\\d,\\c);",
            "}",
            "\\end{scope}"
        ]
        # affichage de la correction
        if self.__sol is not None:
            list_str = ",".join([f"{index1//w}/{index1%w}/{index2//w}/{index2%w}/{v}" for (index1,index2),v in self.__sol.items() if v > 0])
            output += [
                "\\ifthenelse{\\showCor = 1}{",
                "\\begin{scope}[shift={(0.5,{"+ str(self.__data.height - 0.5) + "})}, yscale=-1]",
                "\\foreach \\a/\\b/\\c/\\d/\\v in {" + list_str + "} {",
                "\\foreach \\k in {1, ..., \\v}{",
                "\\ifthenelse{\\a = \\c}{",
                "\\draw[line width=2pt, yshift= {(\\k - \\v/2 - 0.5)*4pt}] (\\b,\\a) -- (\\d,\\c);",
                "}{",
                "\\draw[line width=2pt, xshift= {(\\k - \\v/2 - 0.5)*4pt}] (\\b,\\a) -- (\\d,\\c);",
                "}",
                "} }",
                "\\end{scope}",
                "}{ }"
            ]
        output += list_to_showList(
            w,
            h,
            {(i,j):True for (i,j) in islands},
            symbol = lambda it:"B" if it else '',
            macroname = "showCircleList",
            size=0.4
        )
        output += list_to_showList(
            w,
            h,
            islands,
            size=0.8
        )
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

