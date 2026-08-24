from typing import Tuple, List
from enum import Enum
import re

class Direction(Enum):
    UP = "U"
    RIGHT = "R"
    DOWN = "D"
    LEFT = "L"

    def delta(self) -> Tuple[int,int]:
        if self == Direction.UP:
            return (-1,0)
        if self == Direction.DOWN:
            return (1,0)
        if self == Direction.LEFT:
            return (0,-1)
        return (0,1)
    
    @classmethod
    def step_to_dir(cls, di:int, dj:int) -> "Direction":
        assert di*dj == 0
        if di>0:
            return Direction.DOWN
        if di<0:
            return Direction.UP
        if dj>0:
            return Direction.RIGHT
        return Direction.LEFT


    def tex_angle(self) -> int:
        if self == Direction.UP:
            return 270
        if self == Direction.DOWN:
            return 90
        if self == Direction.LEFT:
            return 180
        return 0
    
    def rotate_right(self) -> "Direction":
        if self == Direction.UP:
            return Direction.RIGHT
        if self == Direction.RIGHT:
            return Direction.DOWN
        if self == Direction.DOWN:
            return Direction.LEFT
        return Direction.UP
    
    @property
    def label(self) -> str:
        if self == Direction.UP:
            return "up"
        if self == Direction.DOWN:
            return "down"
        if self == Direction.LEFT:
            return "left"
        return "right"
    
    def __str__(self) -> str:
        if self == Direction.UP:
            return "U"
        if self == Direction.DOWN:
            return "D"
        if self == Direction.LEFT:
            return "L"
        return "R"


    def neighbour_index(self, width:int, index:int) -> int:
        """
        renvoie l'index correspondant à la direction
        """
        i = index // width
        j = index % width
        di, dj = self.delta()
        return (i+di)*width + (j+dj)

    @classmethod
    def path_to_str(cls, coords:List[Tuple[int,int]]) -> str:
        n = len(coords)
        if n <= 1:
            return ""
        moves = []
        for index in range(1, n):
            i1,j1 = coords[index-1]
            i2,j2 = coords[index]
            di = i2 - i1
            dj = j2 - j1
            moves.append(cls.step_to_dir(di,dj))
        # compression
        counted_moves = []
        debIndex = 0
        while debIndex < len(moves):
            stopIndex = debIndex + 1
            while stopIndex < len(moves) and moves[stopIndex] == moves[debIndex]:
                stopIndex += 1
            counted_moves.append((moves[debIndex],stopIndex - debIndex))
            debIndex = stopIndex
        moves_str = []
        for dir, count in counted_moves:
            radix_26 = []
            while count > 0:
                radix_26.append(count%26)
                count //=26
            if len(radix_26) == 0:
                radix_26.append(0)
            countStr = "".join(chr(ord('a') + item) for item in radix_26[::-1])
            moves_str.append(f"{dir}{countStr if count != 1 else ""}")
        return "".join(moves_str)

    @classmethod
    def str_to_path(cls, path:str) -> List[Tuple[int,int]]:
        step_pattern = r'([UDLR])([a-z]*)'
        steps_str = re.findall(step_pattern, path)
        out =  []
        for dir_str, delta_str in steps_str:
            if dir_str == "U":
                dir = Direction.UP
            elif dir_str == "D":
                dir = Direction.DOWN
            elif dir_str == "L":
                dir = Direction.LEFT
            else:
                dir = Direction.RIGHT
            delta = 0
            for car in delta_str:
                delta *= 26
                delta += ord(car) - ord('a')
            di, dj = dir.delta()
            di *= delta
            dj *= delta
            out.append((di, dj))
        return out