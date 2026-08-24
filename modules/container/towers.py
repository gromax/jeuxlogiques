from typing import List, Tuple, Dict

class Data:
    """
    Contient les informations de jeu
    """
    __knowns:Dict[Tuple[int,int],int]
    __clues:Tuple[int]
    __size:int

    def __init__(
        self,
        size:int,
        clues:List[int],
        knowns:Dict[Tuple[int,int],int]
    ):
        self.__size = size
        self.__knowns = knowns
        self.__clues = tuple(clues)

    @property
    def height(self) -> int:
        return self.__size
    
    @property
    def width(self) -> int:
        return self.__size

    @property
    def size(self) -> int:
        return self.__size

    @property
    def game_id(self) -> str:
        # Forme :
        # size:[borders séparés de /][,cases connues]
        # ex: 5:///4//3//2//3/4/////////2,2k2l
        str_clues = [str(item) if item > 0 else "" for item in self.__clues]
        return f"{self.__size}:{'/'.join(str_clues)}{self.__game_id_knowns()}"

    def __game_id_knowns(self) -> str:
        if len(self.__knowns) == 0:
            return ""
        ijs = sorted(self.__knowns)
        current_index = 0
        cars = []
        for (i,j) in ijs:
            index = i*self.__size + j
            while index > current_index:
                d = min(26, index - current_index)
                letter = chr(ord('a') + d - 1)
                current_index += d
                cars.append(letter)
            value = self.__knowns[i,j]
            cars.append(str(value))
            current_index += 1
        N = self.__size**2
        while current_index < N:
            d = min(26, N - current_index)
            letter = chr(ord('a') + d - 1)
            current_index += d
            cars.append(letter)
        return "," + "".join(cars)

    @property
    def top(self) -> Tuple[int]:
        return self.__clues[:self.__size]
    
    @property
    def bottom(self) -> Tuple[int]:
        return self.__clues[self.__size:2*self.__size]

    @property
    def left(self) -> Tuple[int]:
        return self.__clues[2*self.__size:3*self.__size]

    @property
    def right(self) -> Tuple[int]:
        return self.__clues[3*self.__size:]

    @property
    def knowns(self) -> Dict[Tuple[int,int], int]:
        return self.__knowns
    
    @property
    def clues(self) -> Tuple[int]:
        return self.__clues