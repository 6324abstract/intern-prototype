"""
Visualizing of this module:
https://miro.com/app/board/uXjVPes5Bj4=/?moveToWidget=3458764531408495124&cot=14
"""
from __future__ import annotations

from .core import Instance, Type


class IntType(Type):
    def create(self: IntType, value: int) -> Instance[IntType]:
        res = self.cw.create_cell(f"{value}")
        self.cw.link(res, self.cell, "io", oriented=True)
        return Instance[IntType](res)


class FloatType(Type):
    def create(self: FloatType, value: float) -> Instance[FloatType]:
        res = self.cw.create_cell(f"{value}")
        self.cw.link(res, self.cell, "io", oriented=True)
        return Instance[FloatType](res)


class StringType(Type):
    def create(self: StringType, value: str) -> Instance[StringType]:
        res = self.cw.create_cell(value)
        self.cw.link(res, self.cell, "io", oriented=True)
        return Instance[StringType](res)
