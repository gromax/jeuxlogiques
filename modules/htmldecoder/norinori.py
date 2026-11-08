"""
Décodeur pour le site https://fr.puzzle-nurikabe.com/
"""

import re
from playwright.sync_api import sync_playwright
from modules.container.norinori import Data
from modules.primitives.zones import Zones

URL = "https://fr.puzzle-norinori.com/"

def decode_html(url_complement:str) -> Data:
    """
    Décodeur pour le site https://fr.puzzle-norinori.com/
    """
    url = URL if url_complement == "" else URL + f"?size={url_complement}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        # attendre que la page soit chargée
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
    return __decode(html)

def __decode(html:str) -> Data:
    """
    Décode le code html pour extraire le jeu
    """
    pattern = r'<div[^>]*class="cell\sselectable([^"]*)"(?:[^>]*)'
    content = []
    for n in re.findall(pattern, html):
        content.append(("br" in n, "bb" in n))
    s = int(len(content)**0.5)
    z = Zones(s, s)
    for index, (wr, wb) in enumerate(content):
        iline = index // s
        icol = index % s
        if not wr:
            z.removeRightWall(iline, icol)
        if not wb:
            z.removeBottomWall(iline, icol)
    return Data(z)
