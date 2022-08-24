from __future__ import annotations

from abc import abstractmethod
from typing import Generic
from typing import Type as Type_
from typing import TypeVar

from cwdb.interfaces import ICell, ICWComplex

T = TypeVar("T", bound="Type")
HT = TypeVar("HT", bound="TypeConstructor")


class Star:
    """Creates types"""

    def __init__(self, cw: ICWComplex, name: str = "*"):
        self.cw: ICWComplex = cw
        self.cell: ICell = self.cw.create_cell(name)

    def create(self, cls: Type_[T]) -> T:
        return cls(self)  # type: ignore[call-arg]


class StarToStar:
    """Creates type constructors"""

    def __init__(self, star: Star, name: str = "* -> *"):
        self.name = name
        self.star: Star = star
        self.cw: ICWComplex = star.cw
        self.cell: ICell = self.cw.create_cell(name)

    def create_type_constructor(self, cls: Type_[HT]) -> HT:
        return cls(self)  # type: ignore[call-arg]


class Instance(Generic[T]):
    """Represents Instance of specific type"""

    def __init__(self, cell: ICell):
        self.cell: ICell = cell


class Type:
    """Base class for all types"""

    def __init__(self, star: Star, name: str):
        self.star = star
        self.cw: ICWComplex = self.star.cw
        self.cell = self.cw.create_cell(name)
        self.cw.link(self.cell, self.star.cell, "io", oriented=True)

    @property
    def name(self) -> str:
        return self.cell.label


class TypeConstructor:
    """
    Base class for all type constructors
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
