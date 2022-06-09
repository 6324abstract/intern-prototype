from cwdb import (
    CWComplex,
    Cell,
    to_lang_representation
)
from cwdb.rules import apply_rule


def define_rule(c: CWComplex) -> Cell:
    Rule = c.create_cell('ImplySusbtitutionRule')

    P1 = c.create_cell('Any')
    P2 = c.create_cell('Any')
    C = c.create_cell('Any')
    is_1 = c.create_cell('is', [P1, P2])
    is_2 = c.create_cell('is', [P2, C])

    r_P1 = c.create_cell('Any')
    r_P2 = c.create_cell('Any')
    r_C = c.create_cell('Any')
    r_is_1 = c.create_cell('is', [r_P1, r_P2])
    r_is_2 = c.create_cell('is', [r_P2, r_C])
    r_is_3 = c.create_cell('is', [r_P1, r_C])

    b_1 = c.create_cell('bind', [P1, r_P1])
    b_2 = c.create_cell('bind', [P2, r_P2])
    b_3 = c.create_cell('bind', [C, r_C])
    b_4 = c.create_cell('bind', [is_1, b_2, r_is_1, b_1])
    b_5 = c.create_cell('bind', [is_2, b_3, r_is_2, b_2])

    _1 = c.create_cell('pattern_scaffold', [Rule, P1])
    _2 = c.create_cell('pattern_scaffold', [Rule, P2])
    _3 = c.create_cell('pattern_scaffold', [Rule, C])

    Pattern = c.create_cell('pattern', [_1, _2, _3, P1, P2, C, is_1, is_2])

    _4 = c.create_cell('product_scaffold', [Rule, r_P1])
    _5 = c.create_cell('product_scaffold', [Rule, r_P2])
    _6 = c.create_cell('product_scaffold', [Rule, r_C])

    Product = c.create_cell('product', [_4, _5, _6, r_is_3])

    #
    # A = c.create_cell('A')
    # B = c.create_cell('B')
    # D = c.create_cell('D')
    # c_is_1 = c.create_cell('is', [A,B])
    # c_is_2 = c.create_cell('is', [B,D])

    return Rule


def define_rule_2(c: CWComplex) -> Cell:
    Rule = c.create_cell('Rule2')

    P1 = c.create_cell('Any')
    r_P1 = c.create_cell('Any')
    b_1 = c.create_cell('bind', [P1, r_P1])

    r_P2 = c.create_cell('Foo')
    r_produced = c.create_cell('produced', [r_P1, r_P2])

    _1 = c.create_cell('pattern_scaffold', [Rule, P1])

    Pattern = c.create_cell('pattern', [_1, P1])

    _4 = c.create_cell('product_scaffold', [Rule, r_P1])
    _5 = c.create_cell('product_scaffold', [Rule, r_P2])

    Product = c.create_cell('product', [_4, _5, r_P2, r_produced])

    return Rule


def define_rule_3(c: CWComplex) -> Cell:
    Rule = c.create_cell('Rule3')

    P1 = c.create_cell('Any')
    P2 = c.create_cell('Foo')
    produced = c.create_cell('produced', [P1, P2])

    r_P1 = c.create_cell('Any')
    b_1 = c.create_cell('bind', [P1, r_P1])

    _1 = c.create_cell('pattern_scaffold', [Rule, P1])
    _2 = c.create_cell('pattern_scaffold', [Rule, P2])

    Pattern = c.create_cell('pattern', [_1, _2, P1, P2, produced])

    _5 = c.create_cell('product_scaffold', [Rule, r_P1])

    Product = c.create_cell('product', [_5])

    return Rule


def show_diff(repr_1: str, repr_2: str, changes_only=True):
    import difflib
    diff = difflib.ndiff(repr_1.split("\n"), repr_2.split("\n"))
    if changes_only:
        diff = (line for line in diff if not line.startswith("  ") and not line.startswith("? ") )
    print('\n'.join(diff))


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

    Rule = define_rule(c)

    c.build_coboundary()

    lang_repr_1_before = to_lang_representation(c)
    apply_rule(c, Rule, [robin, bird, vertebrate, is_1, is_2])
    lang_repr_1_after = to_lang_representation(c)

    print("Rule 1 application:")
    show_diff(lang_repr_1_before, lang_repr_1_after)
    print()
    print()

    Rule2 = define_rule_2(c)
    c.build_coboundary()

    lang_repr_2_before = to_lang_representation(c)
    apply_rule(c, Rule2, [robin])
    lang_repr_2_after = to_lang_representation(c)

    print("Rule 2 application:")
    show_diff(lang_repr_2_before, lang_repr_2_after)
    print()
    print()

    Rule2_inv = define_rule_3(c)
    c.build_coboundary()

    Foo, produced = [(prod.boundary[1], prod) for prod in robin.coboundary if prod.label == "produced"][0]

    lang_repr_3_before = to_lang_representation(c)
    apply_rule(c, Rule2_inv, [robin, Foo, produced])
    lang_repr_3_after = to_lang_representation(c)
    print("Rule 3 application:")
    show_diff(lang_repr_3_before, lang_repr_3_after, changes_only=True)
    print()
    print()



if __name__ == '__main__':
    main()
