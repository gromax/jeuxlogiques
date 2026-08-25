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
        # ex : 5x5n5:aBzzcV...
        cluesStr = []
        lastIndex = -1
        for iLine, iCol in self.__clues:
            clue = self.__clues[iLine, iCol]
            assert 0 < clue < 27
            clueLetter = chr(ord('A') + clue - 1)
            index = iLine*self.__width + iCol
            cluesStr.append(self.__value_to_letter(index-lastIndex-1))
            cluesStr.append(clueLetter)
            lastIndex = index
        dlast = self.__width * self.__height - lastIndex - 1
        cluesStr.append(self.__value_to_letter(dlast))
        return f"{self.__width}x{self.__height}:{''.join(cluesStr)}"

    def __value_to_letter(self, value:int) -> str:
        assert value >= 0
        if value == 0:
            return ""
        if value % 26 == 0:
            return "z"*(value//26)
        return "z"*(value//26) + chr(ord('a') + value%26 - 1)

    @property
    def clues(self) -> Dict[Tuple[int, int], int]:
        return self.__clues.copy()

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        renvoie un objet Data à partir d'un code
        """
        sizeStr, cluesStr = game_id.split(":")
        wStr,hStr = sizeStr.split("x")
        width = int(wStr)
        height = int(hStr)
        index = 0
        clues = {}
        for letter in cluesStr:
            if ord("A") <= ord(letter) <= ord("Z"):
                clues[index//width, index%width] = ord(letter) - ord("A") + 1
                index += 1
            elif ord("a") <= ord(letter) <= ord("z"):
                index += ord(letter) - ord("a") + 1
            else:
                raise ValueError(f"{letter}: symbole inconnu")
        return Data(width, height, clues)
