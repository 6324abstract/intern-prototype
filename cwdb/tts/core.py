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

    def __init__(self, cell: ICell, *, context: ICWComplex):
        self.cell: ICell = cell
        self.cw: ICWComplex = context

    @classmethod
    def _from_empty_context(cls, context: ICWComplex):
        cell = context.create_cell("*")
        return cls(cell=cell, context=context)

    def create_new_type(
        self, class_: Type_[T], /, name: str, *, context: ICWComplex
    ) -> T:
        return class_._from_name(star=self, name=name, context=context)


class StarToStar:
    """Creates type constructors"""

    def __init__(self, cell: ICell, star: Star, *, context: ICWComplex):
        self.star: Star = star
        self.cw: ICWComplex = context
        self.cell: ICell = cell

    @classmethod
    def _from_star(cls, star: Star, *, context: ICWComplex):
        cell = context.create_cell("* -> *")

        # TODO: Add explanation of `* -> *` in terms of `*`
        #       Currently, there is no connection between `*` and `* -> *`,
        #       they are completely unrelated cells in the underlying CWc.
        return cls(cell=cell, star=star, context=context)

    def create_type_constructor(self, cls: Type_[HT]) -> HT:
        return cls(self)  # type: ignore[call-arg]


class Instance(Generic[T]):
    """Represents Instance of specific type"""

    def __init__(self, cell: ICell):
        self.cell: ICell = cell

    def is_instance_of(self, type_: Type, *, context: ICWComplex) -> bool:
        for link in self.cell.coboundary(context):
            if (
                link.dimension == 1
                and link.label == "io"
                and link.boundary[1] == type_.cell
            ):
                return True
        return False


class Type:
    """Base class for all types"""

    def __init__(self, star: Star, cell: ICell, *, context: ICWComplex, **kwargs):
        assert len(kwargs) == 0
        self.star: Star = star
        self.cell: ICell = cell
        self.cw: ICWComplex = context

    @classmethod
    def _from_name(cls, name: str, star: Star, *, context: ICWComplex, **kwargs):
        cell = context.create_cell(name)
        context.link(cell, star.cell, "io", oriented=True)
        return cls(cell=cell, star=star, context=context, **kwargs)

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
    def create_type(self, param: T, *, context: ICWComplex) -> Type:
        pass
