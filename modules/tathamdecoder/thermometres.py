"""
Décodeur pour le site fr.puzzle-yin-yang.com
"""

import re
from modules.container.thermometres import Data
from modules.primitives.direction import Direction

def decoder(game_id:str) -> Data:
    dims, thermos_str, clues_str = game_id.split(":")
    if "x" in dims:
        wStr, hStr = dims.split("x")
        width = int(wStr)
        height = int(hStr)
    else:
        width = int(dims)
        height = width
    pattern = r'([0-9]*)>((?:[UDLR][a-z]*)+)'
    brut_content = [(int(start), path) for start, path in re.findall(pattern, thermos_str)]
    thermos = []
    for start, path in brut_content:
        i, j = start//width, start%width
        didjs = Direction.str_to_path(path)
        t = [(i,j)]
        for di, dj in didjs:
            dir = Direction.step_to_dir(di,dj)
            diStep, djStep = dir.delta()
            for _ in range(abs(di)+abs(dj)):
                i += diStep
                j += djStep
                t.append((i,j))
        thermos.append(t)
    clues = [int(it) for it in clues_str.split(',')]
    return Data(width, height, thermos, clues)
