# exemple :
# 7x7:6,16,8,bLeLdRcLaRLaRLbRcLRaRLaLaReRLRRa,3,3,4,4,8,2,3,4,0,0,3,2,5,1,1,0,1,0,0,2,3,1,0,3,0,3,2,2

from typing import List, Tuple, Dict

class TathamUndeadDecoder:
    __game_id:str
    __size:int
    __ghosts:int
    __vampires:int
    __zombies:int
    __mirrors:Dict[Tuple[int,int], bool]
    __latteralsCounts:Dict[str, List[int]]

    def __init__(self, game_id:str):
        """
        game_id: chaîne selon jeu keen de simon tatham
        """
        self.__game_id = game_id
        sizeStr, contentStr = game_id.split(':')
        wStr, hStr = sizeStr.split('x')
        assert wStr == hStr, "jeu non carré"
        self.__size = int(wStr)

        items = contentStr.split(',')
        # 3 premiers items : nombre de ghosts, vampire, zombies
        self.__ghosts = int(items[0])
        self.__vampires = int(items[1])
        self.__zombies = int(items[2])

        # 4ème item : miroir. minuscules indiquent le nombre de case à sauter
        # majuscule L ou R pour la position du miroir
        self.__mirrors = {}
        index = 0
        for car in items[3]:
            if car in "LR":
                self.__mirrors[(index//self.__size, index%self.__size)] = (car == "L")
                index += 1
            else:
                index += ord(car) - ord('a') + 1
        latCounts = list(map(int, items[4:]))
        
        n = self.__size
        self.__latteralsCounts = {
            "top": latCounts[0:n],
            "right": latCounts[n:2*n],
            "bottom": latCounts[2*n:3*n][::-1],
            "left": latCounts[3*n:4*n][::-1]
        }

    @property
    def size(self) -> int:
        return self.__size

    @property
    def game_id(self) -> str:
        return self.__game_id
    
    @property
    def vampires(self) -> int:
        return self.__vampires

    @property
    def ghosts(self) -> int:
        return self.__ghosts

    @property
    def zombies(self) -> int:
        return self.__zombies

    @property
    def mirrors(self) -> Dict[Tuple[int, int], bool]:
        return self.__mirrors.copy()

    @property
    def top(self) -> List[int]:
        return self.__latteralsCounts["top"].copy()
    
    @property
    def right(self) -> List[int]:
        return self.__latteralsCounts["right"].copy()
    
    @property
    def bottom(self) -> List[int]:
        return self.__latteralsCounts["bottom"].copy()
    
    @property
    def left(self) -> List[int]:
        return self.__latteralsCounts["left"].copy()