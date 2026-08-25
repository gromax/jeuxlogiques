from typing import Tuple, List, Dict

class Data:
    __width:int
    __height:int
    __clues:Dict[Tuple[int, int], int]

    def __init__(
            self,
            width:int,
            height:int,
            clues:Dict[Tuple[int, int], int]
        ):
        self.__width = width
        self.__height = height
        self.__clues = clues.copy()

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def game_id(self) -> str:
        # construit un game_id version tatham
        # ex : 7x7t0:a22d3c1b3022a3c3a2b02b2b1b31a1d2b
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
        return f"{self.__width}x{self.__height}t0:{''.join(cluesStr)}"
    
    @property
    def clues(self) -> Dict[Tuple[int, int], int]:
        return self.__clues.copy()

