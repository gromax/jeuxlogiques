from modules.container.palisade import Data

def decoder(game_id:str) -> Data:
    """
    game_id: chaîne selon jeu palisade de simon tatham
    exemple, uniquement pour les carrés : 10x8n8:a22d3c1b3022a3c3a2b02b2b1b31a1d2b
    """
    gridStr, contentStr = game_id.split(':')
    sizeStr,nStr = gridStr.split("n")
    wStr, hStr = sizeStr.split("x")
    width = int(wStr)
    height = int(hStr)
    zoneSize = int(nStr)
    assert (width*height)%zoneSize == 0, "la taille de zone doit diviser la taille de la grille"
    clues = {}
    i = 0
    for car in contentStr:
        if car in "01234":
            # c'est un digit à placer
            c = int(car)
            iline = i // width
            icol = i % width
            clues[iline, icol] = c
            i += 1
            continue
        delta = ord(car) - ord('a') + 1
        i += delta
    return Data(width, height, zoneSize, clues)

