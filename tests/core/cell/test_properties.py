import numpy as np
import pytest

from cwdb import Cell


def test_label():
    a = Cell.from_label("x")
    assert a.label == "x"
    a.label = "123"
    assert a.label == "123"


def test_embedding():
    a = Cell.from_label("x")
    assert len(a.embedding) == 0
    a.embedding = np.zeros(100)
    assert len(a.embedding) == 100
