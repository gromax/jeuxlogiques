from typing import Tuple, List, Dict
import re
class Data:
    __width:int
    __height:int
    __islands:Tuple[Tuple[int,int]]
    __max_bridges:int
    __cons:Tuple[Tuple[int,int,int,int]]

    def __init__(
            self,
            width:int,
            height:int,
            islands:List[int],
            max_bridges:int
        ):
        self.__width = width
        self.__height = height
        self.__islands = tuple(islands)
        self.__max_bridges = max_bridges
        self.__make_connexions()

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def game_id(self) -> str:
        # construit un game_id version tatham
        # ex : 7x7m2:a3d31h3c42b2a3b2e3a6b3b2d3
        currentIndex = 0
        chaine = ""
        for index, value in self.__islands:
            delta = index - currentIndex
            while delta > 26:
                chaine += "z"
                currentIndex += 26
                delta -= 26
            if delta > 0:
                chaine += chr(ord("a") + delta - 1)
            if value < 10:
                chaine += str(value)
            else:
                chaine += chr(ord('A')  + value - 10)
            currentIndex = index + 1
        S = self.__width * self.__height
        while S - currentIndex > 26:
            chaine += "z"
            currentIndex += 26
        if S - currentIndex > 0:
            chaine += chr(ord("a") + S - currentIndex - 1)
        return f"{self.__width}x{self.height}m{self.__max_bridges}:{chaine}"
    
    @property
    def islands(self) -> Tuple[Tuple[int,int]]:
        return self.__islands
    
    def islands_as_dict(self) -> Dict[Tuple[int,int], int]:
        out = {}
        for index, value in self.__islands:
            i = index // self.__width
            j = index % self.__width
            out[i,j] = value
        return out
    
    @property
    def max_bridges(self) -> int:
        return self.__max_bridges
    
    def __make_connexions(self):
        """
        renvoie la liste des coordonnées connectées (i1,j1) -> (i2,j2)
        en un seul exemplaire
        """
        islands = self.islands_as_dict()
        pos_per_lines = sorted(islands.keys()) 
        pos_per_columns = sorted(islands.keys(), key = lambda it:(it[1],it[0])) 

        cons = []
        for index,(i1,j1) in enumerate(pos_per_lines[:-1]):
            (i2,j2) = pos_per_lines[index+1]
            if i1 == i2:
                cons.append((i1,j1,i2,j2))
        for index,(i1,j1) in enumerate(pos_per_columns[:-1]):
            (i2,j2) = pos_per_columns[index+1]
            if j1 == j2:
                cons.append((i1,j1,i2,j2))
        self.__cons = tuple(cons)

    def neighborhood(self) -> Dict[Tuple[int,int],List[Tuple[int,int]]]:
        n = {(index//self.__width,index%self.__width):[] for index, _ in self.__islands}
        for i1,j1,i2,j2 in self.__cons:
            n[i1,j1].append((i2,j2))
            n[i2,j2].append((i1,j1))
        return n

    @property
    def connexions(self) -> Tuple[Tuple[int,int,int,int]]:
        return self.__cons
    
    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu loopy de simon tatham
        ex: 7x7m2:a3d31h3c42b2a3b2e3a6b3b2d3
        """
        pattern = r'^(?P<w>[1-9][0-9]*)x(?P<h>[1-9][0-9]*)m(?P<m>[1-4]):(?P<i>(?:[a-z]*[0-9A-Z])+)[a-z]*$'
        res = re.match(pattern, game_id)
        if res is None:
            raise ValueError("game_id invalide")

        width = int(res["w"])
        height = int(res["h"])
        m = int(res["m"])
        islands = []
        currentIndex = 0
        step_pattern = r'([a-z]*)([0-9A-Z])'
        for delta_cars, number in re.findall(step_pattern, res["i"]):
            for car in delta_cars:
                currentIndex += ord(car) - ord('a') + 1
            if number in "0123456789":
                n = int(number)
            else:
                n = ord(number) - ord('A') + 10
            islands.append((currentIndex,n))
            currentIndex += 1
        return Data(width, height, islands, m)
