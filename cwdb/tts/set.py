"""
Visualizing of this module:
https://miro.com/app/board/uXjVPes5Bj4=/?moveToWidget=3458764531336116322&cot=14
"""
from __future__ import annotations

from typing import Generic, Iterator

from cwdb.interfaces import ICell, ICWComplex

from .core import Instance, Star, StarToStar, T, Type, TypeConstructor


class SetTypeConstructor(TypeConstructor):
    """Represents `Set[_]` type constructor"""

    def __init__(self, star_to_star: StarToStar):
        super(SetTypeConstructor, self).__init__(
            star_to_star=star_to_star, name="Set[...]"
        )

    def create_type(self, param: T, *, context: ICWComplex) -> SetType[T]:
        type_name = f"Set[{param.name}]"
        return SetType._from_element_type(
            type_=param, name=type_name, star=self.star, context=context
        )


class SetType(Generic[T], Type):
    """Represents `Set[T]` type with specific type of elements `T` e.g. Set[IntType]"""

    def __init__(self, star: Star, cell: ICell, element_t: T, *, context: ICWComplex):
        super(SetType, self).__init__(star=star, cell=cell, context=context)
        self.element_type = element_t

    @classmethod
    def _from_element_type(
        cls, type_: T, name: str, star: Star, *, context: ICWComplex
    ):
        return cls._from_name(name=name, star=star, context=context, element_t=type_)

    # TODO elems should be unique
    def create(self, *args: Instance[T]) -> SetInstance[T]:
        boundary = [self.cw.link(el.cell, self.cell, oriented=True) for el in args]
        result_atom = self.cw.create_cell(f"instance of Set[{self.element_type.name}]")
        result_cell = self.cw.create_cell(
            label=f"Set[{self.element_type.name}]#{id(result_atom):0x}",
            boundary=boundary,
        )
        self.cw.create_atom_link(expansion=result_cell, atom=result_atom)
        self.cw.link(result_atom, self.cell, "io", oriented=True)
        return SetInstance(result_cell)


class SetInstance(Generic[T], Instance[SetType[T]]):
    """Represents instances of `Set[T]` type
    e.g. instance of Set[IntType] = {1,22,-45}"""

    def __init__(self, cell: ICell):
        super(SetInstance, self).__init__(cell=cell)

    def __contains__(self, item: Instance[T]) -> bool:
        for link in self.cell.boundary:
            if link.boundary[0] == item.cell:
                return True
        return False

    def __iter__(self) -> Iterator[ICell]:
        return [link.boundary[0] for link in self.cell.boundary].__iter__()

    def __len__(self) -> int:
        return len(self.cell.boundary)
