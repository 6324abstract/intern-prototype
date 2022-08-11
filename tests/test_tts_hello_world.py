from tts import TaskTypeSystem
from cwdb import CWComplex, Cell
import pytest


class PyImplementation:
    def __init__(self):
        self.called_with_args = None
        self.called_with_kwargs = None

    def __call__(self, *args, **kwargs):
        self.called_with_args = args
        self.called_with_kwargs = kwargs


def test_hello_world():
    cw = CWComplex()
    tts = TaskTypeSystem(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={}, code=printer)
    hw.eval()
    assert printer.called_with_kwargs == {}


@pytest.mark.skip(reason="Task args check is not implemented yet")
def test_hello_world_wrong_number_of_arguments():
    cw = CWComplex()
    tts = TaskTypeSystem(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={}, code=printer)
    arg = tts.Int.create(7)

    with pytest.raises(RuntimeError) as exc:
        hw.eval(n=arg)


def test_hello_world_n_times():
    cw = CWComplex()
    tts = TaskTypeSystem(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={"n": tts.Int}, code=printer)
    arg = tts.Int.create(7)
    hw.eval(n=arg)
    assert printer.called_with_kwargs == {"n": arg.cell}


@pytest.mark.skip(reason="Task arg type check is not implemented yet")
def test_hello_world_n_times_wrong_arg_type():
    cw = CWComplex()
    tts = TaskTypeSystem(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={"n": tts.Int.cell}, code=printer)
    arg = tts.String.create("Alice")
    with pytest.raises(RuntimeError) as exc:
        hw.eval(n=arg)


class PyTaskImplementationWithReturnValue:
    def __init__(self, return_value: Cell):
        self.called_with_args = None
        self.called_with_kwargs = None
        self.return_value = return_value

    def __call__(self, *args, **kwargs) -> Cell:
        self.called_with_args = args
        self.called_with_kwargs = kwargs
        return self.return_value


def test_task_return_type():
    cw = CWComplex()
    Human = cw.create_cell("Human")
    alice = cw.create_cell("Alice")
    cw.link(alice, Human, "io")
    tts = TaskTypeSystem(cw)

    func = PyTaskImplementationWithReturnValue(alice)
    hw = tts.Task.create(name="Get the Human", args={}, code=func)

    a_human = hw.eval()
    assert a_human is alice
