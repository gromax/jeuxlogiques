# exemple :
# 6x6:_ada_a_a_a_a3c_2da_a_a2ba_a_ba,a2a315a5d1h5

from typing import List, Tuple, Dict
from modules.primitives.zones import Zones
from modules.primitives.cellgroup import CellGroup

class TathamTechtonicDecoder:
    __game_id:str
    __width:int
    __height:int
    __zones:List[CellGroup]
    __numbers:Dict[Tuple[int,int], int]

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu keen de simon tatham
        """
        self.__game_id = game_id
        sizeStr, contentStr = game_id.split(':')
        if 'x' not in sizeStr:
            self.__width = int(sizeStr)
            self.__height = self.__width
        else:
            wStr, hStr = sizeStr.split('x')
            self.__width = int(wStr)
            self.__height = int(hStr)
        zonesStr, numbersStr = contentStr.split(',')
        z = Zones.makeFromStr(sizeStr + ":" + zonesStr)
        _, _, self.__zones = z.zones()
        self.__numbers = {}
        index = 0
        for car in numbersStr:
            if car in "123456789":
                i = index//self.__width
                j = index%self.__width
                self.__numbers[i,j] = int(car)
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
    def numbers(self) -> Dict[Tuple[int,int], int]:
        return self.__numbers.copy()
    
    @property
    def zones(self) -> List[CellGroup]:
        return self.__zones.copy()
