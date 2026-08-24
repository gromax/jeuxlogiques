from typing import Tuple, Dict

class Data:
    """
    Contient les informations de jeu
    """
    __clues:Dict[Tuple[int,int], int]
    __width:int
    __height:int

    def __init__(
        self,
        width:int,
        height:int,
        clues:Dict[Tuple[int,int], int]
    ):
        self.__width = width
        self.__height = height
        self.__clues = clues


    @property
    def height(self) -> int:
        return self.__height
    
    @property
    def width(self) -> int:
        return self.__width

    @property
    def game_id(self) -> str:
        # Forme : WxH:séquence
        # dans la séquence, une lettre indique un nombre de cases vides, un chiffre est une case connue
        # attention : les indces étant dans le coins, c'est sur une grille de (width+1)x(height+1) cases
        clues = []
        lastIndex = -1
        W = self.__width + 1
        H = self.__height + 1
        for index in range(W*H):
            col = index % W
            row = index // W
            if (row,col) not in self.__clues:
                continue
            delta = index - lastIndex
            if delta > 1:
                letter = chr(ord('a') + delta - 2)
                clues.append(letter)
            clues.append(str(self.__clues[row,col]))
            lastIndex = index
        delta = W*H - lastIndex
        if delta > 1:
            letter = chr(ord('a') + delta - 2)
            clues.append(letter)
        return f"{self.__width}x{self.__height}:{''.join(clues)}"

    @property
    def clues(self) -> Dict[Tuple[int,int], int]:
        return self.__clues.copy()