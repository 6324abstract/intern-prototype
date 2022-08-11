from typing import List

import numpy as np

from .core import Cell, CWComplex


def apply_rule(c: CWComplex, rule: Cell, subcomplex: List[Cell]):
    # pattern matching

    cb = rule.coboundary
    pattern_links = [x for x in cb if x.label == "pattern_scaffold"]
    # sanity check

    assert len(pattern_links) > 0
    assert len(pattern_links) == len([x for x in subcomplex if x.dimension == 0])

    assert len(pattern_links[0].coboundary) == 1

    pattern = pattern_links[0].coboundary[0]
    assert pattern.label == "pattern"
    assert len(pattern.boundary) > len(pattern_links)
    pattern_list = pattern.boundary[len(pattern_links) :]

    if len(pattern_list) != len(subcomplex):
        raise RuntimeError("Pattern matching failed")

    for pattern_cell, cell in zip(pattern_list, subcomplex):
        if pattern_cell.dimension != cell.dimension:
            raise RuntimeError(
                f"Pattern matching failed: dimensions mismatch "
                f"{pattern_cell.label}({pattern_cell.dimension}) "
                f"!= {cell.label}({cell.dimension})"
            )
        if pattern_cell.label != "Any" and pattern_cell.label != cell.label:
            raise RuntimeError(
                f"Pattern matching failed: label mismatch {pattern_cell.label} "
                f"!= {cell.label}"
            )

    # pattern matched

    deletion_list = []
    target_to_destination = {}
    for destination_cell, p in zip(subcomplex, pattern_list):
        bindings = [b for b in p.coboundary if b.label == "bind"]
        assert len(bindings) <= 1
        if len(bindings) == 1:
            bind = bindings[0]
            assert bind.dimension == p.dimension + 1
            # find target
            target = [
                b
                for b in bind.boundary
                if b.label not in ["bind", "nobind"] and b is not p
            ]
            assert len(target) == 1
            target = target[0]
            target_to_destination[id(target)] = destination_cell
        else:
            deletion_list.append(destination_cell)

    product_links = [x for x in cb if x.label == "product_scaffold"]

    if product_links:
        assert len(product_links[0].coboundary) == 1
        product = product_links[0].coboundary[0]
        assert product.label == "product"
        for pl in product_links[1:]:
            assert pl.coboundary == [product]
        product_list = product.boundary[len(product_links) :]
        create_list = [x for x in product_list if id(x) not in target_to_destination]

        for x in sorted(
            create_list, key=lambda x: x.dimension
        ):  # sort is redundant if rules are well-written
            if x.dimension == 0:
                target_to_destination[id(x)] = c.create_cell(x.label)
            else:
                target_to_destination[id(x)] = c.create_cell(
                    x.label, [target_to_destination[id(b)] for b in x.boundary]
                )

    # deletion
    for x in deletion_list:
        x.data.deleted = True


def revision_rule(c: CWComplex, e1: Cell, e2: Cell) -> Cell:
    assert e1.label == e2.label
    assert e1.boundary == e2.boundary
    f1, c1 = e1.embedding
    f2, c2 = e2.embedding
    f3 = (f1 * c1 * (1 - c2) + f2 * c2 * (1 - c1)) / (c1 * (1 - c2) + c2 * (1 - c1))
    c3 = (c1 * (1 - c2) + c2 * (1 - c1)) / (
        (c1 * (1 - c2) + c2 * (1 - c1)) + (1 - c1) * (1 - c2)
    )

    result = c.create_cell(e1.label, e1.boundary)
    result.data.embedding = np.array([f3, c3])
    e1.data.deleted = True
    e2.data.deleted = True
    return result


def choice_rule(c: CWComplex, e1: Cell, e2: Cell) -> Cell:
    assert e1.label == e2.label
    assert e1.boundary == e2.boundary
    f1, c1 = e1.embedding
    f2, c2 = e2.embedding
    if c1 > c2:
        e1, e2 = e2, e1
    e1.data.deleted = True
    return e2


def random_rule(c: CWComplex, e1: Cell, e2: Cell) -> Cell:
    assert e1.label == e2.label
    assert e1.boundary == e2.boundary
    if np.random.random() > 0.5:
        rule = choice_rule
    else:
        rule = revision_rule
    return rule(c, e1, e2)
