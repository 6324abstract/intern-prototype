from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Set, Tuple

import numpy as np


@dataclass
class DSUData:
    """Disjoint set union"""

    size: Optional[int] = None
    parent: Optional[Cell] = None


@dataclass
class Data:
    """Flexible mutable smth"""

    label: str
    dsu: DSUData = field(default=DSUData, repr=False)
    zero_cells: Set[Cell] = field(default_factory=set, repr=False)
    coboundary: List[Cell] = field(default=None, repr=False)
    deleted: bool = False
    embedding: np.ndarray = field(default_factory=lambda: np.empty(shape=(0,)))
    task_implementation: Optional[Callable] = None
    atom_of: Set[Cell] = field(default_factory=set, repr=False)
    atoms: Set[Cell] = field(default_factory=set, repr=False)


@dataclass(frozen=True)
class Cell:
    dimension: int = -1
    data: Data = field(default=None, compare=False, hash=False)
    boundary: Tuple[Cell] = field(default_factory=tuple)

    @property
    def atoms(self) -> Set[Cell]:
        assert self.dimension >= 1
        return self.data.atoms

    @property
    def atom_of(self) -> Set[Cell]:
        assert self.dimension == 0
        return self.data.atom_of

    @property
    def atom(self) -> Optional[Cell]:
        assert self.dimension >= 1
        n = len(self.data.atoms)
        if n > 1:
            raise RuntimeError(f"Cell {self} has {n} atoms")
        for atom in self.data.atoms:
            return atom

    @property
    def self_or_atom(self) -> Optional[Cell]:
        if self.dimension == 0:
            return self
        return self.atom

    @property
    def self_or_the_only_atom_for(self) -> Optional[Cell]:
        if self.dimension == 0:
            return self.the_only_atom_of
        return self

    @property
    def the_only_atom_of(self) -> Optional[Cell]:
        assert self.dimension == 0
        n = len(self.data.atom_of)
        if n > 1:
            raise RuntimeError(f"Cell {self} has {n} atomisations")
        for atomisation in self.data.atom_of:
            return atomisation

    @property
    def embedding(self) -> np.ndarray:
        return self.data.embedding

    @property
    def label(self) -> str:
        result = self.data.label
        if self.data.deleted:
            result = "[DELETED] " + result
        return result

    @property
    def coboundary(self) -> List[Cell]:
        if self.data.coboundary is None:
            raise RuntimeError("Co-boundary is not built")
        return self.data.coboundary

    @property
    def zero_cells(self) -> Set[Cell]:
        return self.data.zero_cells

    @classmethod
    def from_label(cls, label: str) -> Cell:
        cell = cls(data=Data(label=label), dimension=0)
        cell.data.zero_cells = {cell}
        return cell

    @classmethod
    def from_boundary(cls, label: str, boundary: List[Cell]) -> Cell:
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

        # check that closure is connected
        for b in cell.zero_cells:
            b.data.dsu.parent = b
            b.data.dsu.size = 0

        for b in boundary:
            b.data.dsu.parent = b
            b.data.dsu.size = 0
            for z in b.zero_cells:
                merge(b, z)

        p1 = find(boundary[0])

        for b in boundary[1:]:
            p = find(b)
            if p1 is not p:
                raise RuntimeError(f"Closure is not connected '{b.label}'")
            p1 = p

        for b in boundary:
            b.data.dsu.parent = None
            b.data.dsu.size = -1

        for b in cell.data.zero_cells:
            b.data.dsu.parent = None
            b.data.dsu.size = -1

        return cell

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(id(self))

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


def find(cell: Cell) -> Cell:
    while cell is not cell.data.dsu.parent:
        cell.data.dsu.parent = cell.data.dsu.parent.data.dsu.parent
        cell = cell.data.dsu.parent
    return cell


def merge(a: Cell, b: Cell) -> None:
    parent_a = find(a)
    parent_b = find(b)
    if parent_a.data.dsu.size > parent_b.data.dsu.size:
        parent_a, parent_b = parent_b, parent_a

    parent_a.data.dsu.parent = parent_b
    parent_b.data.dsu.size += parent_a.data.dsu.size


class Atomisation:
    closure_of: Cell
    atom: Cell

    def __init__(self, atom: Cell, closure_of: Cell):
        self.atom = atom
        self.closure_of = closure_of
        atom.data.atom_of.add(closure_of)
        closure_of.data.atoms.add(atom)

    def destroy(self):
        self.atom.data.atom_of.remove(self.closure_of)
        self.closure_of.data.atoms.remove(self.atom)


@dataclass
class CWComplex:
    layers: List[List[Cell]] = field(default_factory=list)
    atomisations: List[Atomisation] = field(default_factory=list)

    def link(self, a: Cell, b: Cell, label="", oriented=False) -> Optional[Cell]:
        assert a.dimension == 0
        assert b.dimension == 0

        if len(self.layers) < 2:
            self.layers.append([])

        for c in self.layers[1]:
            if (
                a == c.boundary[0]
                and c == c.boundary[1]
                or (not oriented and a == c.boundary[1] and c == c.boundary[0])
            ):
                return c
        return self.create_cell(label, [a, b])

    def atomize(self, what: Cell, to: Cell) -> Atomisation:
        assert what.dimension >= 1
        assert to.dimension == 0
        assert to not in what.atoms
        result = Atomisation(closure_of=what, atom=to)
        self.atomisations.append(result)
        return result

    def create_cell(self, label: str, boundary=None) -> Cell:
        if boundary:
            cell = Cell.from_boundary(label, boundary=boundary)
        else:
            cell = Cell.from_label(label)

        while cell.dimension >= len(self.layers):
            self.layers.append([])

        self.layers[cell.dimension].append(cell)

        return cell

    def __getitem__(self, key: str) -> Optional[Cell]:
        for layer in self.layers:
            for cell in layer:
                if cell.label == key:
                    return cell

    def build_coboundary(self):
        self.clear_coboundary()
        for layer in self.layers[1:]:
            for cell in layer:
                if cell.data.deleted:  # skip deleted
                    continue
                for b in cell.boundary:
                    if b.data.deleted:  # skip deleted
                        continue
                    if b.data.coboundary is None:
                        b.data.coboundary = []
                    b.coboundary.append(cell)

    def clear_coboundary(self):
        for layer in self.layers[:-1]:
            for cell in layer:
                cell.data.coboundary = None
