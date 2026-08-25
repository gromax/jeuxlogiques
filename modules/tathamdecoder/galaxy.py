from typing import List, Tuple
from modules.container.galaxy import Data

def decoder(game_id:str) -> Data:
    """
    game_id: chaîne selon jeu galaxy de simon tatham
    ex: 7x7:akisdznfrqtkh
    """
    sizeStr, contentStr = game_id.split(':')
    width, height = map(int, sizeStr.split("x"))

    values = [ord(letter) - ord('a') + 1 for letter in contentStr]
    t = -1
    S = 2*width - 1
    stars = [] # les coords sont doublées pour conserver des entiers
    for v in values:
        t += v
        if v == 26:
            # un z sert à faire un saut plus grand
            # exemple zc pour 28
            t -= 1
            continue
        stars.append((t//S, t%S))
    return Data(width, height, stars)

