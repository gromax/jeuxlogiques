from typing import Tuple, List

class Data:
    __width:int
    __height:int
    __trees:Tuple[int]
    __right:Tuple[int]
    __top:Tuple[int]

    def __init__(
            self,
            width:int,
            height:int,
            trees:List[int],
            right:List[int],
            top:List[int]
        ):
        self.__width = width
        self.__height = height
        self.__trees = tuple(trees)
        self.__right = tuple(right)
        self.__top = tuple(top)

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def game_id(self) -> str:
        # construit un game_id version tatham
        # ex : 15x15:bcaececfcgbebbdbac_cn_bra__bd__eqgefddaiab_ckb,2,4,2,4,2,4,3,4,3,2,4,1,4,3,3,4,3,3,3,4,2,4,3,3,3,2,2,2,2,5
        sizeStr = f"{self.__width}x{self.height}"
        currentIndex = 0
        treesListStr = []
        for index in self.__trees:
            if index > currentIndex:
                saut = chr(ord('a') + index - currentIndex - 1)
                treesListStr.append(saut)
            else:
                treesListStr.append('_')
            currentIndex = index + 1
        dlast = self.__width * self.__height - currentIndex
        if dlast > 0:
            saut = chr(ord('a') + dlast - 1)
            treesListStr.append(saut)
        cluesList = [str(clue) for clue in self.__top] + [str(clue) for clue in self.__right]
        return sizeStr + ":" + "".join(treesListStr) + "," + ",".join(cluesList)
    
    @property
    def trees(self) -> Tuple[int]:
        return self.__trees
    
    @property
    def top(self) -> Tuple[int]:
        return self.__top
    
    @property
    def right(self) -> Tuple[int]:
        return self.__right

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu nurikabe
        """
        width:int
        height:int
        trees:List[int]
        right:List[int]
        top:List[int]

        sizeStr, contentStr = game_id.split(':')
        if "x" in sizeStr:
            wStr, hStr = sizeStr.split('x')
            width = int(wStr)
            height = int(hStr)
        else:
            width = int(sizeStr)
            height = width
        parts = contentStr.split(',')
        trees = []
        index = 0
        for car in parts[0]:
            if ord("a") <= ord(car) <= ord("z"):
                index += ord(car) - ord('a') + 1
            trees.append(index)
            index += 1
        if len(trees)>0 and trees[-1] == height*width:
            # le codage peut entraîner un arbre en trop
            trees.pop()
        clues = [int(car) for car in parts[1:]]
        top = clues[:width]
        right = clues[width:]
        return Data(width, height, trees, right, top)