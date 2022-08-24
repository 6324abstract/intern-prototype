from cwdb import CWComplex
from cwdb.patched_context import PatchedContext


def test_context_layer():
    layer_0 = CWComplex()
    a = layer_0.create_cell("a")

    layer_1 = CWComplex()
    b = layer_1.create_cell("b")

    combo = PatchedContext(patch=layer_1, base=layer_0)
    combo.create_cell(label="ab", boundary=[a, b])

    assert len(layer_0.get_layer_cells(0)) == 1
    assert len(layer_1.get_layer_cells(0)) == 1
    assert len(combo.get_layer_cells(0)) == 2

    # coboundary depends on contexts
    assert len(a.coboundary(layer_0)) == 0
    assert len(a.coboundary(layer_1)) == 1

    assert len(layer_0.get_layer_cells(1)) == 0
    assert len(layer_1.get_layer_cells(1)) == 1
    assert len(combo.get_layer_cells(1)) == 1

    layer_0.link(a, a)
    combo.link(a, a)

    assert len(layer_0.get_layer_cells(1)) == 1
    assert len(layer_1.get_layer_cells(1)) == 1
    assert len(combo.get_layer_cells(1)) == 2

    layer_1.link(b, b)
    combo.link(b, b)

    assert len(layer_0.get_layer_cells(1)) == 1
    assert len(layer_1.get_layer_cells(1)) == 2
    assert len(combo.get_layer_cells(1)) == 3
