from typing import Tuple, List
from modules.primitives.direction import Direction

class Data:
    __width:int
    __height:int
    __thermometres:Tuple[Tuple[Tuple[int,int]]]
    __clues:Tuple[int]

    def __init__(
            self,
            width:int,
            height:int,
            thermometres:List[List[Tuple[int,int]]],
            clues:List[int],
        ):
        self.__width = width
        self.__height = height
        self.__thermometres = tuple([tuple(item) for item in thermometres])
        self.__clues = tuple(clues)

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def game_id(self) -> str:
        thermos_str = []
        for t in self.__thermometres:
            iStart, jStart = t[0]
            thermos_str.append(f"{iStart*self.__width+jStart}>{Direction.path_to_str(t)}")
        if self.__height == self.__width:
            dims = str(self.__width)
        else:
            dims = f"{self.__width}x{self.__height}"
        return f"{dims}:{"".join(thermos_str)}:{",".join(str(it) for it in self.__clues)}"
    
    @property
    def thermometres(self) -> Tuple[Tuple[int]]:
        return self.__thermometres
    
    @property
    def top(self) -> Tuple[int]:
        return self.__clues[:self.__width]
    
    @property
    def right(self) -> Tuple[int]:
        return self.__clues[self.__width:]
