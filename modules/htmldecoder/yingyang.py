"""
Décodeur pour le site fr.puzzle-yin-yang.com
"""

import re
from typing import List
from playwright.sync_api import sync_playwright
from modules.container.yingyang import Data

URL = "https://fr.puzzle-yin-yang.com/"

def decode_html(url_complement:str) -> Data:
    """
    Décodeur pour le site fr.puzzle-yin-yang.com
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
    content = __decode(html)
    size = int(len(content)**0.5)
    clues = {}
    for i, v in enumerate(content):
        iline = i//size
        icol = i%size
        if v == 1:
            clues[iline,icol] = True
        elif v == -1:
            clues[iline,icol] = False
    return Data(size, size, clues)
    
def __decode(html:str) -> List[int]:
    """
    Décode le code html pour extraire le jeu
    """
    pattern = r'<div[^>]*class="(task-)?cell\s([^"]*)"'
    content = []
    for _, b in re.findall(pattern, html):
        if "selectable" in b:
            content.append(0)
        elif "0" in b:
            content.append(1)                
        else:
            content.append(-1)
    return content


