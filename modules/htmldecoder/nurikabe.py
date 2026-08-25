"""
Décodeur pour le site https://fr.puzzle-nurikabe.com/
"""

import re
from typing import List
from playwright.sync_api import sync_playwright
from modules.container.nurikabe import Data

def decoder(url:str):
    """
    Décodeur pour le site https://fr.puzzle-nurikabe.com/
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # attendre que la page soit chargée
        page.wait_for_load_state("networkidle")

        html = page.content()

        browser.close()
    content_list = __decode(html)
    size = int(len(content_list)**0.5)
    content = {}
    for i, v in enumerate(content_list):
        iline = i//size
        icol = i%size
        if v > 0:
            content[iline,icol] = v
    return Data(size, size, content)

def __decode(html:str) -> List[int]:
    """
    Décode le code html pour extraire le jeu
    """
    pattern = r'<div[^>]*class="[^"]*cell\s([^"]*)"[^>]*>([0-9]*)</div>'
    content = []
    for _, n in re.findall(pattern, html):
        if n == "":
            content.append(0)
        else:
            content.append(int(n))
    return content
