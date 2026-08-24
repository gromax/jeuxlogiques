# exemple :
# 6:eAcBbBaNcNBbBdN
# pas un tatham, mais créé par moi pour le site fr.puzzle-nurikabe.com

from typing import Tuple, Dict

class TathamNurikabeDecoder:
    __game_id:str
    __size:int
    __content:Dict[Tuple[int,int], int]

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu nurikabe
        """
        self.__game_id = game_id
        sizeStr, contentStr = game_id.split(':')
        self.__size = int(sizeStr)

        self.__content = {}
        index = 0
        for car in contentStr:
            if ord("A") <= ord(car) <= ord("Z"):
                self.__content[(index//self.__size, index%self.__size)] = ord(car) - ord('A') + 1
                index += 1
            else:
                index += ord(car) - ord('a') + 1

    @property
    def size(self) -> int:
        return self.__size

    @property
    def game_id(self) -> str:
        return self.__game_id
    
    @property
    def content(self) -> Dict[Tuple[int, int], int]:
        return self.__content.copy()
