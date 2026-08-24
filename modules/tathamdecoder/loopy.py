from typing import Dict, Tuple

from modules.primitives.direction import Direction

class TathamLoopyDecoder:
    __game_id:str
    __constraints:Dict[Tuple[int,int],int]
    __size:int

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu loopy de simon tatham
        """
        self.__game_id = game_id

        sizeStr, contentStr = game_id.split(':')
        self.__size = int(sizeStr.split("x")[0]) # assume que ce sera un carré
        self.__constraints = {}

        if contentStr == "":
            return
        i = 0
        for car in contentStr:
            if car in "01234":
                # c'est un digit à placer
                c = int(car)
                iline = i // self.__size
                icol = i % self.__size
                self.__constraints[iline, icol] = c
                i += 1
                continue
            delta = ord(car) - ord('a') + 1
            i += delta

    @property
    def size(self) -> int:
        return self.__size

    @property
    def constraints(self) -> Dict[Tuple[int,int],int]:
        return self.__constraints.copy()

    @property
    def game_id(self) -> str:
        return self.__game_id
