# exemple :
# 11x11:d1d11a1a2b2123a11a3a231a21d3c23a211b1b32a133a1a123a3e1a223d312f131a1c132b1c2a11d233a1b23a3a3a2b1d1d11a

from typing import List, Tuple, Dict

class TathamSlantDecoder:
    __game_id:str
    __width:int
    __height:int
    __constraints:Dict[Tuple[int,int], int]

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu keen de simon tatham
        """
        self.__game_id = game_id
        
        sizeStr, contentStr = game_id.split(':')
        wStr, hStr = sizeStr.split('x')
        self.__width = int(wStr)
        self.__height = int(hStr)

        self.__constraints = {}
        index = 0
        W = self.__width + 1 # indices sur les lignes donc une colonne de plus
        for car in contentStr:
            if car in "01234":
                self.__constraints[index//W, index%W] = int(car)
                index += 1
            else:
                index += ord(car) - ord('a') + 1

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def game_id(self) -> str:
        return self.__game_id
    
    @property
    def constraints(self) -> Dict[Tuple[int,int], int]:
        return self.__constraints.copy()

