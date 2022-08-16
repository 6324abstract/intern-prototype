from __future__ import annotations

from typing import Any, Callable, Dict

from cwdb import Cell

from .core import Instance, Star, Type


class SignatureType:
    def __init__(self, task_type: TaskType):
        self.cw = task_type.cw
        self.cell = self.cw.create_cell("Signature")
        task_type.cw.link(self.cell, task_type.cell)

        self.ArgumentType = ArgumentType(self)
        self.ReturnType = ReturnType(self)


class ArgumentType:
    def __init__(self, signature_type: SignatureType):
        self.cw = signature_type.cw
        self.cell = self.cw.create_cell("Argument")
        self.Argument_Signature_link = self.cw.link(self.cell, signature_type.cell)

    def typing_task_arguments(self, task_name: str, **args_types: Type) -> Cell:
        # Create argument 2-cell
        arg_cell_boundary = []

        for arg_name, arg_type in args_types.items():
            arg_cell = self.cw.create_cell(arg_name)
            arg_cell_boundary += [
                self.cw.link(arg_cell, arg_type.cell),
                self.cw.link(arg_cell, self.cell, oriented=True),
            ]

        arg_cell_boundary += [self.Argument_Signature_link]

        return self.cw.create_cell(f"Arguments for {task_name} task", arg_cell_boundary)


class ReturnType:
    def __init__(self, signature_type: SignatureType):
        self.cw = signature_type.cw
        self.cell = self.cw.create_cell("Return")
        self.Return_Signature_link = self.cw.link(self.cell, signature_type.cell)

    def typing_task_return(self, task_name: str, return_type: Type) -> Cell:
        # Create "return" 2-cell
        return self.cw.create_cell(
            f"Return for {task_name} task",
            [
                self.Return_Signature_link,
                self.cw.create_cell(return_type.cell.label, self.cell),
            ],
        )


class TaskType(Type):
    def __init__(self, star: Star):
        super().__init__(star, "Task")
        self.SignatureType = SignatureType(self)

    def create(  # type: ignore[override]
        self, name: str, args: Dict[str, Type], code: Callable, return_type: Type = None
    ) -> TaskInstance:
        task = self.cw.create_cell(name + "_task")
        self.cw.link(task, self.cell, "io")

        arguments_cell = self.SignatureType.ArgumentType.typing_task_arguments(
            name, **args
        )

        return_cell = None
        if return_type:
            return_cell = self.SignatureType.ReturnType.typing_task_return(
                name, return_type
            )

        if return_cell:
            task_three_cell = self.cw.create_cell(
                f"{name} task 3-cell", [arguments_cell, return_cell]
            )
        else:
            task_three_cell = self.cw.create_cell(
                f"{name} task 3-cell", [arguments_cell]
            )

        task.data.task_implementation = code

        self.cw.atomize(task_three_cell, task)
        return TaskInstance(task, self)


class BindedArgs:
    def __init__(self, cell: Cell, task: TaskInstance):
        self.cell = cell
        self.task = task

    def to_args_dict(self) -> Dict[str, Cell]:
        result = {}
        for link in self.cell.boundary:
            if (
                link.boundary[1]
                is not self.task.TaskType.SignatureType.ArgumentType.cell
            ):
                result[link.boundary[1].label] = link.boundary[0]
        return result


class TaskInstance(Instance[TaskType]):
    def __init__(self, cell: Cell, task_type: TaskType):
        super().__init__(cell)
        self.TaskType = task_type

    def _bind(self, **kwargs: Instance[Type]) -> BindedArgs:
        """Return 2-cell with specific arguments values"""
        return_cell_boundary = []
        for atomization in self.cell.atom_of:
            for cell in atomization.boundary:
                if cell.dimension == 2:
                    for link in cell.boundary:
                        if (
                            link.boundary[1]
                            is self.TaskType.SignatureType.ArgumentType.cell
                        ):
                            arg = link.boundary[0]
                            assert arg.data.label in kwargs
                            return_cell_boundary += [
                                link,
                                self.TaskType.cw.link(
                                    kwargs[arg.data.label].cell, arg, "io"
                                ),
                            ]

        bind_args_cell = self.TaskType.cw.create_cell(
            f"Input for {self.cell.data.label}", return_cell_boundary
        )
        return BindedArgs(bind_args_cell, self)

    def eval(self, **kwargs: Instance[Type]) -> Any:
        if self.cell.data.task_implementation is None:
            raise RuntimeError("Task is not atomic")

        if kwargs is None:
            return self.cell.data.task_implementation(**{})
        else:
            args_dict: Dict[str, Cell] = self._bind(**kwargs).to_args_dict()
            return self.cell.data.task_implementation(**args_dict)