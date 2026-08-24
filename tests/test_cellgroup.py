from modules.primitives.cellgroup import CellGroup

class TestCellGroup:
    def test_zone_creation(self):
        z = CellGroup("a")
        assert z.tag == "a"

    def test_has_no_value_cell(self):
        z = CellGroup("a")
        z.add_coord(1,5)
        z.add_coord(2,5)
        z.add_coord(3,5)
        assert z.hasNoValueCell()
        z.init_possibles([1,2,3])
        assert not z.hasNoValueCell()
        z[1,5].remove_possibles([1,2,3])
        assert z.hasNoValueCell()

    def test_int_values(self):
        z = CellGroup("a")
        z.add_coord(1,5)
        z.add_coord(2,5)
        z.add_coord(3,5)
        z.init_possibles([1,2,3])
        z[1,5].value = 2
        z[2,5].value = 3
        assert z.int_values() == {2,3}
        z.clean_candidates()
        assert z.int_values() == {1,2,3}


