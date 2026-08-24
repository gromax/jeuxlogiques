from modules.primitives.graph import Graph

class TestGraph:
    def test_graph(self):
        g = Graph()
        g.add_node('a')
        g.add_node('b')
        g.add_node('c')
        g.add_vertex('a', 'b')
        g.add_vertex('b', 'c')
        assert g.get_node_of_order_equal(0) == set()
        assert g.get_node_of_order_equal(1) == {'a', 'c'}
        assert g.get_node_of_order_equal(2) == {'b'}
        assert g.has_cycle() == False
        g.add_vertex('c', 'a')
        assert g.has_cycle() == True

