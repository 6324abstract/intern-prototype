from __future__ import annotations

from cwdb import Cell, CWComplex

from .core import Instance, Star, StarToStar, Type  # noqa: F401
from .list import ListInstance, ListType, ListTypeConstructor  # noqa: F401
from .literals import FloatType, IntType, StringType
from .set import SetInstance, SetType, SetTypeConstructor  # noqa: F401
from .task import TaskInstance, TaskType  # noqa: F401


class TaskTypeSystem:
    def __init__(self, cw: CWComplex):
        self.cw = cw
        self.Star = Star(cw)
        self.StarToStar = StarToStar(star=self.Star)
        self.Int: IntType = self.Star.create(IntType)
        self.Float: FloatType = self.Star.create(FloatType)
        self.String: StringType = self.Star.create(StringType)
        self.Task: TaskType = self.Star.create(TaskType)

        self.Set: SetTypeConstructor = self.StarToStar.create_type_constructor(
            SetTypeConstructor
        )
        self.List: ListTypeConstructor = self.StarToStar.create_type_constructor(
            ListTypeConstructor
        )

    def is_instance_of(self, instance: Cell, asserted_type: Type) -> bool:
        # FIXME: context might be different from tts
        context = self.cw
        for link in instance.coboundary(context):
            if (
                link.dimension == 1
                and link.label == "io"
                and link.boundary[1] == asserted_type.cell
            ):
                return True
        return False
