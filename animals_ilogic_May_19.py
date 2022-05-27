from cwdb import *
from cwdb.ilogic import *


def main():
    c = CWComplex()

    robin = c.create_cell("robin")
    bird = c.create_cell("bird")
    animal = c.create_cell("animal")
    water = c.create_cell("water")
    liquid = c.create_cell("liquid")
    vertibrate = c.create_cell("vertibrate")

    animal_have_wings = c.create_cell("animal_have_wings")
    animal_flying = c.create_cell("animal_flying")

    is_1 = c.create_cell("is", [c["robin"], bird])
    c.create_cell("is", [robin, animal_have_wings])
    c.create_cell("is", [animal_have_wings, animal_flying])
    c.create_cell("is", [animal_flying, animal])
    is_2 = c.create_cell("is", [bird, vertibrate])
    c.create_cell("is", [vertibrate, animal])
    c.create_cell("is", [water, liquid])

    c.build_coboundary()

    print(get_truth_value(robin, animal, 10))

    print(get_truth_value(water, robin, 10))

    print(get_truth_value(water, liquid, 10))

    print(get_truth_value(water, water, 10))

    print(get_truth_value(bird, animal_have_wings), get_truth_value(animal_have_wings, bird))


if __name__ == '__main__':
    main()
