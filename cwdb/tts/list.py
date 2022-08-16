from __future__ import annotations

from typing import Generic, Iterator, List

from cwdb import Cell

from .core import Instance, Star, StarToStar, T, Type, TypeConstructor


class ListType(Generic[T], Type):
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
        self.cw.atomize(what=result_cell, to=result_atom)
        return ListInstance(result_atom)


class ListInstance(Generic[T], Instance[ListType[T]]):
    def __init__(self, cell: Cell):
        super(ListInstance, self).__init__(cell=cell)

    # Border of atomed cell must be in order
    @property
    def list_representation(self) -> List[Cell]:
        return [link.boundary[0] for link in self.cell.the_only_atom_of.boundary]

    def __contains__(self, item: Instance[T]) -> bool:
        return item.cell in self.list_representation

    def __iter__(self) -> Iterator[Cell]:
        return self.list_representation.__iter__()

    def __getitem__(self, idx: int) -> Cell:
        return self.list_representation[idx]

    def __len__(self) -> int:
        return len(self.list_representation)


class ListTypeConstructor(TypeConstructor):
    def __init__(self, star_to_star: StarToStar):
        super(ListTypeConstructor, self).__init__(
            star_to_star=star_to_star, name="List[...]"
        )

    def create_type(self, type_of_elems: T) -> ListType[T]:
        type_name = f"List[{type_of_elems.name}]"
        return ListType(self.star, type_name, type_of_elems)
