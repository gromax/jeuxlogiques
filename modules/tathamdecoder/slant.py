# exemple :
# 11x11:d1d11a1a2b2123a11a3a231a21d3c23a211b1b32a133a1a123a3e1a223d312f131a1c132b1c2a11d233a1b23a3a3a2b1d1d11a

from modules.container.slant import Data

def decoder(game_id:str) -> Data:
    """
    game_id: chaîne selon jeu keen de simon tatham
    """

    sizeStr, contentStr = game_id.split(':')
    wStr, hStr = sizeStr.split('x')
    width = int(wStr)
    height = int(hStr)

    constraints = {}
    index = 0
    W = width + 1 # indices sur les lignes donc une colonne de plus
    for car in contentStr:
        if car in "01234":
            constraints[index//W, index%W] = int(car)
            index += 1
        else:
            index += ord(car) - ord('a') + 1
    return Data(width, height, constraints)

