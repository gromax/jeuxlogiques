# exemple :
# 7x7:6,16,8,bLeLdRcLaRLaRLbRcLRaRLaLaReRLRRa,3,3,4,4,8,2,3,4,0,0,3,2,5,1,1,0,1,0,0,2,3,1,0,3,0,3,2,2

from typing import List, Tuple, Dict
from modules.container.undead import Data

def decoder(game_id:str) -> Data:
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
