from typing import Dict, Hashable, List, Optional, Set, Tuple, Any

class Graph:
    """
    classe de graphe non orienté
    """

    __nodes:Dict[Hashable, Set[Hashable]]

    def __init__(self):
        self.__nodes = {}

    def add_node(self, name:Hashable):
        """
        name: nom du nœud
        ajoute un nœud au graphe
        """
        assert name not in self.__nodes
        self.__nodes[name] = set()
    
    def add_vertex(self, orig:Hashable, dest:Hashable):
        """
        orig: nom du nœud d'origine
        dest: nom du nœud de destination
        ajoute une arête entre orig et dest
        """
        assert orig != dest
        assert orig in self.__nodes
        assert dest in self.__nodes
        self.__nodes[orig].add(dest)
        self.__nodes[dest].add(orig)

    def clone(self) -> 'Graph':
        """
        renvoie une copie du graphe
        """
        g = Graph()
        for n in self.__nodes:
            g.__nodes[n] = self.__nodes[n].copy()
        return g
    
    def __del_orphan(self) -> bool:
        """
        supprime les nœuds orphelins (sans connexion)
        le graph étant non orienté, il n'y a pas de connexion retour à ajuster
        renvoie True s'il y avait au moins un nœud orphelin, False sinon
        """
        to_del = []
        for n in self.__nodes:
            if len(self.__nodes[n]) == 0:
                to_del.append(n)
        for n in to_del:
            del self.__nodes[n]
        return len(to_del) > 0
    
    def get_node_of_order_equal(self, n:int) -> Set[Hashable]:
        """
        n: ordre demandé
        renvoie les noms des nœuds d'ordre n
        """
        return {lab for lab in self.__nodes if len(self.__nodes[lab]) == n}

    def get_node_of_order_less(self, n:int) -> Set[Hashable]:
        """
        n: ordre demandé
        renvoie les noms des nœuds d'ordre <= n
        """
        return {lab for lab in self.__nodes if len(self.__nodes[lab]) <= n}

    def remove_node(self, label:Hashable):
        """
        label: nom du nœud à supprimer
        supprime un nœud en ajustant les connexions
        """
        assert label in self.__nodes
        for lab in self.__nodes[label]:
            self.__nodes[lab].discard(label)
        del self.__nodes[label]

    def remove_nodes(self, labels:List[Hashable]):
        """
        labels: liste des noms des nœuds à supprimer
        supprime les nœuds en ajustant les connexions
        """
        for lab in labels:
            self.remove_node(lab)
            
    def __del_single(self) -> bool:
        """supprime les nœuds d'ordre 1
        le graph étant non orienté, il faut ajuster les connexions des nœuds connectés
        renvoie True s'il y avait au moins un nœud d'ordre 1, False sinon
        """
        to_del = self.get_node_of_order(1)
        self.remove_nodes(to_del)
        return len(to_del) > 0

    def __has_cycle_destruc(self) -> bool:
        """
        renvoie True s'il y a un cycle dans le graphe, False sinon
        cette fonction casse le graphe
        """
        while len(to_del := self.get_node_of_order_less(1)) > 0:
            self.remove_nodes(to_del)
        return len(self.__nodes) > 0
    
    def has_cycle(self) -> bool:
        return self.clone().__has_cycle_destruc()

