from typing import List, Tuple, Dict
from modules.primitives.direction import Direction

class Data:
    """
    Contient les informations de jeu
    """
    knowns:Dict[Tuple[int,int],int]
    constraints:Dict[Tuple[int,int,Direction],bool]
    __size:int
    __game_id:str

    def __init__(
        self,
        game_id:str,
        size:int,
        knowns:List[Tuple[int,int,int]],
        constraints:Dict[Tuple[int,int,Direction],bool]
    ):
        self.__game_id = game_id
        self.__size = size
        self.knowns = knowns
        self.constraints = constraints

    @property
    def height(self) -> int:
        return self.__size
    
    @property
    def width(self) -> int:
        return self.__size
    
    @property
    def game_id(self) -> str:
        return self.__game_id
    
    @property
    def size(self) -> int:
        return self.__size

