import re

from .core import Cell


def to_lang_representation(cplx) -> str:
    cell2name = {}
    name2count = {}

    def escape_label(label):
        return re.sub(r"([\\\'])", r"\\\1", label)

    def get_name(c: Cell) -> str:
        if id(c) in cell2name:
            return cell2name[id(c)]
        if c.dimension == 1 and c.label == "":
            prefix = "one_cell"
        else:
            prefix = ""

        name = prefix + re.sub(r"\s", "_", re.sub("[^0-9A-Za-z_ ]", "", c.label))
        if name in name2count:
            name2count[name] += 1
            name += "_" + str(name2count[name])
        else:
            name2count[name] = 0
        cell2name[id(c)] = name
        return name

    result = ""
    for cell in cplx.layers[0]:
        result += get_name(cell) + ": '" + escape_label(cell.label) + "'\n"

    for cell in cplx.layers[1]:
        result += get_name(cell) + ": " + get_name(cell.boundary[0])
        result += "-" if cell.label == "" else "->"
        result += get_name(cell.boundary[1]) + ": '" + escape_label(cell.label) + "'\n"

    for layer in cplx.layers[2:]:
        for cell in layer:
            result += get_name(cell) + ": ["
            for b in cell.boundary:
                result += get_name(b) + ", "
            result = result.rstrip(", ")
            result += "]: '" + escape_label(cell.label) + "'\n"

    for a in cplx.atomisations:
        result += f"{get_name(a.closure_of)} ~> {get_name(a.atom)}\n"

    return result
