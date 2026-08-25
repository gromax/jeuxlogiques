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

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu loopy de simon tatham
        exemple, uniquement pour les carrés : 7x7t0:a22d3c1b3022a3c3a2b02b2b1b31a1d2b
        """
        sizeStr, contentStr = game_id.split(':')
        wStr, hStr = sizeStr.split("x")
        width = int(wStr)
        assert hStr.endswith("t0"), "game_id incorrect"
        height = int(hStr[:-2]) # supprime le "t0"
        clues = {}
        i = 0
        for car in contentStr:
            if car in "01234":
                # c'est un digit à placer
                c = int(car)
                iline = i // width
                icol = i % width
                clues[iline, icol] = c
                i += 1
                continue
            delta = ord(car) - ord('a') + 1
            i += delta
        return Data(width, height, clues)


