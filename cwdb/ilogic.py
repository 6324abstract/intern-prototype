from .core import Cell
from typing import Set, List


def get_extension_dfs(cell: Cell, visited: Set[Cell]) -> List[Cell]:
    result = [cell]
    visited.add(cell)
    for b in cell.coboundary:
        if b.boundary[1] is cell:
            if b.boundary[0] in visited:
                continue
            result.extend(get_extension_dfs(b.boundary[0], visited))
    return result


def get_extension(cell: Cell) -> List[Cell]:
    assert cell.dimension == 0
    visited = set()
    return get_extension_dfs(cell, visited)


def get_intention_dfs(cell: Cell, visited: Set[Cell]) -> List[Cell]:
    result = [cell]
    visited.add(cell)
    for b in cell.coboundary:
        if b.boundary[0] is cell:
            if b.boundary[1] in visited:
                continue
            result.extend(get_intention_dfs(b.boundary[1], visited))
    return result


def get_intention(cell: Cell) -> List[Cell]:
    assert cell.dimension == 0
    visited = set()
    return get_intention_dfs(cell, visited)


def get_truth_value(s: Cell, p: Cell, k: int = 1):
    se = get_extension(s)
    si = set(get_intention(s))

    pe = set(get_extension(p))
    pi = get_intention(p)

    # positive evidence = W+ ???? ?
    po_half = len({
        id(x)
        for x in se
        if x in pe
    })

    po_another_half = len({
        id(x)
        for x in pi
        if x in si
    })

    negative_half = len(se) - po_half
    negative_another_half = len(pi) - po_another_half

    W = po_half + po_another_half + negative_another_half + negative_half
    W_plus = po_half + po_another_half

    return W_plus, W, W_plus / W, W / (W + k)