from .core import CWComplex, Cell
from typing import List


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
    pattern_list = pattern.boundary[len(pattern_links):]

    if len(pattern_list) != len(subcomplex):
        raise RuntimeError("Pattern matching failed")

    for pattern_cell, cell in zip(pattern_list, subcomplex):
        if pattern_cell.dimension != cell.dimension:
            raise RuntimeError(f"Pattern matching failed: dimensions mismatch "
                               f"{pattern_cell.label}({pattern_cell.dimension}) != {cell.label}({cell.dimension})")
        if pattern_cell.label != "Any" and pattern_cell.label != cell.label:
            raise RuntimeError(f"Pattern matching failed: label mismatch {pattern_cell.label} != {cell.label}")

    # pattern matched

    deletion_list = []
    target_to_destination = {}
    for destination_cell, p in zip(subcomplex, pattern_list):
        bindings = [
            b
            for b in p.coboundary
            if b.label == "bind"
        ]
        assert len(bindings) <= 1
        if len(bindings) == 1:
            bind = bindings[0]
            assert bind.dimension == p.dimension + 1
            # find target
            target = [b for b in bind.boundary if b.label not in ["bind", "nobind"] and b is not p]
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
        product_list = product.boundary[len(product_links):]
        create_list = [x for x in product_list if id(x) not in target_to_destination]

        for x in sorted(create_list, key=lambda x: x.dimension):  # sort is redundant if rules are well-written
            if x.dimension == 0:
                target_to_destination[id(x)] = c.create_cell(x.label)
            else:
                target_to_destination[id(x)] = c.create_cell(x.label, [
                    target_to_destination[id(b)]
                    for b in x.boundary
                ])

    # deletion
    for x in deletion_list:
        x.data.deleted = True
