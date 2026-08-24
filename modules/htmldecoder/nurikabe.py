"""
Décodeur pour le site https://fr.puzzle-nurikabe.com/
"""

import re
from typing import List, Tuple, Dict
from playwright.sync_api import sync_playwright

class NurikabeHtmlDecoder:
    """
    Décodeur pour le site https://fr.puzzle-nurikabe.com/
    """
    __content:Dict[Tuple[int,int],int]
    def __init__(self, url:str):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            # attendre que la page soit chargée
            page.wait_for_load_state("networkidle")

            html = page.content()

            browser.close()
        content = self.__decode(html)
        self.__size = int(len(content)**0.5)
        self.__content = {}
        for i, v in enumerate(content):
            iline = i//self.__size
            icol = i%self.__size
            if v > 0:
                self.__content[iline,icol] = v

    def __decode(self, html:str) -> List[int]:
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

    @property
    def size(self) -> int:
        return self.__size
    
    @property
    def game_id(self) -> str:
        gid = f"{self.__size}:"
        keys = sorted(self.__content.keys())
        index = 0
        for i,j in keys:
            new_index = i*self.__size+j
            delta = new_index - index
            if delta > 0:
                gid += chr(ord('a')+delta-1)
            index = new_index
            gid += chr(ord('A')+self.__content[(i,j)]-1)
            index += 1
        return gid
    
    @property
    def content(self) -> Dict[Tuple[int,int],int]:
        return self.__content.copy()

