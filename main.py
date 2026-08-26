import sys

if len(sys.argv) <= 2:
    print("Vous disposez des commandes :")
    print("kenken <-- code -->")
    print("bridges <-- code -->")
    print("slant <-- code -->")
    print('unequal "<-- code -->"')
    print('adjacent "<-- code -->"')
    print('towers "<-- code -->"')
    print('loopy <-- code -->')
    print('palisade <-- code -->')
    print('galaxy <-- code -->')
    print('yingyang "<-- url ou code -->"')
    print('nurikabe "<-- url ou code -->"')
    print('undead "<-- code -->"')
    print('techtonic "<-- code -->"')
    print('camping "<-- code -->"')
    print('thermometres "<-- url ou code -->"')
    print('grid <-- filename -->')
    sys.exit(1)

com = sys.argv[1]
if com == "kenken":
    from modules.jeux.kenken import Kenken
    k = Kenken(tatham = sys.argv[2])
    print(k.tex())
elif com == "bridges" or com == "ponts":
    from modules.jeux.bridges import Bridges
    j = Bridges(tatham = sys.argv[2])
    print(j.tex())
elif com == "slant":
    from modules.jeux.slant import Slant
    s = Slant(tatham = sys.argv[2])
    print(s.tex())
elif com == "unequal":
    from modules.jeux.unequal import Unequal
    u = Unequal(tatham = sys.argv[2])
    print(u.tex())
elif com == "adjacent":
    from modules.jeux.adjacent import Adjacent
    a = Adjacent(tatham=sys.argv[2])
    print(a.tex())
elif com == "towers":
    from modules.jeux.towers import Towers
    chaine = sys.argv[2]
    t = Towers(tatham = chaine)
    print(t.tex())
elif com == "loopy":
    from modules.jeux.loopy import Loopy
    t = Loopy(tatham = sys.argv[2])
    print(t.tex())
elif com == "palisade":
    from modules.jeux.palisade import Palisade
    t = Palisade(tatham = sys.argv[2])
    print(t.tex())
elif com == "galaxy":
    from modules.jeux.galaxy import Galaxy
    g = Galaxy(tatham  = sys.argv[2])
    print(g.tex())
elif com == "yingyang":
    from modules.jeux.yingyang import Yingyang
    chaine = sys.argv[2]
    if chaine.startswith("html"):
        url = chaine.split(":",1)[1].strip() if ":" in chaine else ""
        y = Yingyang(url=url)
    else:
        y = Yingyang(tatham=chaine)
    print(y.tex())
elif com == "undead":
    from modules.jeux.undead import Undead
    u = Undead(tatham=sys.argv[2])
    print(u.tex())
elif com == "camping":
    from modules.jeux.camping import Camping
    c = Camping(tatham=sys.argv[2])
    print(c.tex())
elif com == "techtonic":
    from modules.jeux.techtonic import Techtonic
    t = Techtonic(tatham=sys.argv[2])
    print(t.tex())
elif com == "nurikabe":
    from modules.jeux.nurikabe import Nurikabe
    chaine = sys.argv[2]
    if chaine.startswith("http"):
        n = Nurikabe(url=chaine)
    else:
        n = Nurikabe(tatham=chaine)
    print(n.tex())
elif com == "thermometres":
    from modules.jeux.thermometres import Thermometres
    chaine = sys.argv[2]
    if chaine.startswith("http"):
        j = Thermometres(url=chaine)
    else:
        j = Thermometres(tatham=chaine)
    print(j.tex())
elif com == "grid":
    from modules.primitives.zones import Zones
    filename = sys.argv[2]
    with open(filename, 'r') as f:
        lines = f.read()
    print(Zones.tag_to_id(lines))


else:
    print(f"Commande inconnue")
    sys.exit(1)

