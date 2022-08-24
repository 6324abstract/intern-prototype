"""
Visualizing of this module:
https://miro.com/app/board/uXjVPes5Bj4=/?moveToWidget=3458764531336116209&cot=14
"""
from __future__ import annotations

from typing import Generic, Iterator, List

from cwdb.interfaces import ICell

from .core import Instance, Star, StarToStar, T, Type, TypeConstructor


class ListTypeConstructor(TypeConstructor):
    """Represents `List[_]` type constructor"""

    def __init__(self, star_to_star: StarToStar):
        super(ListTypeConstructor, self).__init__(
            star_to_star=star_to_star, name="List[...]"
        )

    def create_type(self, type_of_elems: T) -> ListType[T]:
        type_name = f"List[{type_of_elems.name}]"
        return ListType(self.star, type_name, type_of_elems)


class ListType(Generic[T], Type):
    """Represents `List[T]` type with specific type of elements `T`
    e.g. List[IntType]"""

    def __init__(self, star: Star, name: str, type_: Type):
        super(ListType, self).__init__(star=star, name=name)
        self.element_type = type_

    def create(self, *args: Instance[T]) -> ListInstance[T]:
        boundary = []
        previous_cell = self.cell
        for elem in args:
            boundary.append(self.cw.link(elem.cell, previous_cell, oriented=True))
            previous_cell = elem.cell

        result_atom = self.cw.create_cell(f"instance of List[{self.element_type.name}]")
        result_cell = self.cw.create_cell(
            label=f"List[{self.element_type.name}]#{id(result_atom):0x}",
            boundary=boundary,
        )
        self.cw.create_atom_link(expansion=result_cell, atom=result_atom)
        self.cw.link(result_atom, self.cell, "io", oriented=True)
        return ListInstance(result_cell)


class ListInstance(Generic[T], Instance[ListType[T]]):
    """Represents instances of `List[T]` type
    e.g. instance of List[IntType] = [1,22,-45]"""

    def __init__(self, cell: ICell):
        super(ListInstance, self).__init__(cell=cell)

    @property
    def list_representation(self) -> List[ICell]:
        return [link.boundary[0] for link in self.cell.boundary]

    def __contains__(self, item: Instance[T]) -> bool:
        return item.cell in self.list_representation

    def __iter__(self) -> Iterator[ICell]:
        return self.list_representation.__iter__()

    def __getitem__(self, idx: int) -> ICell:
        return self.list_representation[idx]

    def __len__(self) -> int:
        return len(self.list_representation)
