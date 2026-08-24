# exemple :
# 6:a4_b_3a_11aa__a_3a_a4__aa_aa,m108s1d2d2a6d3s1a9s1m10a5d2a6s1d2m36m24

import re
from typing import List, Tuple
from modules.primitives.zones import Zones
from modules.primitives.cellgroup import CellGroup

class TathamKenkenDecoder:
    __game_id:str
    __size:int
    __zones:List[CellGroup]
    __constraints:List[Tuple[List[Tuple[int, int]], str, int]]

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu keen de simon tatham
        """
        self.__game_id = game_id
        sizeStr, contentStr = game_id.split(':')
        self.__size = int(sizeStr)
        zonesStr, opersStr = contentStr.split(',')
        z = Zones.makeFromStr(sizeStr + ":" + zonesStr)
        _, _, self.__zones = z.zones()
        self.__zones.sort(key=lambda z: z.getFirstCellCoords()) # tri ordre lexicographique
        opers = [(it[0], int(it[1:])) for it in re.findall(r"[a-z][1-9][0-9]*", opersStr)]
        self.__constraints = []
        for (z, op) in zip(self.__zones, opers):
            z.data = op
            self.__constraints.append((z.coords(), op[0], int(op[1])))

    @property
    def size(self) -> int:
        return self.__size

    @property
    def game_id(self) -> str:
        return self.__game_id
    
    @property
    def constraints(self) -> List[Tuple[List[Tuple[int, int]], str, int]]:
        return self.__constraints.copy()
    
    @property
    def zones(self) -> List[CellGroup]:
        return self.__zones.copy()
