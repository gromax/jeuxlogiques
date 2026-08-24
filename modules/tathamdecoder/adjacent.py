from modules.primitives.direction import Direction
from modules.container.adjacent import Data

def decoder(game_id:str) -> Data:
    """
    game_id: chaîne selon jeu loopy de simon tatham
    """
    constraints = {}
    knowns = {}

    sizeStr, valuesStr = game_id.split('a:')
    size = int(sizeStr)
    valuesStrList = valuesStr.split(',')[:size**2]

    # toutes les contraintes mises à False
    for iline in range(size):
        for icol in range(size):
            for d in Direction:
                constraints[iline, icol, d] = False

    for i, tag in enumerate(valuesStrList):
        iline = i//size
        icol = i%size
        symbols = tag[1:]
        for d in symbols:
            constraints[iline,icol,Direction(d)] = True
        k = int(tag[0])
        if k != 0:
            knowns[iline,icol] = k
    
    return Data(game_id, size, knowns, constraints)


