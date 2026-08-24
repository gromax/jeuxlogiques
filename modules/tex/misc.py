"""
fonctions tex utilitaires
"""
from typing import List, Tuple, Dict, Any, Union

def __filter_exclude_list(
        in_L:list,
        width:int,
        exclude:List[Union[int, Tuple[int,int]]],
        default:Any
    ) -> List[Any]:
    exclude_indexes = [item[0]*width + item[1] if type(item)==tuple else item for item in exclude]
    return [item if index not in exclude_indexes else default for index, item in enumerate(in_L)]

def __filter_exclude_dict(
        in_L:Dict[Tuple[int,int], Any],
        width:int,
        height:int,
        exclude:List[Union[int, Tuple[int,int]]],
        default:Any
    ) -> List[Any]:
    """
    in_L: dictionnaire (i,j) -> item
    width: largeur de la grille
    height: hauteur de la grille
    exclude: liste d'items à exclure (index ou (i,j))
    default: valeur par défaut si item absent
    """
    N = width*height
    ijs = [(index//width, index%width) for index in range(N)]
    exclude_ijs = [item if type(item)==tuple else (item//width, item%width) for item in exclude]
    return [in_L.get((i,j), default) if (i,j) not in exclude_ijs else default for i,j in ijs ]


def list_to_showList(width:int, height:int, in_L:Union[list, dict], **options) -> List[str]:
    """
    width: largeur de la grille
    height: hauteur de la grille
    in_L: liste ou dictionnaire des items à afficher
    options:
        size: taille des items dans le tex. si -1, pas mis dans tex
        symbol: fonction pour transformer un item en string
        default: valeur par défaut si item absent
        macroname: nom de la macro tex à utiliser (showList par défaut)
        cor: si True, le code est conditionné par \\ifthenelse{\\showCor=1}{...}{}
        exclude: liste d'items à exclure (index ou (i,j))
        addDims: liste de dimensions à ajouter aux arguments de la macro. Défaut []
    """
    assert set(options) <= {"size", "symbol", "default", "macroname", "cor", "exclude", "addDims"}
    if len(in_L) == 0:
        return []
    s = options.get('size',1)
    symbol = options.get('symbol', lambda item:str(item))
    default = options.get('default', '')
    macroname = options.get('macroname', 'showList')
    cor = options.get('cor', False)
    addDims = options.get('addDims', [])
    flat_L = []
    exclude:List[Union[int, Tuple[int,int]]] = options.get("exclude", [])

    if type(in_L) == list:
        flat_L = [symbol(item) for item in __filter_exclude_list(in_L,width,exclude,default)]
    else:
        flat_L = [symbol(item) for item in __filter_exclude_dict(in_L,width,height,exclude,default)]
    M = max(len(item) for item in flat_L)
    flat_sized_L = [" "*(M-len(item))+item for item in flat_L]
    out_L = [",".join(flat_sized_L[i:i+width])+',' for i in range(0, width*height, width)]
    out_L[-1] = out_L[-1][:-1] # suppression dernier ','
    output = []
    if cor:
        output.append("\\ifthenelse{\\showCor = 1}{")
    output.append("\\" + macroname + "{" + str(width) + "}{" + str(height) + "}{ {")
    output += out_L
    addDims_str = "{" + "}{".join(str(dim) for dim in addDims) +"}" if addDims else ""
    if s == -1:
        output.append("} }" + addDims_str)
    else:
        output.append("} }{ " + str(s) + " }" + addDims_str)
    if cor:
        output.append("}{ }")
    return output

def list_command(width:int, height:int, in_L:Union[list, dict], **options) -> List[str]:
    assert set(options) <= {"symbol", "default", "cor", "exclude", "varname", "commands"}
    if len(in_L) == 0:
        return []
    symbol = options.get('symbol', lambda item:str(item))
    default = options.get('default', '')
    cor = options.get('cor', False)
    var_name = options.get('varname','\\item')
    commands = options.get('commands', ["\\draw <coord> node[scale=1]{\\item};"])
    assert type(commands) == list
    coord_replacement = "({mod(\\index,"+str(width)+")},{int(\\index/"+str(width)+")})"
    for index in range(len(commands)):
        commands[index] = commands[index].replace("<coord>", coord_replacement)
    
    flat_L = []
    exclude:List[Union[int, Tuple[int,int]]] = options.get("exclude", [])

    if type(in_L) == list:
        flat_L = [symbol(item) for item in __filter_exclude_list(in_L,width,exclude,default)]
    else:
        flat_L = [symbol(item) for item in __filter_exclude_dict(in_L,width,height,exclude,default)]
    M = max(len(item) for item in flat_L)
    flat_sized_L = [" "*(M-len(item))+item for item in flat_L]
    out_L = [",".join(flat_sized_L[i:i+width])+',' for i in range(0, width*height, width)]
    out_L[-1] = out_L[-1][:-1] # suppression dernier ','

    output = []
    if cor:
        output.append("\\ifthenelse{\\showCor = 1}{")
    output.append("\\begin{scope}[shift={(.5," + str(height -.5) +")},yscale=-1]")
    output.append("\\foreach[count=\\index] " + var_name + " in {")
    output += out_L
    output.append("}{")
    output += commands
    output.append("}")
    output.appnd("\\end{scope}")
    if cor:
        output.append("}{ }")
    return output


def sideItems(width:int, height:int, top:List[Any], right:List[Any], bottom:List[Any], left:List[Any], **options) -> List[str]:
    assert set(options) <= {"symbol", "size"}
    symbol = options.get("symbol", lambda item:str(item))
    size = options.get("size", 1)
    t = ",".join(symbol(item) for item in top)
    r = ",".join(symbol(item) for item in right)
    b = ",".join(symbol(item) for item in bottom)
    l = ",".join(symbol(item) for item in left)
    return [
        "\\sideItems{"+str(width)+"}{"+str(height)+"}{ {",
        "{"+t+"},",
        "{"+b+"},",
        "{"+l+"},",
        "{"+r+"}",
        "} }{"+str(size)+"}"
    ]
