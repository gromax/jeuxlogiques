from typing import Dict, Tuple, List
from modules.primitives.direction import Direction

class TathamUnequalDecoder:
    __game_id:str
    __constraints:List[Tuple[int,int,Direction]]
    __knowns:Dict[Tuple[int,int],int]
    __size:int

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu loopy de simon tatham
        """
        self.__game_id = game_id
        self.__constraints = []
        self.__knowns = {}

        sizeStr, valuesStr = game_id.split(':')
        self.__size = int(sizeStr)
        valuesStrList = valuesStr.split(',')[:self.__size**2]

        for i, tag in enumerate(valuesStrList):
            iline = i//self.__size
            icol = i%self.__size
            for symbol in tag[1:]:
                self.__constraints.append((iline,icol,Direction(symbol)))
            d = int(tag[0])
            if d != 0:
                self.__knowns[iline,icol] = d

    @property
    def size(self) -> int:
        return self.__size

    @property
    def constraints(self) -> List[Tuple[int,int,Direction]]:
        return self.__constraints.copy()
    
    @property
    def knowns(self) -> List[Tuple[int,int,int]]:
        return [(iline,icol,k) for (iline,icol), k in self.__knowns.items()]

    @property
    def game_id(self) -> str:
        return self.__game_id
