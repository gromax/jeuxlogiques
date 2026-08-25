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

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu palisade de simon tatham
        exemple, uniquement pour les carrés : 10x8n8:a22d3c1b3022a3c3a2b02b2b1b31a1d2b
        """
        gridStr, contentStr = game_id.split(':')
        sizeStr,nStr = gridStr.split("n")
        wStr, hStr = sizeStr.split("x")
        width = int(wStr)
        height = int(hStr)
        zoneSize = int(nStr)
        assert (width*height)%zoneSize == 0, "la taille de zone doit diviser la taille de la grille"
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
        return Data(width, height, zoneSize, clues)