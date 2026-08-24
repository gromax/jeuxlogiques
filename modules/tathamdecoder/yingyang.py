# exemple :
# 6:eNcBbBaNcNBbBdN
# pas un tatham, mais créé par moi pour le site fr.puzzle-yin-yang.com

from typing import Tuple, Dict
import re

class TathamYingYangDecoder:
    __game_id:str
    __size:int
    __content:Dict[Tuple[int,int], bool]

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu yingyang
        """
        self.__game_id = game_id
        sizeStr, contentStr = game_id.split(':')
        self.__size = int(sizeStr)

        # les éventuels nombres dans le content indiqueraient une répétition
        # on peut donc remplacer toutes les occurences de c### par "c"*###
        regex = r"[a-z_BN][0-9]+"
        L = re.findall(regex, contentStr)
        for item in L:
            car = item[0]
            n = int(item[1:])
            repl = car*n
            contentStr = contentStr.replace(item, repl)

        self.__content = {}
        index = 0
        for car in contentStr:
            if car in "BN":
                self.__content[(index//self.__size, index%self.__size)] = (car == "B")
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
    def content(self) -> Dict[Tuple[int, int], bool]:
        return self.__content.copy()
