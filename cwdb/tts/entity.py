"""
Visualizing of this module:
https://miro.com/app/board/uXjVPes5Bj4=/?moveToWidget=3458764532429039768&cot=14
"""
from __future__ import annotations

from typing import Callable, Generic, List, Optional, TypeVar

from cwdb.interfaces import ICell, ICWComplex

from .core import Instance, Type
from .task import TaskInstance, TaskType

T = TypeVar("T", bound=Type)


class EntityType(Type):
    def __init__(self, cell: ICell, *, context: ICWComplex, task_type: TaskType = None):
        assert task_type is not None
        super().__init__(cell, context=context)
        self.task_type = task_type

    def create_child(self, name: str) -> EntityType:
        cell = self.cw.create_cell(name)
        self.cw.link(cell, self.cell, "is", oriented=True)
        return EntityType(cell, context=self.cw, task_type=self.task_type)

    def create(self: EntityType, name: str) -> EntityInstance:
        cell = self.cw.create_cell(name)
        self.cw.link(cell, self.cell, "io", oriented=True)
        return EntityInstance(cell, self.task_type)


class EntityInstance(Instance[EntityType]):
    def __init__(self, cell: ICell, task_type: TaskType):
        super().__init__(cell)
        self.task_type = task_type

    def aspects(self, *, context: ICWComplex) -> List[AspectInstance]:
        cwc_aspects = []
        for link in self.cell.coboundary(context):
            if link.label == "possess":
                assert link.boundary[0] == self.cell
                cwc_aspects.append(AspectInstance(link.boundary[1], self.task_type))
        return cwc_aspects

    def declare_aspect(self, aspect: AspectInstance, *, context: ICWComplex) -> ICell:
        return context.link(self.cell, aspect.cell, label="possess", oriented=True)

    def get(self, getter: GetterInstance[T], *, context: ICWComplex) -> Instance[T]:
        if getter.aspect not in self.aspects(context=context):
            raise RuntimeError(
                f"{getter.name} requires possession of {getter.aspect.name}"
            )

        ans = getter.find_memo(self, context=context)
        if ans is not None:
            return ans
        return getter.eval(self, context=context)

    def memoize(
        self, getter: GetterInstance[Type], value: Instance[Type], context: ICWComplex
    ) -> ICell:

        return context.create_cell(
            "memo",
            [
                context.link(self.cell, value.cell, label="value", oriented=True),
                context.link(self.cell, getter.cell, label="getter", oriented=True),
            ],
        )


class AspectType(Type):
    def __init__(self, cell: ICell, *, context: ICWComplex, task_type: TaskType = None):
        assert task_type is not None
        super().__init__(cell, context=context)
        self.task_type = task_type

    def create(self: AspectType, name: str) -> AspectInstance:
        result = self.cw.create_cell(name)
        self.cw.link(result, self.cell, "io", oriented=True)
        return AspectInstance(result, task_type=self.task_type)


class AspectInstance(Instance[AspectType]):
    def __init__(self, cell: ICell, task_type: TaskType):
        super().__init__(cell)
        self.task_type = task_type

    @property
    def name(self) -> str:
        return self.cell.label

    def getters(self, *, context: ICWComplex) -> List[GetterInstance]:
        cwc_getters: List[GetterInstance] = []
        for link in self.cell.coboundary(context):
            if link.label == "getter":
                assert link.boundary[0] == self.cell
                cwc_getters.append(
                    GetterInstance(link.boundary[1], self, self.task_type)
                )
        return cwc_getters


class GetterType(Type):
    def __init__(self, cell: ICell, *, context: ICWComplex, task_type: TaskType = None):
        assert task_type is not None
        super().__init__(cell, context=context)
        context.link(self.cell, task_type.cell, "is", oriented=True)
        self.task_type = task_type

    def create(
        self,
        name: str,
        aspect: AspectInstance,
        association_type: EntityType,
        return_type: Type,
        impl: Callable = None,
    ) -> GetterInstance[T]:
        task: TaskInstance = self.task_type.create(
            name=name,
            args={"arg": association_type},
            return_type=return_type,
            impl=impl,
        )
        self.cw.link(aspect.cell, task.cell, "getter", oriented=True)
        self.cw.link(task.cell, self.cell, "io", oriented=True)
        return GetterInstance(task.cell, aspect, task_type=self.task_type)


class GetterInstance(Generic[T], Instance[GetterType]):
    def __init__(self, cell: ICell, aspect: AspectInstance, task_type: TaskType):
        super().__init__(cell)
        self.task_type = task_type
        self.aspect = aspect

    @property
    def name(self) -> str:
        return self.cell.label

    def find_memo(
        self, entity: EntityInstance, *, context: ICWComplex
    ) -> Optional[Instance]:
        for link in entity.cell.coboundary(context):
            if (link.label == "getter") and (link.boundary[1] == self.cell):
                for cell in link.coboundary(context):
                    for link_inner in cell.boundary:
                        if link_inner.label == "value":
                            assert link_inner.boundary[0] == entity.cell
                            return Instance(link_inner.boundary[1])
        return None

    def find_task(self, context: ICWComplex) -> TaskInstance:
        return TaskInstance(self.cell, self.task_type)

    def eval(self, arg: EntityInstance, *, context: ICWComplex) -> Instance[T]:
        return self.find_task(context=context).eval(arg=arg)
