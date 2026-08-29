import sys

if len(sys.argv) <= 2:
    print("Vous disposez des commandes :")
    print('adjacent "<-- code -->"')
    print("bridges <-- code -->")
    print('camping "<-- code -->"')
    print('galaxy <-- code -->')
    print("kenken <-- code -->")
    print('loopy <-- code -->')
    print('nurikabe "<-- url ou code -->"')
    print('palisade <-- code -->')
    print('pearl <-- code -->')
    print("slant <-- code -->")
    print('techtonic "<-- code -->"')
    print('thermometres "<-- url ou code -->"')
    print('towers "<-- code -->"')
    print('tracks "<-- code -->"')
    print('undead "<-- code -->"')
    print('unequal "<-- code -->"')
    print('yingyang "<-- url ou code -->"')
    print('--------------')
    print('grid <-- filename -->')
    sys.exit(1)

com = sys.argv[1]
if com == "adjacent":
    from modules.jeux.adjacent import Adjacent
    a = Adjacent(tatham=sys.argv[2])
    print(a.tex())
elif com == "bridges" or com == "ponts":
    from modules.jeux.bridges import Bridges
    j = Bridges(tatham = sys.argv[2])
    print(j.tex())
elif com == "camping":
    from modules.jeux.camping import Camping
    grid = Camping(tatham=sys.argv[2])
    print(grid.tex())
elif com == "galaxy":
    from modules.jeux.galaxy import Galaxy
    g = Galaxy(tatham  = sys.argv[2])
    print(g.tex())
elif com == "kenken":
    from modules.jeux.kenken import Kenken
    k = Kenken(tatham = sys.argv[2])
    print(k.tex())
elif com == "loopy":
    from modules.jeux.loopy import Loopy
    t = Loopy(tatham = sys.argv[2])
    print(t.tex())
elif com == "nurikabe":
    from modules.jeux.nurikabe import Nurikabe
    chaine = sys.argv[2]
    if chaine.startswith("http"):
        url = chaine.split(":",1)[1].strip() if ":" in chaine else ""
        grid = Nurikabe(url=url)
    else:
        grid = Nurikabe(tatham=chaine)
    print(grid.tex())
elif com == "palisade":
    from modules.jeux.palisade import Palisade
    grid = Palisade(tatham = sys.argv[2])
    print(grid.tex())
elif com == "pearl":
    from modules.jeux.pearl import Game
    grid = Game(tatham = sys.argv[2])
    print(grid.tex())
elif com == "slant":
    from modules.jeux.slant import Slant
    s = Slant(tatham = sys.argv[2])
    print(s.tex())
elif com == "techtonic":
    from modules.jeux.techtonic import Techtonic
    t = Techtonic(tatham=sys.argv[2])
    print(t.tex())
elif com == "thermometres":
    from modules.jeux.thermometres import Thermometres
    chaine = sys.argv[2]
    if chaine.startswith("http"):
        url = chaine.split(":",1)[1].strip() if ":" in chaine else ""
        grid = Thermometres(url=url)
    else:
        grid = Thermometres(tatham=chaine)
    print(grid.tex())
elif com == "towers":
    from modules.jeux.towers import Towers
    chaine = sys.argv[2]
    t = Towers(tatham = chaine)
    print(t.tex())
elif com == "tracks":
    from modules.jeux.tracks import Game
    chaine = sys.argv[2]
    grid = Game(tatham = chaine)
    print(grid.tex())
elif com == "undead":
    from modules.jeux.undead import Undead
    u = Undead(tatham=sys.argv[2])
    print(u.tex())
elif com == "unequal":
    from modules.jeux.unequal import Unequal
    u = Unequal(tatham = sys.argv[2])
    print(u.tex())
elif com == "yingyang":
    from modules.jeux.yingyang import Yingyang
    chaine = sys.argv[2]
    if chaine.startswith("html"):
        url = chaine.split(":",1)[1].strip() if ":" in chaine else ""
        grid = Yingyang(url=url)
    else:
        grid = Yingyang(tatham=chaine)
    print(grid.tex())
elif com == "grid":
    from modules.primitives.zones import Zones
    filename = sys.argv[2]
    with open(filename, 'r') as f:
        lines = f.read()
    print(Zones.tag_to_id(lines))


else:
    print(f"Commande inconnue")
    sys.exit(1)

