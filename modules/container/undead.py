from typing import List, Tuple, Dict

class Data:
    """
    Contient les informations de jeu
    """
    __width:int
    __height:int
    __clues:Tuple[int]
    __ghosts:int
    __vampires:int
    __zombies:int
    __mirrors:Dict[Tuple[int,int], bool]

    def __init__(
        self,
        width:int,
        height:int,
        clues:List[int],
        ghosts:int,
        vampires:int,
        zombies:int,
        mirrors:Dict[Tuple[int,int], bool],
    ):
        """
        :param width: largeur du jeu
        :param height: hauteur du jeu
        :param clues: indices du bord donné dans le sens horaire depuis haut gauche
        :param ghosts: nombre de fantômes
        :param vampires: nombre de vampires
        :param zombies: nombre de zombies
        :param mirrors: dictionnaire des miroirs, clé = (i,j), valeur = True si miroir, False sinon
        """
        self.__width = width
        self.__height = height
        self.__clues = tuple(clues)
        self.__ghosts = ghosts
        self.__vampires = vampires
        self.__zombies = zombies
        self.__mirrors = mirrors.copy()

    @property
    def height(self) -> int:
        return self.__height

    @property
    def width(self) -> int:
        return self.__width

    @property
    def game_id(self) -> str:
        # Forme : sizexsize:mirrors,laterals Clues
        mirrors = []
        lastIndex = -1
        for index in range(self.__width*self.__height):
            col = index % self.__width
            row = index // self.__width
            if (row,col) not in self.__mirrors:
                continue
            delta = index - lastIndex
            if delta > 1:
                letter = chr(ord('a') + delta - 2)
                mirrors.append(letter)
            mirrors.append("L" if self.mirrors[row,col] else "R")
            lastIndex = index
        delta = self.__width * self.__height - lastIndex
        if delta > 1:
            letter = chr(ord('a') + delta - 2)
            mirrors.append(letter)
        return f"{self.__width}x{self.__height}:{self.__ghosts},{self.__vampires},{self.__zombies},{''.join(mirrors)},{",".join(str(c) for c in self.__clues)}"

    @property
    def top(self) -> Tuple[int]:
        return self.__clues[:self.__width]

    @property
    def right(self) -> Tuple[int]:
        return self.__clues[self.__width:self.__width + self.__height]

    @property
    def bottom(self) -> Tuple[int]:
        return self.__clues[self.__width + self.__height:2 * self.__width + self.__height][::-1]

    @property
    def left(self) -> Tuple[int]:
        return self.__clues[2 * self.__width + self.__height:][::-1]

    @property
    def mirrors(self) -> Dict[Tuple[int,int], bool]:
        return self.__mirrors.copy()

    @property
    def ghosts(self) -> int:
        return self.__ghosts

    @property
    def vampires(self) -> int:
        return self.__vampires

    @property
    def zombies(self) -> int:
        return self.__zombies

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon jeu keen de simon tatham
        """
        sizeStr, contentStr = game_id.split(':')
        wStr, hStr = sizeStr.split('x')
        width = int(wStr)
        height = int(hStr)

        items = contentStr.split(',')
        # 3 premiers items : nombre de ghosts, vampire, zombies
        ghosts = int(items[0])
        vampires = int(items[1])
        zombies = int(items[2])

        # 4ème item : miroir. minuscules indiquent le nombre de case à sauter
        # majuscule L ou R pour la position du miroir
        mirrors = {}
        index = 0
        for car in items[3]:
            if car in "LR":
                mirrors[(index//width, index%width)] = (car == "L")
                index += 1
            else:
                index += ord(car) - ord('a') + 1
        latCounts = list(map(int, items[4:]))
        
        return Data(width, height, latCounts, ghosts, vampires, zombies, mirrors)
