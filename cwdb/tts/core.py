from __future__ import annotations

from abc import abstractmethod
from typing import Generic
from typing import Type as Type_
from typing import TypeVar

from cwdb import Cell, CWComplex

T = TypeVar("T", bound="Type")
HT = TypeVar("HT", bound="TypeConstructor")


class Star:
    def __init__(self, cw: CWComplex, name: str = "*"):
        self.cw: CWComplex = cw
        self.cell: Cell = self.cw.create_cell(name)

    def create(self, cls: Type_[T]) -> T:
        return cls(self)  # type: ignore[call-arg]


class StarToStar:
    def __init__(self, star: Star, name: str = "* -> *"):
        self.name = name
        self.star: Star = star
        self.cw: CWComplex = star.cw
        self.cell: Cell = self.cw.create_cell(name)

    def create_type_constructor(self, cls: Type_[HT]) -> HT:
        return cls(self)  # type: ignore[call-arg]


class Instance(Generic[T]):
    def __init__(self, cell: Cell):
        self.cell: Cell = cell


class Type:
    def __init__(self, star: Star, name: str):
        self.star = star
        self.cw: CWComplex = self.star.cw
        self.cell = self.cw.create_cell(name)
        self.cw.link(self.cell, self.star.cell, "io", oriented=True)

    @property
    def name(self) -> str:
        return self.cell.label


class TypeConstructor:
    """
    Only for * -> *
    NOT for * -> * -> *  or  * -> (* -> *), etc.
    """

    def __init__(self, star_to_star: StarToStar, name: str):
        self.star = star_to_star.star
        self.cw = self.star.cw
        self.cell = self.cw.create_cell(name)
        self.cw.link(self.cell, star_to_star.cell, "io", oriented=True)

    @abstractmethod
    def create_type(self, type_: Type) -> Type:
        pass
