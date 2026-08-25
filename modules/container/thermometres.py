from typing import Tuple, List
import re

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

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        dims, thermos_str, clues_str = game_id.split(":")
        if "x" in dims:
            wStr, hStr = dims.split("x")
            width = int(wStr)
            height = int(hStr)
        else:
            width = int(dims)
            height = width
        pattern = r'([0-9]*)>((?:[UDLR][a-z]*)+)'
        brut_content = [(int(start), path) for start, path in re.findall(pattern, thermos_str)]
        thermos = []
        for start, path in brut_content:
            i, j = start//width, start%width
            didjs = Direction.str_to_path(path)
            t = [(i,j)]
            for di, dj in didjs:
                dir = Direction.step_to_dir(di,dj)
                diStep, djStep = dir.delta()
                for _ in range(abs(di)+abs(dj)):
                    i += diStep
                    j += djStep
                    t.append((i,j))
            thermos.append(t)
        clues = [int(it) for it in clues_str.split(',')]
        return Data(width, height, thermos, clues)