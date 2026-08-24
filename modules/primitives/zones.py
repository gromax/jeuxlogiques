from typing import List, Tuple, Union
from modules.primitives.cellgroup import CellGroup
import re

class Zones:
    """
    Représente un ensemble de zones d'une grille de jeu
    sert à décoder la description d'une grille de jeu à partir d'une chaîne de caractères
    et à fournir les zones de la grille
    """

    __labels:List[int]  # permet de donner un numéro de zone pour chaque cellule
    __width:int
    __height:int
    __horNumber:int # nombre de murs horizontaux
    __verNumber:int # nombre de murs verticaux
    __verWall:List[bool]
    __horWall:List[bool]
    __cells:CellGroup

    def __init__(self, width:int, height:int):
        self.__width = width
        self.__height = height
        self.__labels = list(range(width*height))
        self.__horNumber  = width*(height-1)
        self.__verNumber = height*(width-1)
        # initialement, tous les murs sont mis
        self.__horWall = [True]*self.__horNumber
        self.__verWall = [True]*self.__verNumber
        self.__cells = CellGroup.make_from_size("cells", (width,height))

    def __cellTag(self, iline:int, icol:int) -> int:
        """
        renvoie le numéro de zone de la cellule (iline, icol)
        """
        assert 0 <= iline < self.__height
        assert 0 <= icol < self.__width
        return self.__labels[iline*self.__width + icol]
    
    def upLabel(self, oldLabel:int, newLabel:int):
        """
        remplace oldLabel par newLabel dans les labels de toutes les cellules
        """
        if oldLabel is newLabel:
            return
        for i in range(len(self.__labels)):
            if (self.__labels[i] == oldLabel):
                self.__labels[i] = newLabel

    def removeVerWall(self, index:int):
        """
        retire la cloison verticale d'indice index
        et met à jour les labels des cellules concernées
        """
        if not 0 <= index < self.__verNumber:
            return
        assert self.__verWall[index]
        self.__verWall[index] = False
        iline = index // (self.__width - 1)
        icol = index % (self.__width - 1)
        newLabel = self.__cellTag(iline, icol)
        oldLabel = self.__cellTag(iline, icol+1)
        self.upLabel(oldLabel, newLabel)

    def removeHorWall(self, index:int):
        """
        retire la cloison horizontale d'indice index
        et met à jour les labels des cellules concernées
        """
        if not 0 <= index < self.__horNumber:
            return
        assert self.__horWall[index]
        self.__horWall[index] = False
        icol = index // (self.__height - 1)
        iline = index % (self.__height - 1)
        newLabel = self.__cellTag(iline, icol)
        oldLabel = self.__cellTag(iline+1, icol)
        self.upLabel(oldLabel, newLabel)

    @property
    def labels(self) -> List[int]:
        """
        renvoie une copie de la liste des labels des cellules
        """
        return self.__labels.copy()
    
    @property
    def width(self) -> int:
        """
        renvoie la largeur de la grille
        """
        return self.__width

    @classmethod
    def tag_to_id(cls, chaine:str) -> str:
        """
        produit un id type tatham avec une chaine décrivant graphiquement la grille comme
        AAA
        ABC
        BBC
        """
        lines = [line.strip() for line in chaine.split('\n')]
        lines = [line for line in lines if line != ""]
        return cls.array_to_id(lines)

    @classmethod
    def array_to_id(cls, lines:List[Union[str,List]]) -> str:
        height = len(lines)
        s = [len(line) for line in lines]
        assert min(s) == max(s), "longueurs différentes !"
        width = min(s)
        verWalls = []
        for i in range(height):
            for j in range(width-1):
                verWalls.append(lines[i][j] != lines[i][j+1])
        horWalls = []
        for j in range(width):
            for i in range(height-1):
                horWalls.append(lines[i][j] != lines[i+1][j])
        walls = verWalls + horWalls
        wallsStr = ""
        c = 0
        for w in walls:
            if w and c>0:
                wallsStr += chr(ord('a')  + c - 1)
                c= 0
            elif w:
                wallsStr += '_'
            else:
                c += 1
        if c>0:
            wallsStr += chr(ord('a')  + c - 1)
        
        index = 0
        c = 1
        while index<len(wallsStr)-1:
            if wallsStr[index] != wallsStr[index+1] and c <= 2:
                index += 1
                c = 1
            elif wallsStr[index] == wallsStr[index+1] and c < 8:
                index += 1
                c += 1
            else:
                # cas d'un remplacement
                # index est donc la cième répétition du caractère
                wallsStr = wallsStr[:index-c+2] + str(c) + wallsStr[index+1:]
                index = index - c + 3
                c= 1
        if c>2:
            wallsStr = wallsStr[:-c+1] + str(c)
        return str(width)+"x"+str(height)+":"+wallsStr



    @classmethod
    def makeFromStr(cls, chaine:str) -> "Zones":
        """
        chaine: une chaîne de caractères décrivant la grille de jeu, au format:
            size:description des murs
            Par exemple, pour une grille de taille 6, on peut avoir:
            6:aa_4a_3a_a_3a__a_a_aa_a_3a_a__aa_a4
            où:
            - le chiffre indique une répétition. Par ex _4 veut dire _ _ _ _
            - _ veut dire que la prochaine limite verticale sera une cloison
            - a veut dire que l'on sautera la prochaine cloison, b on sautera 2 cloisons...
        renvoie l'objet Zones correspondant à la description de la grille
        """
        # 6:aa_4a_3a_a_3a__a_a_aa_a_3a_a__aa_a4
        parts = chaine.split(':')
        if 'x' in parts[0]:
            wStr, hStr = parts[0].split('x')
            width = int(wStr)
            height = int(hStr)
        else:
            width = int(parts[0])
            height = width
        wallsStr = parts[1]
        # le chiffre indique une répétition. Par ex _4 veut dire _ _ _ _
        # _ veut dire que la prochaine limite verticale sera une cloison
        # a veut dire que l'on sautera la prochaine cloison, b on sautera 2 cloisons...
        wallsParts = re.findall(r"[a-z_][0-9]*", wallsStr)
        wallsParts.reverse()
        walls = []
        N_hor = width*(height-1)
        N_ver = height*(width-1)
        while len(wallsParts) > 0:
            item = wallsParts.pop()
            if len(item) > 1:
                rep = int(item[1:])
                wallsParts = wallsParts + [item[0]]*rep
                continue
            L = 0 if item[0] == '_' else ord(item[0]) - ord('a') + 1
            # L est le nombre de cloisons qu'il faut sauter
            walls = walls + [False]*L + [True]
        # Il pourrait y avoir un problème s'il n'y avait pas 2*N...
        # s'il y en a 2N+1 et que le dernier est True, là c'est bon
        if not (len(walls) ==N_hor + N_ver or  len(walls)== N_hor + N_ver + 1 and walls[-1]):
            print(f"On obtient {len(walls)} au lieu de {N_hor + N_ver} marques de murs, peut être problème.")
        
        verWalls = walls[:N_ver]
        horWalls = walls[N_ver:]

        g = Zones(width, height)
        for i, item in enumerate(verWalls):
            if not item:
                g.removeVerWall(i)
        for i, item in enumerate(horWalls):
            if not item:
                g.removeHorWall(i)
        
        L = g.labels
        return g

    def __coords_with_label(self, label:int) -> List[Tuple[int,int]]:
        """
        label: numéro de zone demandée
        renvoie la liste des coordonnées des cellules de la zone de numéro label
        """
        return [(i//self.__width, i%self.__width) for i, lab in enumerate(self.__labels) if lab == label]

    @property
    def cells(self) -> CellGroup:
        return self.__cells
    
    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height


    def zones(self)->Tuple[List[CellGroup], List[CellGroup], List[CellGroup]]:
        """
        renvoie les listes de zones pour les lignes, les colonnes, et les zones de la grille
        """
        lines = [CellGroup(f"line {i}") for i in range(self.__height)]
        cols = [CellGroup(f"col {i}") for i in range(self.__width)]
        zones = []
        for lab in set(self.__labels):
            z = CellGroup(lab)
            coordsList = self.__coords_with_label(lab)
            for iline, icol in coordsList:
                cell = self.__cells[iline, icol]
                lines[iline].add_coord(iline, icol,cell)
                cols[icol].add_coord(iline, icol, cell)
                z.add_coord(iline, icol, cell)
            zones.append(z)
        return lines, cols, zones
    
    def zones_ij(self) -> List[List[Tuple[int,int]]]:
        """
        Chaque groupe est une liste de (i,j). Renvoie la liste de ces groupes
        """
        return [self.__coords_with_label(lab) for lab in set(self.__labels)]
    
