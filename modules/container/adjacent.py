from typing import List, Tuple, Dict
from modules.primitives.direction import Direction

class Data:
    """
    Contient les informations de jeu
    """
    knowns:Dict[Tuple[int,int],int]
    constraints:Dict[Tuple[int,int,Direction],bool]
    __size:int
    __game_id:str

    def __init__(
        self,
        game_id:str,
        size:int,
        knowns:List[Tuple[int,int,int]],
        constraints:Dict[Tuple[int,int,Direction],bool]
    ):
        self.__game_id = game_id
        self.__size = size
        self.knowns = knowns
        self.constraints = constraints

    @property
    def height(self) -> int:
        return self.__size
    
    @property
    def width(self) -> int:
        return self.__size
    
    @property
    def game_id(self) -> str:
        return self.__game_id
    
    @property
    def size(self) -> int:
        return self.__size

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu loopy de simon tatham
        """
        constraints = {}
        knowns = {}

        sizeStr, valuesStr = game_id.split('a:')
        size = int(sizeStr)
        valuesStrList = valuesStr.split(',')[:size**2]

        # toutes les contraintes mises à False
        for iline in range(size):
            for icol in range(size):
                for d in Direction:
                    constraints[iline, icol, d] = False

        for i, tag in enumerate(valuesStrList):
            iline = i//size
            icol = i%size
            symbols = tag[1:]
            for d in symbols:
                constraints[iline,icol,Direction(d)] = True
            k = int(tag[0])
            if k != 0:
                knowns[iline,icol] = k
        
        return Data(game_id, size, knowns, constraints)
