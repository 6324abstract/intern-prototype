from __future__ import annotations
import abc
from typing import Iterable, Set, Tuple, TypeVar

import numpy as np

T = TypeVar("T")
CellId = int


class ICell(abc.ABC):
    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        ...

    @property  # type: ignore[misc]
    @abc.abstractmethod
    def boundary(self) -> Tuple[ICell, ...]:
        ...

    @boundary.setter  # type: ignore[misc]
    @abc.abstractmethod
    def boundary(self, value: Iterable[ICell]):
        ...

    @property
    @abc.abstractmethod
    def label(self) -> str:
        ...

    @label.setter
    def label(self, value: str):
        ...

    @property
    @abc.abstractmethod
    def embedding(self) -> np.ndarray:
        ...

    @embedding.setter
    def embedding(self, value: np.ndarray):
        ...

    @property
    @abc.abstractmethod
    def data(self):
        ...

    @property
    @abc.abstractmethod
    def zero_cells(self) -> Set[ICell]:
        ...

    @property
    @abc.abstractmethod
    def id(self) -> CellId:
        ...

    def atoms(self, context: ICWComplex) -> Set[ICell]:
        return context.get_atoms_of(self)

    def atom(self, context: ICWComplex) -> ICell:
        atoms = context.get_atoms_of(self)
        if len(atoms) > 1:
            raise RuntimeError("1+ atoms")
        for atom in atoms:
            return atom
        raise RuntimeError("No atoms")

    def expansions(self, context: ICWComplex) -> Set[ICell]:
        return context.get_expansions_of(self)

    def expansion(self, context: ICWComplex) -> ICell:
        expansions = context.get_expansions_of(self)
        if len(expansions) > 1:
            raise RuntimeError("1+ expansions")
        for expansion in expansions:
            return expansion
        raise RuntimeError("No expansions")

    def coboundary(self, context: ICWComplex) -> Set[ICell]:
        return context.get_coboundary_of(self)

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class ICWComplex(abc.ABC):
    @abc.abstractmethod
    def get_layer_cells(self, layer: int) -> Set[ICell]:
        ...

    @abc.abstractmethod
    def link(self, a: ICell, b: ICell, label="", oriented=False) -> ICell:
        ...

    @abc.abstractmethod
    def create_atom_link(self, expansion: ICell, atom: ICell):
        ...

    @abc.abstractmethod
    def delete_atom_link(self, expansion: ICell, atom: ICell):
        ...

    @abc.abstractmethod
    def get_atoms_of(self, expansion: ICell) -> Set[ICell]:
        ...

    @abc.abstractmethod
    def get_expansions_of(self, atom: ICell) -> Set[ICell]:
        ...

    @abc.abstractmethod
    def create_cell(self, label: str, boundary=None) -> ICell:
        ...

    @abc.abstractmethod
    def delete_cell(self, cell: ICell):
        ...

    @abc.abstractmethod
    def get_cell_by_label(self, label: str) -> ICell:
        ...

    @abc.abstractmethod
    def get_coboundary_of(self, cell: ICell) -> Set[ICell]:
        ...

    @abc.abstractmethod
    def __contains__(self, item: ICell) -> bool:
        ...
