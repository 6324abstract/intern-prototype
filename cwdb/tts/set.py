"""
Visualizing of this module:
https://miro.com/app/board/uXjVPes5Bj4=/?moveToWidget=3458764531336116322&cot=14
"""
from __future__ import annotations

from typing import Generic, Iterator

from cwdb import Cell

from .core import Instance, Star, StarToStar, T, Type, TypeConstructor


class SetTypeConstructor(TypeConstructor):
    """Represents `Set[_]` type constructor"""

    def __init__(self, star_to_star: StarToStar):
        super(SetTypeConstructor, self).__init__(
            star_to_star=star_to_star, name="Set[...]"
        )

    def create_type(self, type_of_elems: T) -> SetType[T]:
        type_name = f"Set[{type_of_elems.name}]"
        return SetType(self.star, type_name, type_of_elems)


class SetType(Generic[T], Type):
    """Represents `Set[T]` type with specific type of elements `T` e.g. Set[IntType]"""

    def __init__(self, star: Star, name: str, type_: Type):
        super(SetType, self).__init__(star=star, name=name)
        self.element_type = type_

    # TODO elems should be unique
    def create(self, *args: Instance[T]) -> SetInstance[T]:
        boundary = [self.cw.link(el.cell, self.cell, oriented=True) for el in args]
        result_atom = self.cw.create_cell(f"instance of Set[{self.element_type.name}]")
        result_cell = self.cw.create_cell(
            label=f"Set[{self.element_type.name}]#{id(result_atom):0x}",
            boundary=boundary,
        )
        self.cw.atomize(what=result_cell, to=result_atom)
        return SetInstance(result_atom)


class SetInstance(Generic[T], Instance[SetType[T]]):
    """Represents instances of `Set[T]` type
    e.g. instance of Set[IntType] = {1,22,-45}"""

    def __init__(self, cell: Cell):
        super(SetInstance, self).__init__(cell=cell)

    def __contains__(self, item: Instance[T]) -> bool:
        for link in self.cell.the_only_atom_of.boundary:
            if link.boundary[0] is item.cell:
                return True
        return False

    def __iter__(self) -> Iterator[Cell]:
        return [
            link.boundary[0] for link in self.cell.the_only_atom_of.boundary
        ].__iter__()

    def __len__(self) -> int:
        return len(self.cell.the_only_atom_of.boundary)
