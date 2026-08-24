# exemple :
# 15x15:bcaececfcgbebbdbac_cn_bra__bd__eqgefddaiab_ckb,2,4,2,4,2,4,3,4,3,2,4,1,4,3,3,4,3,3,3,4,2,4,3,3,3,2,2,2,2,5
from typing import List
from modules.container.camping import Data

def decoder(game_id:str) -> Data:
    """
    game_id: chaîne selon jeu nurikabe
    """
    width:int
    height:int
    trees:List[int]
    right:List[int]
    top:List[int]

    sizeStr, contentStr = game_id.split(':')
    if "x" in sizeStr:
        wStr, hStr = sizeStr.split('x')
        width = int(wStr)
        height = int(hStr)
    else:
        width = int(sizeStr)
        height = width
    parts = contentStr.split(',')
    trees = []
    index = 0
    for car in parts[0]:
        if ord("a") <= ord(car) <= ord("z"):
            index += ord(car) - ord('a') + 1
        trees.append(index)
        index += 1
    if len(trees)>0 and trees[-1] == height*width:
        # le codage peut entraîner un arbre en trop
        trees.pop()
    clues = [int(car) for car in parts[1:]]
    top = clues[:width]
    right = clues[width:]
    return Data(width, height, trees, right, top)
