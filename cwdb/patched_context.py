from typing import Set

from .interfaces import ICell, ICWComplex


class PatchedContext(ICWComplex):
    """
    The patch context preserves constant `self.base` complex from alternations
    by reflecting all the changes in `self.patch`
    """

    def __init__(self, patch: ICWComplex, base: ICWComplex):
        self.patch = patch
        self.base = base

    def get_layer_cells(self, layer: int) -> Set[ICell]:
        return self.patch.get_layer_cells(layer) | self.base.get_layer_cells(layer)

    def link(self, a: ICell, b: ICell, label="", oriented=False) -> ICell:
        # check if link exists in base
        for c in self.base.get_layer_cells(1):
            if c.label == label and (
                a == c.boundary[0]
                and b == c.boundary[1]
                or (not oriented and a == c.boundary[1] and b == c.boundary[0])
            ):
                return c
        # if not link found in base context, create in patch
        return self.patch.link(a, b, label, oriented)

    def create_atom_link(self, expansion: ICell, atom: ICell):
        self.patch.create_atom_link(expansion=expansion, atom=atom)

    def get_atoms_of(self, expansion: ICell) -> Set[ICell]:
        return self.patch.get_atoms_of(expansion) | self.base.get_atoms_of(expansion)

    def get_expansions_of(self, atom: ICell) -> Set[ICell]:
        return self.patch.get_expansions_of(atom) | self.base.get_expansions_of(atom)

    def create_cell(self, label: str, boundary=None) -> ICell:
        assert all(b in self for b in boundary)
        return self.patch.create_cell(label=label, boundary=boundary)

    def delete_cell(self, cell: ICell):
        if cell in self.base:
            raise NotImplementedError(
                "Shadowing of cells from base complex is not implemented"
            )
        self.patch.delete_cell(cell)

    def delete_atom_link(self, expansion: ICell, atom: ICell):
        if atom in self.base.get_atoms_of(expansion):
            raise NotImplementedError(
                "Shadowing of atomisation from base complex is not implemented"
            )
        self.patch.delete_atom_link(expansion=expansion, atom=atom)

    def get_cell_by_label(self, label: str) -> ICell:
        try:
            return self.patch.get_cell_by_label(label)
        except KeyError:
            return self.base.get_cell_by_label(label)

    def get_coboundary_of(self, cell: ICell) -> Set[ICell]:
        return self.patch.get_coboundary_of(cell) | self.base.get_coboundary_of(cell)

    def __contains__(self, item: ICell) -> bool:
        return item in self.patch or item in self.base
