from typing import Dict, List, Tuple, Union
from modules.container.slant import Data
from ortools.sat.python import cp_model

class SlantSolver:
    __width:int
    __height:int
    __constraints:Dict[Tuple[int,int],int]

    def __init__(self, data:Data):
        self.__width = data.width
        self.__height = data.height
        self.__constraints = data.clues

    def __neighbors_mils(self, i:int, j:int):
        """
        i,j représente une coordonnée en comptant les mileux
        on veut les voins en diagonale
        """
        if (i+j)%2 == 0:
            return []
        deltas = [(1,1),(-1,-1),(-1,1),(1,-1)]
        ns = [(i+di, j+dj) for di,dj in deltas]
        return [(ni,nj) for (ni,nj) in ns if 0 <= ni < 2*self.__height+1 and 0 <= nj < 2*self.__width+1]

    def __desc_diag(self, i:int, j:int) -> List[Tuple[int,int]]:
        """
        (i,j): position d'un intersection
        renvoie les coordonnées de case en haut à gauche et en bas à droite
        si sur un bord, l'une des deux sera absente
        """
        out = []
        if i>0 and j>0:
            out.append((i-1,j-1)) # haut gauche
        if i<self.__height and j<self.__width:
            out.append((i,j)) # bas droite
        return out
   
    def __asc_diag(self, i:int, j:int) -> List[Tuple[int,int]]:
        """
        (i,j): position d'un intersection
        renvoie les coordonnées de case en haut à droite et en bas à gauche
        si sur un bord, l'une des deux sera absente
        """
        out = []
        if i<self.__height and j>0:
            out.append((i,j-1)) # bas gauche
        if i>0 and j<self.__width:
            out.append((i-1,j)) # haut droit
        return out

    def solve(self) -> Union[List[bool], False]:
        model = cp_model.CpModel()

        # -------------------------
        # Variables cellules
        # -------------------------
        cell = {}
        # valeur True pour un diag dans le sens montant
        for i in range(self.__height):
            for j in range(self.__width):
                cell[i,j] = model.NewBoolVar(f"c_{i}_{j}")
        
        # -------------------------------
        # Prise en compte des contraintes
        # -------------------------------
        for (i,j), v in self.__constraints.items():
            # les cells False sur la diag descendante comptent +1
            # les cells True sur la diag ascendante comptent +1
            # on doit donc avoir sum(ascendante) + 2 - sum(descendante) == contrainte
            cells_asc = [cell[ic,jc] for (ic,jc) in self.__asc_diag(i,j)]
            cells_desc = [cell[ic,jc] for (ic,jc) in self.__desc_diag(i,j)]
            k = len(cells_desc)
            model.Add(sum(cells_asc) + k - sum(cells_desc) == v)
        
        #---------------------------------------
        # le flux entre les lignes doit circuler
        #---------------------------------------
        # on va numéroter toutes les cases de milieu
        # si on compte tous les sommets et les milieu on en 2*w + 1
        # idem pour les lignes : 2*h+1
        # un milieu sur une ligne horizontale à un j impair et i pair
        # réciproqhement pour milieu vertical
        # on veut donc i + j impair
        # on aura donc w*(h+1) + (w+1)*h cases en tout
        # on ajoutera une cellule root en plus
        N = self.__width*(self.__height + 1) + (self.__width + 1)*self.__height + 1
        flux = {}
        for i in range(2*self.__height+1):
            for j in range(2*self.__width+1):
                if (i+j)%2 == 0:
                    continue
                n_mils = self.__neighbors_mils(i,j)
                for (ni,nj) in n_mils:
                    flux[i,j,ni,nj] = model.NewIntVar(0, N, f"flux_{i}_{j}_{ni}_{nj}")
                    # flux seulement si segment le permet
                    # calcul de la cellule correspondante
                    ic = (i+ni)//4
                    jc = (j+nj)//4
                    # passe si la cellule est dans le même sens
                    if (ni-i)*(nj-j)<0: # ascendant
                        model.Add(flux[i,j,ni,nj] <= N * cell[ic,jc])
                    else:
                        model.Add(flux[i,j,ni,nj] <= N * cell[ic,jc].Not())
        # on ajoute un flux venant d'une cellule r qui communique avec tous les milieux de bords
        for i in range(1,2*self.__height+1,2):
            flux[-1,-1,i,0] = model.NewIntVar(0, N, f"flux_root_{i}_{0}")
            flux[-1,-1,i,2*self.__width] = model.NewIntVar(0, N, f"flux_root_{i}_{2*self.__width}")
        for j in range(1,2*self.__width+1,2):
            flux[-1,-1,0,j] = model.NewIntVar(0, N, f"flux_root_{0}_{j}")
            flux[-1,-1,2*self.__height,j] = model.NewIntVar(0, N, f"flux_root_{2*self.__height}_{j}")


        # -------------------------
        # conservation du flux
        # -------------------------
        out_root = []
        for i in range(2*self.__height+1):
            for j in range(2*self.__width+1):
                if (i+j)%2 == 0:
                    continue
                ns = self.__neighbors_mils(i,j)
                incoming = []
                outgoing = []

                for ni,nj in ns:
                    incoming.append(flux[ni,nj,i,j])
                    outgoing.append(flux[i,j,ni,nj])
                if (-1,-1,i,j) in flux:
                    incoming.append(flux[-1,-1,i,j])
                    out_root.append(flux[-1,-1,i,j])

                incoming_sum = sum(incoming)
                outgoing_sum = sum(outgoing)
                model.Add(incoming_sum - outgoing_sum == 1)

        model.Add(sum(out_root) == N-1)

        
        # -------------------------
        # solve
        # -------------------------

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15

        status = solver.Solve(model)
        if status == cp_model.INFEASIBLE:
            print("Insoluble !")
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            return [solver.Value(cell[index//self.__width,index%self.__width]) for index in range(self.__width*self.__height)]
        return False
