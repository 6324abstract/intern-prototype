from typing import List, Set

from .interfaces import ICell as ICell
from .interfaces import ICWComplex


def get_extension_dfs(cell: ICell, visited: Set[ICell], c: ICWComplex) -> List[ICell]:
    result = [cell]
    visited.add(cell)
    for b in cell.coboundary(c):
        if b.boundary[1] is cell:
            if b.boundary[0] in visited:
                continue
            result.extend(get_extension_dfs(b.boundary[0], visited, c))
    return result


def get_extension(cell: ICell, c: ICWComplex) -> List[ICell]:
    assert cell.dimension == 0
    visited: Set[ICell] = set()
    return get_extension_dfs(cell, visited, c)


def get_intention_dfs(cell: ICell, visited: Set[ICell], c) -> List[ICell]:
    result: List[ICell] = [cell]
    visited.add(cell)
    for b in cell.coboundary(c):
        if b.boundary[0] is cell:
            if b.boundary[1] in visited:
                continue
            result.extend(get_intention_dfs(b.boundary[1], visited, c))
    return result


def get_intention(cell: ICell, c: ICWComplex) -> List[ICell]:
    assert cell.dimension == 0
    visited: Set[ICell] = set()
    return get_intention_dfs(cell, visited, c)


def get_truth_value(s: ICell, p: ICell, c: ICWComplex, k: int = 1):
    se = get_extension(s, c)
    si = set(get_intention(s, c))

    pe = set(get_extension(p, c))
    pi = get_intention(p, c)

    # positive evidence = W+ ???? ?
    po_half = len({id(x) for x in se if x in pe})

    po_another_half = len({id(x) for x in pi if x in si})

    negative_half = len(se) - po_half
    negative_another_half = len(pi) - po_another_half

    W = po_half + po_another_half + negative_another_half + negative_half
    W_plus = po_half + po_another_half

    return W_plus / W, W / (W + k)
