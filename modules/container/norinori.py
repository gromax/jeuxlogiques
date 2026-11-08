from typing import List
from modules.primitives.zones import Zones
from modules.primitives.cellgroup import CellGroup

class Data:
    """
    Objet contenant les données utiles
    """
    _zones:Zones

    def __init__(self, z:Zones):
        self._zones = z

    @property
    def width(self) -> int:
        return self._zones.width

    @property
    def height(self) -> int:
        return self._zones.height

    @property
    def game_id(self) -> str:
        return self._zones.toTathamStr()

    def toStringDbg(self) -> str:
        """
        donne une représentation de la grille, afin de débugage
        """
        return self._zones.toLettersTags()

    @classmethod
    def decode(cls, game_id:str) -> "Data":
        """
        game_id: chaîne selon le style tatham
        """
        z = Zones.makeFromStr(game_id)
        return Data(z)

    @property
    def zones(self) -> List[CellGroup]:
        _, _, z = self._zones.zones()
        return z
