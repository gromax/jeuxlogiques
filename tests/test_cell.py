from modules.primitives.cell import Cell

class TestCell:
    def test_cell_creation(self):
        v = Cell(0,0)
        assert str(v) == '?'
        assert not v.known # False
        v.value = 3
        assert str(v) == '3'
        assert v.known
        v.reinit([1,2,3])
        assert str(v) == '?'
        assert not v.known
        assert len(v) == 3
        assert v.next()
        assert str(v) == '1'
        v.uncache()
        assert str(v) == '?'
        assert not v.known
        assert len(v) == 2