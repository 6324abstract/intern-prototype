import numpy as np

from cwdb import *
from cwdb.ilogic import *
from cwdb.query import query_boundary, query_boundary_and_resolve_ambiguity
from cwdb.rules import *


def main():
    c = CWComplex()

    robin = c.create_cell("robin")
    bird = c.create_cell("bird")
    animal = c.create_cell("animal")
    water = c.create_cell("water")
    liquid = c.create_cell("liquid")
    vertebrate = c.create_cell("vertebrate")

    animal_have_wings = c.create_cell("animal_have_wings")
    animal_flying = c.create_cell("animal_flying")

    is_1 = c.create_cell("is", [c["robin"], bird])
    c.create_cell("is", [robin, animal_have_wings])
    c.create_cell("is", [animal_have_wings, animal_flying])
    c.create_cell("is", [animal_flying, animal])
    is_2 = c.create_cell("is", [bird, vertebrate])
    c.create_cell("is", [vertebrate, animal])
    c.create_cell("is", [water, liquid])

    c.build_coboundary()
    for e in c.layers[1]:
        x, y = e.boundary[:2]
        e.data.embedding = np.array(get_truth_value(x, y))

    is_2_dup = c.create_cell("is", [bird, vertebrate])
    is_2_dup.data.embedding = np.array([0.5, 0.8])

    c.build_coboundary()

    query_boundary("is", [robin, bird])

    print(to_lang_representation(c))

    # revision_rule(is_2, is_2_dup)
    # choice_rule(is_2, is_2_dup)

    print(to_lang_representation(c))

    print(
        query_boundary_and_resolve_ambiguity(
            c, "is", [bird, vertebrate], ambiguity_resolution_rule=random_rule
        )
    )

    print(to_lang_representation(c))

    #  Generic ambiguity resolution rule interface:
    def ambiguity_resolution_rule(e1: Cell, e2: Cell) -> Cell:
        # PRE-CONDITIONS:
        assert e1.label == e2.label
        assert e1.boundary == e2.boundary
        ...
        # POST-CONDITION:
        # assert (e1.data.deleted xor e2.data.deleted) or (new_result and e1.data.deleted and e2.data.deleted)
        return e1


if __name__ == "__main__":
    main()
