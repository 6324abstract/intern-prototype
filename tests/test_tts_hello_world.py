from typing import List

import pytest

from cwdb import CWComplex
from cwdb import tts as t
from cwdb.interfaces import ICell
from cwdb.tts import TaskTypeSystem


class PyImplementation:
    def __init__(self):
        self.called_with_args = None
        self.called_with_kwargs = None

    def __call__(self, *args, **kwargs):
        self.called_with_args = args
        self.called_with_kwargs = kwargs


def test_hello_world():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={}, impl=printer)
    hw.eval()
    assert printer.called_with_kwargs == {}


@pytest.mark.skip(reason="Task args check is not implemented yet")
def test_hello_world_wrong_number_of_arguments():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={}, impl=printer)
    arg = tts.Int.create(7)

    with pytest.raises(RuntimeError) as _:
        hw.eval(n=arg)


def test_hello_world_n_times():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={"n": tts.Int}, impl=printer)
    arg = tts.Int.create(7)
    hw.eval(n=arg)
    assert printer.called_with_kwargs == {"n": arg.cell}


@pytest.mark.skip(reason="Task arg type check is not implemented yet")
def test_hello_world_n_times_wrong_arg_type():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    printer = PyImplementation()
    hw = tts.Task.create(name="hello_world_n_times", args={"n": tts.Int}, impl=printer)
    arg = tts.String.create("Alice")
    with pytest.raises(RuntimeError) as _:
        hw.eval(n=arg)


class PyTaskImplementationWithReturnValue:
    def __init__(self, return_value: ICell):
        self.called_with_args = None
        self.called_with_kwargs = None
        self.return_value = return_value

    def __call__(self, *args, **kwargs) -> ICell:
        self.called_with_args = args
        self.called_with_kwargs = kwargs
        return self.return_value


def test_task_return_type():
    cw = CWComplex()
    Human = cw.create_cell("Human")
    alice = cw.create_cell("Alice")
    cw.link(alice, Human, "io")
    tts = TaskTypeSystem.from_empty_context(cw)

    func = PyTaskImplementationWithReturnValue(alice)
    hw = tts.Task.create(name="Get the Human", args={}, impl=func)

    a_human = hw.eval()
    assert a_human is alice


def test_create_int_set():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    IntSet: t.SetType[t.IntType] = tts.Set.create_type(tts.Int, context=cw)
    ints: List[t.Instance[t.IntType]] = [tts.Int.create(i) for i in (1, 2, 3)]
    int_set_1: t.SetInstance[t.IntType] = IntSet.create(*ints)
    int_4 = tts.Int.create(4)
    assert len(int_set_1) == 3
    assert ints[0] in int_set_1
    assert ints[1] in int_set_1
    assert ints[2] in int_set_1
    assert int_4 not in int_set_1

    for idx, elem in enumerate(int_set_1):
        assert elem is ints[idx].cell


def test_create_int_list():
    cw = CWComplex()
    tts = TaskTypeSystem.from_empty_context(cw)

    IntList: t.ListType[t.IntType] = tts.List.create_type(tts.Int, context=cw)
    ints: List[t.Instance[t.IntType]] = [tts.Int.create(i) for i in (1, 2, 3)]
    int_list_1: t.SetInstance[t.IntType] = IntList.create(*ints)
    int_4 = tts.Int.create(4)
    assert len(int_list_1) == 3
    assert ints[0] in int_list_1
    assert ints[1] in int_list_1
    assert ints[2] in int_list_1
    assert int_4 not in int_list_1

    for idx in range(len(int_list_1)):
        assert int_list_1[idx] is ints[idx].cell
