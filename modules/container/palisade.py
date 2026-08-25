from typing import Tuple, Dict

class Data:
    __width:int
    __height:int
    __zoneSize:int
    __clues:Dict[Tuple[int, int], int]

    def __init__(
            self,
            width:int,
            height:int,
            zoneSize:int,
            clues:Dict[Tuple[int, int], int]
        ):
        self.__width = width
        self.__height = height
        self.__zoneSize = zoneSize
        self.__clues = clues.copy()

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def zoneSize(self) -> int:
        return self.__zoneSize

    @property
    def game_id(self) -> str:
        # construit un game_id version tatham
        # ex : 5x5n5:a1c2c123a2
        cluesStr = []
        lastIndex = -1
        for iLine, iCol in self.__clues:
            clue = self.__clues[iLine, iCol]
            index = iLine*self.__width + iCol
            saut = index - lastIndex - 1
            if saut > 0:
                cluesStr.append(chr(ord('a') + saut - 1))
            cluesStr.append(str(clue))
            lastIndex = index
        dlast = self.__width * self.__height - lastIndex - 1
        if dlast > 0:
            cluesStr.append(chr(ord('a') + dlast - 1))
        return f"{self.__width}x{self.__height}b{self.__zoneSize}:{''.join(cluesStr)}"
    
    @property
    def clues(self) -> Dict[Tuple[int, int], int]:
        return self.__clues.copy()

