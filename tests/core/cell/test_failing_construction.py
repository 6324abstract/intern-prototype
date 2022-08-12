import pytest

from cwdb import Cell


def test_empty_links_creation_raises():
    with pytest.raises(AssertionError):
        Cell.from_boundary("x", [])


def test_links_between_more_than_two_zero_cells_raises():
    with pytest.raises(
        RuntimeError, match="1-cell cannot be connected with 3 or more 0-cells"
    ):
        Cell.from_boundary(
            "abc", [Cell.from_label("a"), Cell.from_label("b"), Cell.from_label("c")]
        )


def test_disjount_boundary_raises():
    ab = Cell.from_boundary("ab", [Cell.from_label("a"), Cell.from_label("b")])
    cd = Cell.from_boundary("cd", [Cell.from_label("c"), Cell.from_label("d")])

    with pytest.raises(RuntimeError):
        Cell.from_boundary("x", [ab, cd])


@pytest.mark.skip("Check is not implemented")
def test_redundant_boundary_raises():
    a = Cell.from_label("a")
    b = Cell.from_label("b")
    ab = Cell.from_boundary("ab", [a, b])

    with pytest.raises(RuntimeError):
        Cell.from_boundary("x", [ab, a])
