from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

import numpy as np

from .interfaces import CellId, ICell, ICWComplex


@dataclass
class Data:
    """Flexible mutable smth"""

    label: str
    zero_cells: Set[ICell] = field(default_factory=set, repr=False)
    deleted: bool = False
    embedding: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    task_implementation: Optional[Callable] = None


class Cell(ICell):
    def __init__(self, *, dimension: int, data: Data, boundary: Tuple[ICell, ...] = ()):
        self.__boundary = tuple(boundary)
        self.__dimension = dimension
        self._data = data

    @property
    def dimension(self) -> int:
        return self.__dimension

    @property
    def boundary(self) -> Tuple[ICell, ...]:
        return self.__boundary

    @boundary.setter
    def boundary(self, value: List[ICell]):
        self.check_boundary_connectedness(value)
        self.check_boundary_is_minimal(value)
        self.__boundary = tuple(value)

    @property
    def data(self) -> Data:
        return self._data

    @property
    def embedding(self) -> np.ndarray:
        return self.data.embedding

    @embedding.setter
    def embedding(self, value: np.ndarray):
        self.data.embedding = value

    @property
    def label(self) -> str:
        result = self.data.label
        if self.data.deleted:
            result = "[DELETED] " + result
        return result

    @label.setter
    def label(self, value: str):
        self.data.label = value

    @property
    def zero_cells(self) -> Set[ICell]:
        return self.data.zero_cells

    @classmethod
    def from_label(cls, label: str) -> Cell:
        cell = cls(data=Data(label=label), dimension=0)
        cell.data.zero_cells = {cell}
        return cell

    @classmethod
    def from_boundary(cls, label: str, boundary: List[ICell]) -> ICell:
        assert len(boundary) != 0
        cell = cls(
            data=Data(label=label),
            dimension=max((x.dimension for x in boundary), default=-1) + 1,
            boundary=tuple(boundary),
        )
        cell.data.zero_cells = {c for x in boundary for c in x.zero_cells}

        if cell.dimension == 1:
            if len(boundary) > 2:
                raise RuntimeError("1-cell cannot be connected with 3 or more 0-cells")
            return cell

        cls.check_boundary_connectedness(boundary)
        cls.check_boundary_is_minimal(boundary)

        return cell

    @classmethod
    def check_boundary_connectedness(cls, boundary):
        # check that closure is connected
        from itertools import chain

        from .utils import DSU

        dsu = DSU(chain(*(b.zero_cells for b in boundary), boundary))
        for b in boundary:
            for z in b.zero_cells:
                dsu.merge(b, z)
        p1 = dsu.find(boundary[0])
        for b in boundary[1:]:
            if p1 != dsu.find(b):
                raise RuntimeError(f"Closure is not connected '{b.label}'")

    @classmethod
    def check_boundary_is_minimal(cls, boundary: List[ICell]):
        # colors of complex cells by boundary
        cell_colours: Dict[ICell, ICell] = {}

        def paint(el: ICell, color: ICell):
            if el in boundary and el in cell_colours:
                existing_color = cell_colours[el]
                if existing_color != color:
                    small = existing_color
                    big = color
                    if big.dimension < small.dimension:
                        big, small = small, big
                    raise RuntimeError(
                        f"Boundary is not minimal: '{small.label}'"
                        f" is contained in '{big.label}'"
                    )
            cell_colours[el] = color
            for b in el.boundary:
                paint(b, color)

        for b in boundary:
            paint(b, b)

    @property
    def id(self) -> CellId:
        return id(self)

    def __repr__(self):
        if self.dimension == 0:
            return f'Cell("{self.label}", embedding={self.embedding})'
        else:
            return (
                f'Cell("{self.label}", embedding={self.embedding}'
                f", dimension={self.dimension}"
                ", boundary=[" + ", ".join(f'"{b.label}"' for b in self.boundary) + "]"
                ")"
            )

    def to_tree(self, prefix=None, is_last=False, max_depth=None, depth=0):
        if max_depth is not None and depth > max_depth:
            return ""
        if prefix is None:
            result = self.label + f" {self.embedding}\n"
            prefix = ""
        else:
            if is_last:
                char = "└── "
            else:
                char = "├── "
            result = prefix + char + self.label + "\n"
            if is_last:
                prefix += "    "
            else:
                prefix += "│   "
        for i, b in enumerate(self.boundary):
            is_last = i == len(self.boundary) - 1
            result += b.to_tree(
                prefix, max_depth=max_depth, depth=depth + 1, is_last=is_last
            )
        return result

    def __str__(self):
        return self.to_tree()


class CWComplex(ICWComplex):
    _layers: List[Set[ICell]]
    _atoms_of: Dict[CellId, Set[ICell]]
    _extensions_of: Dict[CellId, Set[ICell]]
    _coboundary_of: Dict[CellId, Set[ICell]]

    def __init__(self):
        self._layers = []
        self._atoms_of = defaultdict(set)
        self._extensions_of = defaultdict(set)
        self._coboundary_of = defaultdict(set)

    def get_layer_cells(self, layer: int) -> Set[ICell]:
        if len(self._layers) > layer:
            return self._layers[layer]
        return set()

    def get_atoms_of(self, expansion: ICell) -> Set[ICell]:
        return self._atoms_of[expansion.id]

    def get_expansions_of(self, atom: ICell) -> Set[ICell]:
        return self._extensions_of[atom.id]

    def delete_cell(self, cell: ICell):
        raise NotImplementedError()

    def delete_atom_link(self, expansion: ICell, atom: ICell):
        raise NotImplementedError()

    def get_cell_by_label(self, label: str) -> ICell:
        for layer in self._layers:
            for cell in layer:
                if cell.label == label:
                    return cell
        raise KeyError(f"label={label}")

    def get_coboundary_of(self, cell: ICell) -> Set[ICell]:
        # FIXME: avoid recalc
        self._build_coboundary()
        return self._coboundary_of[cell.id]

    def link(self, a: ICell, b: ICell, label="", oriented=False) -> ICell:
        assert a.dimension == 0
        assert b.dimension == 0

        self._ensure_level_exists(1)

        for c in self._layers[1]:
            if c.label == label and (
                a == c.boundary[0]
                and b == c.boundary[1]
                or (not oriented and a == c.boundary[1] and b == c.boundary[0])
            ):
                return c
        return self.create_cell(label, [a, b])

    def create_atom_link(self, expansion: ICell, atom: ICell):
        assert expansion.dimension >= 1
        assert atom.dimension == 0
        assert atom not in self._atoms_of[expansion.id]
        self._atoms_of[expansion.id].add(atom)
        self._extensions_of[atom.id].add(expansion)

    def create_cell(self, label: str, boundary=None) -> ICell:
        if boundary:
            cell = Cell.from_boundary(label, boundary=boundary)
        else:
            cell = Cell.from_label(label)

        self._ensure_level_exists(cell.dimension)
        self._layers[cell.dimension].add(cell)

        return cell

    def _ensure_level_exists(self, dimension):
        while dimension >= len(self._layers):
            self._layers.append(set())

    def _build_coboundary(self):
        self._clear_coboundary()
        for cell in self._layers[0]:
            self._coboundary_of[cell.id] = set()
        for layer in self._layers[1:]:
            for cell in layer:
                if cell.data.deleted:  # skip deleted
                    continue
                for b in cell.boundary:
                    if b.data.deleted:  # skip deleted
                        continue
                    self._coboundary_of[b.id].add(cell)

    def _clear_coboundary(self):
        self._coboundary_of = defaultdict(set)

    def __contains__(self, item: ICell) -> bool:
        if len(self._layers) > item.dimension:
            return item in self._layers[item.dimension]
        return False
