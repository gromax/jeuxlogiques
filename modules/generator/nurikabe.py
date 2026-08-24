import random

WALL = "#"
EMPTY = "."

dirs = ((1,0),(-1,0),(0,1),(0,-1))

def neighbors(x:int, y:int, w:int, h:int):
    """
    x,y: cellule courante
    w,h: taille de la grille
    renvoie les 
    """
    for dx,dy in dirs:
        nx,ny = x+dx,y+dy
        if 0 <= nx < w and 0 <= ny < h:
            yield nx,ny

def generate_solution(w:int, h:int, islands:int=8, max_size:int=5):
    """
    w: largeur de la grille
    h: hauteur de la grille
    islands: nombre d'îles
    max_size: taille maximale d'une île
    """
    grid = [[WALL for _ in range(w)] for _ in range(h)]
    island_id = 1
    island_cells = {}

    attempts=0

    while island_id <= islands and attempts < 1000:
        attempts+=1
        x=random.randrange(w)
        y=random.randrange(h)

        if grid[y][x]!=WALL:
            continue

        size=random.randint(1,max_size)

        stack=[(x,y)]
        cells=[]

        while stack and len(cells)<size:
            cx,cy=stack.pop()

            if grid[cy][cx]!=WALL:
                continue

            grid[cy][cx]=island_id
            cells.append((cx,cy))

            neigh=list(neighbors(cx,cy,w,h))
            random.shuffle(neigh)

            for nx,ny in neigh:
                if grid[ny][nx]==WALL and random.random()<0.6:
                    stack.append((nx,ny))

        if len(cells)==0:
            continue

        island_cells[island_id]=cells
        island_id+=1

    return grid,island_cells


def place_clues(grid,islands):
    h=len(grid)
    w=len(grid[0])

    puzzle=[[EMPTY for _ in range(w)] for _ in range(h)]

    for i,cells in islands.items():

        size=len(cells)
        x,y=random.choice(cells)

        puzzle[y][x]=str(size)

    return puzzle


def encode_text(grid):

    rows=[]
    for r in grid:
        rows.append("".join(r))
    return "\n".join(rows)


def encode_simon_tatham(grid):

    s=""

    for row in grid:
        for c in row:
            if c==EMPTY:
                s+="."
            else:
                s+=c
        s+="/"

    return s[:-1]


def print_solution(sol):

    for row in sol:
        line=""
        for c in row:
            if c==WALL:
                line+="#"
            else:
                line+="o"
        print(line)


def generate_nurikabe(w=10,h=10,islands=10):

    sol,island_cells=generate_solution(w,h,islands)

    puzzle=place_clues(sol,island_cells)

    return sol,puzzle


if __name__=="__main__":

    sol,puzzle=generate_nurikabe(10,10,12)

    print("PUZZLE\n")
    print(encode_text(puzzle))

    print("\nSOLUTION\n")
    print_solution(sol)

    print("\nSTRING\n")
    print(encode_simon_tatham(puzzle))

