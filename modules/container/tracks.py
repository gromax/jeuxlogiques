from typing import Tuple, List, Dict
from modules.primitives.direction import Direction

Symbol = Tuple[Direction, Direction]

class Data:
    __width:int
    __height:int
    __rails:Dict[Tuple[int,int], Symbol]
    __clues:Tuple[int]
    __AB:Tuple[int,int]

    TAGS:Dict[str,Symbol] = {
        "A" : (Direction.DOWN, Direction.UP), # Vertical
        "6" : (Direction.LEFT, Direction.UP), # coude L-U
        "C" : (Direction.LEFT, Direction.DOWN), # coude L-D
        "5" : (Direction.LEFT, Direction.RIGHT), # horizontal
        "3" : (Direction.RIGHT, Direction.UP), # coude R-U
        "9" : (Direction.RIGHT, Direction.DOWN) # coude L-D
    }

    def __init__(
            self,
            width:int,
            height:int,
            rails:List[int],
            clues:List[int],
            AB:List[int]
        ):
        self.__width = width
        self.__height = height
        self.__rails = rails.copy()
        self.__clues = tuple(clues)
        self.__AB = tuple(AB) # indices des clues avec entrée/sortie A et B
        # A est toujours le grand petit des 2
        self.__inout = [
            'A' if i == max(AB) else 'B' if i == min(AB) else '' for i in range(width+height)
        ]

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def AB(self) -> Tuple[int,int]:
        return self.__AB

    def __saut_to_car(self, saut:int) -> str:
        if saut <= 0:
            return ""
        if saut <= 26:
            return chr(ord('a') + saut - 1)
        if saut %26 == 0:
            return "z"*(saut//26)
        return "z"*(saut//26) + chr(ord('a') + saut%26 - 1)

    @property
    def game_id(self) -> str:
        # construit un game_id version tatham
        # ex : 8x8:zl6a6b3m9f,2,S3,3,3,3,4,8,6,2,2,2,4,8,S6,2,6
        sizeStr = f"{self.__width}x{self.height}"
        currentIndex = 0
        railsListStr = []
        for iline, icol in self.__rails:
            index = iline*self.__width + icol
            if index > currentIndex:
                railsListStr.append(self.__saut_to_car(index - currentIndex))
            symbol = self.__rails[iline,icol]
            tag = Data.symbol_to_tag(symbol)
            assert tag != "?", "Direction non reconnue"
            railsListStr.append(tag)
            currentIndex = index + 1
        dlast = self.__width * self.__height - currentIndex
        if dlast > 0:
            saut = chr(ord('a') + dlast - 1)
            railsListStr.append(saut)
        cluesList = [f"S{clue}" if index in self.__AB else str(clue) for index, clue in enumerate(self.__clues)]
        return sizeStr + ":" + "".join(railsListStr) + "," + ",".join(cluesList)

    @classmethod
    def symbol_to_tag(cls, symbol:Symbol) -> str:
        sym = (symbol[1], symbol[0]) # symétrique
        for tag in cls.TAGS:
            if cls.TAGS[tag] == symbol or cls.TAGS[tag] == sym:
                return tag
        return "?"

    
    @property
    def rails(self) -> Dict[Tuple[int,int], Symbol]:
        return self.__rails.copy()
    
    @property
    def top(self) -> Tuple[int]:
        return self.__clues[:self.__width]
    
    @property
    def right(self) -> Tuple[int]:
        return self.__clues[self.__width:]

    @property
    def clues(self) -> Tuple[int]:
        return self.__clues

    @property
    def left(self) -> Tuple[str]:
        # renvoie les symboles d'entrée sortie
        return self.__inout[self.__width:]

    @property
    def bottom(self) -> Tuple[str]:
        return self.__inout[:self.__width]


    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu Tracks
        ex: 8x8:zl6a6b3m9f,2,S3,3,3,3,4,8,6,2,2,2,4,8,S6,2,6
        """
        width:int
        height:int
        rails:List[int]
        clues:List[int]

        sizeStr, contentStr = game_id.split(':')
        wStr, hStr = sizeStr.split('x')
        width = int(wStr)
        height = int(hStr)
        parts = contentStr.split(',')

        railsStr = parts[0]
        AB = []
        clues = []
        for index, item in enumerate(parts[1:]):
            if item.startswith("S"):
                AB.append(index)
                item = item[1:].strip()
            if item == "":
                clues.append(-1)
            else:
                clues.append(int(item))
        assert len(clues) == width + height, "taille ne correspond pas aux indices"
        assert len(AB) == 2, "nombre de sorties incohérent"

        # il faut ensuite décoder les rails présents.
        index = 0
        rails:Dict[Tuple[int,int],Symbol] = {}
        for car in railsStr:
            if ord("a") <= ord(car) <= ord("z"):
                index += ord(car) - ord('a') + 1
                continue
            assert car in Data.TAGS
            iline = index // width
            icol = index % width
            rails[iline, icol] = Data.TAGS[car]
            index += 1
        return Data(width, height, rails, clues, AB)