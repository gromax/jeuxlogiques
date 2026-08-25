from typing import Tuple, List

class Data:
    __height:int
    __width:int
    __stars:Tuple[Tuple[int,int]]

    def __init__(
            self,
            width:int,
            height:int,
            stars:List[Tuple[int,int]]
        ):
        self.__width = width
        self.__height = height
        self.__stars = tuple(stars)

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def game_id(self) -> str:
        # construit un game_id version tatham
        # ex : 7x7:akisdznfrqtkh
        S = 2*self.__width - 1
        # les coordonnées sont doublées pour conserver des entiers
        lastIndex = -1
        letters = []
        for (col, row) in self.__stars:
            index = col*S + row
            saut = index - lastIndex - 1
            assert saut > 0, "étoiles trop proches"
            nzs = max(saut // 25 - 1, 0)
            iletter = saut - nzs*25
            letters.append("z"*nzs + chr(ord('a') + iletter - 1))
        return f"{self.__width}x{self.__height}:{''.join(letters)}"
    
    @property
    def stars(self) -> Tuple[Tuple[int,int]]:
        return self.__stars
    
