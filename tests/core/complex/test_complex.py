import pytest

from cwdb import CWComplex


def test_complex_construction():
    CWComplex()


def test_create_cells():
    cw = CWComplex()
    # 0-d
    a = cw.create_cell("a")
    b = cw.create_cell("b")
    # 1d
    cw.create_cell("ab", [a, b])

    assert len(cw.get_layer_cells(0)) == 2
    assert len(cw.get_layer_cells(1)) == 1


def test_create_links():
    cw = CWComplex()
    a = cw.create_cell("a")
    b = cw.create_cell("b")
    cw.link(a, b)

    assert len(cw.get_layer_cells(0)) == 2
    assert len(cw.get_layer_cells(1)) == 1

    # Get or create link does not create link if
    # it's already present in complex
    cw.link(a, b)
    assert len(cw.get_layer_cells(1)) == 1

    # The order doesn't matter
    cw.link(b, a)
    assert len(cw.get_layer_cells(1)) == 1

    # Unless oriented is provided
    cw.link(b, a, oriented=True)
    assert len(cw.get_layer_cells(1)) == 2

    # Or the label is different
    cw.link(a, b, label="x")
    cw.link(a, b, label="y")
    assert len(cw.get_layer_cells(1)) == 4


def test_get_cell_by_label():
    cw = CWComplex()
    a1 = cw.create_cell("a")
    a2 = cw.create_cell("a")
    cw.create_cell("b")

    assert cw.get_cell_by_label("a") in [a1, a2]


def test_atomisation():
    cw = CWComplex()
    a = cw.create_cell("a")
    b = cw.create_cell("b")
    ab_atom = cw.create_cell("ab_atom")
    ab = cw.create_cell("ab", [a, b])
    cw.create_atom_link(expansion=ab, atom=ab_atom)

    assert ab_atom.expansions(cw) == {ab}
    assert ab.atoms(cw) == {ab_atom}

    with pytest.raises(AssertionError):
        cw.create_atom_link(expansion=ab, atom=ab_atom)


def test_multiple_atomisations():
    cw = CWComplex()
    a = cw.create_cell("a")
    b = cw.create_cell("b")
    ab_atom1 = cw.create_cell("ab_atom1")
    ab_atom2 = cw.create_cell("ab_atom2")
    ab = cw.create_cell("ab", [a, b])
    cw.create_atom_link(expansion=ab, atom=ab_atom1)
    cw.create_atom_link(expansion=ab, atom=ab_atom2)

    assert ab_atom1.expansions(cw) == {ab}
    assert ab_atom2.expansions(cw) == {ab}
    assert ab.atoms(cw) == {ab_atom1, ab_atom2}

    with pytest.raises(RuntimeError, match=r"1\+ atoms"):
        _ = ab.atom(cw)


def test_coboundary():
    cw = CWComplex()
    a = cw.create_cell("a")
    b = cw.create_cell("b")
    c = cw.create_cell("c")
    ab = cw.create_cell("ab", [a, b])
    assert a.coboundary(cw) == {ab}
    assert b.coboundary(cw) == {ab}
    assert c.coboundary(cw) == set()


@pytest.mark.skip(reason="Cell deletion is not implemented at complex level")
def test_zero_cell_deletion():
    pass


@pytest.mark.skip(reason="Cell deletion is not implemented at complex level")
def test_use_of_deleted_cell_raises():
    pass
