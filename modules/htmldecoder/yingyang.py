"""
Décodeur pour le site fr.puzzle-yin-yang.com
"""

import re
from typing import List, Tuple, Dict
from playwright.sync_api import sync_playwright

class YingyangHtmlDecoder:
    """
    Décodeur pour le site fr.puzzle-yin-yang.com
    """
    __content:Dict[Tuple[int,int],bool]
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
            if v == 1:
                self.__content[iline,icol] = True
            elif v == -1:
                self.__content[iline,icol] = False
    
    def __decode(self, html:str) -> List[int]:
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
            gid += "B" if self.__content[(i,j)] is True else "N"
            index += 1
        return gid
    
    @property
    def content(self) -> Dict[Tuple[int,int],bool]:
        return self.__content.copy()

