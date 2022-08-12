import pytest

from cwdb import Cell


def test_zero_cell_skeleton_of_zero_cell():
    a = Cell.from_label("a")
    assert len(a.zero_cells) == 1


def test_zero_cell_skeleton_of_two_cell():
    a = Cell.from_label("a")
    b = Cell.from_label("b")

    ab = Cell.from_boundary("ab", [a, b])
    assert len(ab.zero_cells) == 2


def test_zero_cell_skeleton_of_n_cell():
    a = Cell.from_label("a")
    b = Cell.from_label("b")
    c = Cell.from_label("c")
    d = Cell.from_label("d")

    ab = Cell.from_boundary("ab", [a, b])
    ab_wrap = Cell.from_boundary("ab_wrap", [ab])
    assert len(ab_wrap.zero_cells) == 2

    bc = Cell.from_boundary("bc", [b, c])
    abc = Cell.from_boundary("abc", [ab, bc])
    assert len(abc.zero_cells) == 3

    cd = Cell.from_boundary("cd", [c, d])
    abcd = Cell.from_boundary("abcd", [ab, bc, cd])
    assert len(abcd.zero_cells) == 4

    abc_d = Cell.from_boundary("abc_d", [abc, cd])
    assert len(abc_d.zero_cells) == 4


def test_self_link_of_zero_cell():
    a = Cell.from_label("a")
    link = Cell.from_boundary("link", [a])
    assert len(link.boundary) == 1
    assert len(link.zero_cells) == 1


def test_links_between_two_zero_cells():
    a = Cell.from_label("a")
    b = Cell.from_label("a")
    link = Cell.from_boundary("link", [a, b])
    assert len(link.boundary) == 2


def test_wrappers_are_allowed():
    cell = Cell.from_label("cell")
    for i in range(1, 10):
        wrapper = Cell.from_boundary(f"wrapper_{i}", [cell])
        assert len(wrapper.boundary) == 1
        assert len(wrapper.boundary) == 1
        assert wrapper.dimension == i
        cell = wrapper
