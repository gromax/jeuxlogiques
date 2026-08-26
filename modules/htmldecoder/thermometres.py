"""
Décodeur pour le site fr.puzzle-yin-yang.com
"""

import re
from typing import List, Tuple, Dict
from playwright.sync_api import sync_playwright
from modules.container.thermometres import Data
from modules.primitives.direction import Direction

CONNEXIONS:Dict[str,List[Direction]] = {
    'start': [Direction.UP],
    'end': [Direction.UP],
    'straight':[Direction.UP, Direction.DOWN],
    'curve':[Direction.UP, Direction.RIGHT]
}

URL = "https://fr.puzzle-thermometers.com/"

def decode_html(url_complement:str) -> Data:
    """
    Décodeur pour le site https://fr.puzzle-thermometers.com/
    """
    url = URL if url_complement == "" else url = URL + f"?size={url_complement}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # attendre que la page soit chargée
        page.wait_for_load_state("networkidle")

        html = page.content()

        browser.close()
    return __decode(html)

    
def __decode( html:str) -> Data:
    size, thermos = __decode_thermos(html)
    clues = __decode_clues(html)
    return Data(size, size, thermos, clues)


def __decode_thermos(html:str) -> Tuple[int, List[int]]:
    """
    Décode le code html pour extraire le jeu
    """
    # morceaux de thermo
    pattern = r'<div[^>]*class="cell\s*selectable\s*(?P<rotate>(?:\sr[1-3])?) (?P<type>(?:start)|(?:end)|(?:straight)|(?:curve)) [^>]*top:(?P<top>\s*[0-9]*)px[^>]*left:(?P<left>\s*[0-9]*)px'
    n_rot = lambda tag: 0 if tag == "" else int(tag[-1])
    brut_content = [(n_rot(r), t, int(top), int(left)) for r,t, top, left in re.findall(pattern, html)]
    brut_content.sort(key= lambda item: item[2:])
    size = int(len(brut_content)**0.5)
    content = {(index//size,index%size): brut_content[index][:2] for index in range(size**2)}
    starts = [(i,j) for (i,j) in content if content[i,j][1] == "start"]
    
    thermos = []
    for starti, startj in starts:
        thermo = [(starti,startj)]
        thermos.append(thermo)
        while content[thermo[-1]][1] != "end":
            i,j = thermo[-1]
            r, t = content[i,j]
            conns:List[Direction] = CONNEXIONS[t]
            for _ in range(r):
                conns = [c.rotate_right() for c in conns]
            neighbors = [(i+di, j+dj) for (di,dj) in [c.delta() for c in conns] if (i+di,j+dj) not in thermo]
            assert len(neighbors) == 1
            thermo.append(neighbors[0])
    return size, thermos

def __decode_clues(html:str) -> List[int]:
    pattern = r'<div[^>]*class="cell\s*task\s*(?:v|h)[^>]*>([0-9]*)<'
    return [int(item) for item in re.findall(pattern, html)]




