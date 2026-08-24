from typing import List, Tuple, Union
from modules.tathamdecoder.camping import decoder
from modules.container.camping import Data
from modules.solvers.camping import Solver
from modules.tex.misc import list_to_showList

class Camping:
    __data:Data
    __sol:Union[Tuple[List[bool], List[int]], False]

    def __init__(self, **options):
        assert set(options) <= {"tatham"}, "options incorrectes"
        # pour l'instant seule possibilité : tatham
        assert "tatham" in options
        self.__data = decoder(options["tatham"])
        s = Solver(self.__data)
        self.__sol = s.solve()

    def tex(self) -> str:
        """
        Retourne le code LaTeX pour générer le jeu
        """
        w = self.__data.width
        h = self.__data.height
        output = ["%id: "+self.__data.game_id]
        output.append("\\begin{tikzpicture}[scale=.7]")
        output.append("\\draw[line width=0.5pt] (0,0) grid[step=1] ("+str(w)+","+str(h)+");")
        output += self.__trees_tex()
        strTop = "{" + ",".join([str(c) for c in self.__data.top])+"}"
        strRight = "{" + ",".join([str(c) for c in self.__data.right])+"}"
        output.append("\\def\\bordsHBGD{"+strTop + ",{ },{ },"+strRight+"}")
        output.append("\\sideItems{"+str(w)+"}{"+str(h)+"}{\\bordsHBGD}{1}")
        output += self.__sol_tex()
        output.append("\\end{tikzpicture}")
        return "%\n".join(output)

    def __trees_tex(self) -> List[str]:
        w = self.__data.width
        h = self.__data.height
        posTrees = {(index//w,index%w):"B" for index in self.__data.trees}
        return list_to_showList(w, h, posTrees, {
            "size":0.2,
            "macroname":"showCircleList"
        })
    
    def __sol_tex(self) -> List[str]:
        if self.__sol is False:
            return []
        w = self.__data.width
        h = self.__data.height
        tents, ownerships = self.__sol
        output = ["\\ifthenelse{\\showCor = 1}{"]
        output+= list_to_showList(w, h, tents, {
            "size":1,
            "symbol": lambda item: "T" if item else " "
        })
        # on va séparer les possessions horizontales des possessions verticales
        hor = []
        ver = []
        for (tree, tent) in zip(self.__data.trees, ownerships):
            iTree = tree // self.__data.width
            jTree = tree % self.__data.width
            iTent = tent // self.__data.width
            jTent = tent % self.__data.width
            iRef = min(iTree, iTent)
            jRef = min(jTree, jTent)
            if iTree != iTent: # vertical
                ver.append(f"{iRef}/{jRef}")
            else:
                hor.append(f"{iRef}/{jRef}")
        horStr = ",".join(hor)
        verStr = ",".join(ver)
        output.append("\\begin{scope}[shift={(0,"+str(self.__data.height)+")}, yscale=-1]")
        if horStr != "":
            output.append("\\foreach \\y/\\x in {"+horStr+"} {\\draw[line width=1.5pt] (\\x,\\y) rectangle ++ (2,1);}" )
        if verStr != "":
            output.append("\\foreach \\y/\\x in {"+verStr+"} {\\draw[line width=1.5pt] (\\x,\\y) rectangle ++ (1,2);}" )
        output.append("\\end{scope}")
        output.append("}{ }")
        return output
