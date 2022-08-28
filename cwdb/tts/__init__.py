from __future__ import annotations

from ..interfaces import ICWComplex
from .core import Instance, Star, StarToStar, Type  # noqa: F401
from .list import ListInstance, ListType, ListTypeConstructor  # noqa: F401
from .literals import FloatType, IntType, StringType
from .set import SetInstance, SetType, SetTypeConstructor  # noqa: F401
from .task import TaskInstance, TaskType  # noqa: F401


class TaskTypeSystem:
    def __init__(
        self,
        ctx: ICWComplex,
        star: Star,
        star_to_star: StarToStar,
        int_t: IntType,
        float_t: FloatType,
        string_t: StringType,
        task_t: TaskType,
        set_tc: SetTypeConstructor,
        list_tc: ListTypeConstructor,
    ):
        self.cw = ctx
        self.Star = star
        self.StarToStar = star_to_star
        self.Int = int_t
        self.Float = float_t
        self.String = string_t
        self.Task = task_t
        self.Set = set_tc
        self.List = list_tc

    @classmethod
    def from_empty_context(cls, ctx: ICWComplex) -> TaskTypeSystem:
        star = Star._from_empty_context(ctx)
        star_to_star = StarToStar._from_star(star=star, context=ctx)
        int_t: IntType = star.create_new_type(IntType, name="Int", context=ctx)
        float_t: FloatType = star.create_new_type(FloatType, name="Float", context=ctx)
        string_t: StringType = star.create_new_type(
            StringType, name="String", context=ctx
        )
        task_t: TaskType = star.create_new_type(TaskType, name="Task", context=ctx)

        set_tc: SetTypeConstructor = star_to_star.create_type_constructor(
            SetTypeConstructor
        )
        list_tc: ListTypeConstructor = star_to_star.create_type_constructor(
            ListTypeConstructor
        )
        return cls(
            ctx=ctx,
            star=star,
            star_to_star=star_to_star,
            int_t=int_t,
            float_t=float_t,
            string_t=string_t,
            task_t=task_t,
            set_tc=set_tc,
            list_tc=list_tc,
        )
