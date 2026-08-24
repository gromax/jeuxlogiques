from modules.container.bridges import Data
import re

def decoder(game_id:str) -> Data:
    """
    game_id: chaîne selon jeu loopy de simon tatham
    ex: 7x7m2:a3d31h3c42b2a3b2e3a6b3b2d3
    """
    pattern = r'^(?P<w>[1-9][0-9]*)x(?P<h>[1-9][0-9]*)m(?P<m>[1-4]):(?P<i>(?:[a-z]*[0-9A-Z])+)[a-z]*$'
    res = re.match(pattern, game_id)
    if res is None:
        raise ValueError("game_id invalide")

    width = int(res["w"])
    height = int(res["h"])
    m = int(res["m"])
    islands = []
    currentIndex = 0
    step_pattern = r'([a-z]*)([0-9A-Z])'
    for delta_cars, number in re.findall(step_pattern, res["i"]):
        for car in delta_cars:
            currentIndex += ord(car) - ord('a') + 1
        if number in "0123456789":
            n = int(number)
        else:
            n = ord(number) - ord('A') + 10
        islands.append((currentIndex,n))
        currentIndex += 1
    return Data(width, height, islands, m)
