from modules.container.towers import Data
from typing import Tuple, Dict

def __get_knowns(size:int, code:str) -> Dict[Tuple[int,int], int]:
    knowns = {}
    if code == "":
        return {}
    current_index = 0
    for car in code:
        d = ord(car) - ord('a') + 1
        if 1 <= d <= 26:
            current_index += d
        elif car in "123456789":
            i = current_index//size
            j = current_index%size
            knowns[i,j] = int(car)
            current_index += 1
    return knowns


def decoder(game_id:str) -> Data:
    sizeStr, contentStr = game_id.split(":")
    size = int(sizeStr)
    if "," in contentStr:
        bordersStr, knownsStr = contentStr.split(',')
    else:
        bordersStr = contentStr
        knownsStr = ""
    knowns = __get_knowns(size, knownsStr)
    clues = [int(item) if item != '' else 0 for item in bordersStr.split('/')]
    return Data(size, clues, knowns)
