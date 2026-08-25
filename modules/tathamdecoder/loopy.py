from modules.container.loopy import Data

def decoder(game_id:str) -> Data:
    """
    game_id: chaîne selon jeu loopy de simon tatham
    exemple, uniquement pour les carrés : 7x7t0:a22d3c1b3022a3c3a2b02b2b1b31a1d2b
    """
    sizeStr, contentStr = game_id.split(':')
    wStr, hStr = sizeStr.split("x")
    width = int(wStr)
    assert hStr.endswith("t0"), "game_id incorrect"
    height = int(hStr[:-2]) # supprime le "t0"
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
    return Data(width, height, clues)

