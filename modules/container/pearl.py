from typing import Tuple, List, Dict

class Data:
    __width:int
    __height:int
    __clues:Dict[Tuple[int, int], bool]

    def __init__(
            self,
            width:int,
            height:int,
            clues:Dict[Tuple[int, int], bool]
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
        """
        produit un id à la tatham : wxh:cBaNN...
        """
        gid = f"{self.__width}x{self.__height}:"
        keys = sorted(self.__clues.keys())
        index = 0
        for i,j in keys:
            new_index = i*self.__width+j
            delta = new_index - index
            if delta > 0:
                gid += chr(ord('a')+delta-1)
            index = new_index
            gid += "B" if self.__clues[(i,j)] is True else "W"
            index += 1
        return gid
    
    @property
    def clues(self) -> Dict[Tuple[int, int], int]:
        return self.__clues.copy()

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu pearl de simon tatham
        exemple : 12x8:nBaWcWWWeWWBeWWWfBfWWbWaBcWBWcWaBmBbBWaBWWc
        """
        sizeStr, contentStr = game_id.split(':')
        wStr, hStr = sizeStr.split("x")
        width = int(wStr)
        height = int(hStr)
        clues = {}
        index = 0
        for car in contentStr:
            if car in "BW":
                clues[(index//width, index%width)] = (car == "B")
                index += 1
            else:
                index += ord(car) - ord('a') + 1
        return Data(width, height, clues)

