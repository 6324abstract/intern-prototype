"""
Visualizaing of this module:
https://miro.com/app/board/uXjVPes5Bj4=/?moveToWidget=3458764531408495124&cot=14
"""
from __future__ import annotations

from .core import Instance, Star, Type


class IntType(Type):
    def __init__(self, star: Star):
        super().__init__(star, "Int")

    def create(  # type: ignore[override]
        self: IntType, value: int
    ) -> Instance[IntType]:
        res = self.cw.create_cell(f"{value}")
        self.cw.link(res, self.cell, "io", oriented=True)
        return Instance[IntType](res)


class FloatType(Type):
    def __init__(self, star: Star):
        super().__init__(star, "Float")

    def create(  # type: ignore[override]
        self: FloatType, value: float
    ) -> Instance[FloatType]:
        res = self.cw.create_cell(f"{value}")
        self.cw.link(res, self.cell)
        return Instance[FloatType](res)


class StringType(Type):
    def __init__(self, star: Star):
        super().__init__(star, "String")

    def create(  # type: ignore[override]
        self: StringType, value: str
    ) -> Instance[StringType]:
        res = self.cw.create_cell(value)
        self.cw.link(res, self.cell)
        return Instance[StringType](res)
