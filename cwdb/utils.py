from __future__ import annotations

from typing import Dict, Generic, Iterable, TypeVar

T = TypeVar("T")


class DSUImpl(Generic[T]):
    parent: DSUImpl
    node: T
    size: int
    rank: int

    def __init__(self, node: T):
        self.node = node
        self.parent = self
        self.size = 1
        self.rank = 1

    def find(self) -> DSUImpl[T]:
        data = self
        while data is not data.parent:
            data.parent = data.parent.parent
            data = data.parent
        return data

    @staticmethod
    def merge(a: DSUImpl[T], b: DSUImpl[T]) -> None:
        parent_a = a.find()
        parent_b = b.find()

        if parent_a.size > parent_b.size:
            parent_a, parent_b = parent_b, parent_a

        parent_a.parent = parent_b
        parent_b.size += parent_a.size
        parent_a.rank = max(parent_a.rank, parent_b.rank) + 1


class DSU(Generic[T]):
    def __init__(self, elements: Iterable[T] = ()):
        self.dsu_impl: Dict[T, DSUImpl] = {el: DSUImpl(el) for el in elements}

    def find(self, a: T) -> DSUImpl[T]:
        return self.dsu_impl[a].find()

    def merge(self, a: T, b: T):
        DSUImpl.merge(self.dsu_impl[a], self.dsu_impl[b])
