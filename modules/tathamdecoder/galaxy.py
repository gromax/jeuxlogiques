from typing import List, Tuple


class TathamGalaxyDecoder:
    __game_id:str
    __stars:List[Tuple[int,int]]
    __height:int
    __width:int

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu loopy de simon tatham
        ex: 7x7t0:a22d3c1b3022a3c3a2b02b2b1b31a1d2b
        """
        sizeStr, contentStr = game_id.split(':')
        self.__height, self.__width = map(int, sizeStr.split("x"))
        self.__game_id = game_id

        values = [ord(letter) - ord('a') + 1 for letter in contentStr]
        t = -1
        S = 2*self.__width - 1
        self.__stars = [] # les coords sont doublées pour conserver des entiers
        for v in values:
            t += v
            if v == 26:
                # un z sert à faire un saut plus grand
                # exemple zc pour 28
                t -= 1
                continue
            self.__stars.append((t//S, t%S))

    @property
    def height(self) -> int:
        return self.__height

    @property
    def width(self) -> int:
        return self.__width

    @property
    def stars(self) -> List[Tuple[int,int]]:
        return self.__stars.copy()
    
    @property
    def game_id(self) -> str:
        return self.__game_id
