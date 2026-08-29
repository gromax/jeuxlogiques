# Générateur de tex pour jeux logiques

Ce projet consiste à produire un fichier tex contenant des jeux logiques comme ceux de [Simon Tatham](https://www.chiark.greenend.org.uk/~sgtatham/puzzles/).

Le fichier tex contient une variable `showCor` qui permet de passer du fichier de correction au fichier de sujet.

## `main.py`

Le script **main** permet de tester un jeu individuellement. On pourra par exemple lancer une commande comme :

```
python.exe main.py tracks 8x8:lCc5zr9b,3,4,6,4,3,S5,2,2,2,3,S4,6,5,3,3,3
```

Ici, **tracks** fait partie des jeux de Simon Tatham. Le code donné ensuite est le code produit par le jeu (version exécutable, le code est différent en ligne)

Le script va décoder cette expression pour reconstruire le jeu et produire le tex correspondant ainsi que la correction.

```
python.exe main.py
```

Donnera la liste des commandes possibles.

## Production d'un fichier

Pour produire un fichier tex complet, on peut utiliser un fichier tex de commande comme celui ci :

```
# fichier exemple.txt
# tout ce qui suit # est un commentaire
# les lignes vides sont ignorées

TITLE=titre
AUTHOR=le nom de l'auteur
LHEAD=left head dans le tex
FOOT=pied de page

camping 8x8:daba_qhfd_ccc,2,0,1,2,1,3,0,3,2,2,1,2,0,2,2,1
pearl 12x8:nBaWcWWWeWWBeWWWfBfWWbWaBcWBWcWaBmBbBWaBWW
tracks 8x8:p6zsCa,3,2,1,6,4,3,S3,2,2,4,S2,2,2,5,5,2
```

Dans cet exemple, on produire un fichier `exemple.tex` avec le code tex pour les trois jeux proposés. Pour cela on utilise la commande :

```
python.exe fromfile.py exemple.txt
```

Chaque jeu est enfermé dans un bloc `minipage` et les `tikzpicture` ont un attribut `scale` permettant d'ajuster les tailles.

Charge à l'utilisateur ensuite de faire la mise en page, de compiler le tex une fois avec la correction (en mettant `\showCor = 1`) et une fois sans correction (en mettant `showCor = 0`)

## Générateurs en ligne

Quelques jeux utilisent un générateur en ligne : nurikabe, thermometre, yingyang.

Lors de l'execution de `fromfile.py`, le html est remplacé par un texte décrivant le jeu obtenu, à la façon des jeux de Simon Tatham.

