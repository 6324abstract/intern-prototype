import numpy as np
from .core import CWComplex


class QueryError(RuntimeError):
    def __init__(self, message, offending):
        super().__init__(message)
        self.offending = offending


def query_boundary(label: str, boundary):
    x, y = boundary[:2]
    result = None
    for e in x.coboundary:
        if e.dimension == 1 and e.label == label and e.boundary[1] is y:
            if result is None:
                result = e
                continue
            else:
                raise QueryError("Uncertainty detected", [result, e])
    if result is None:
        return np.array([0.5, 0])
    return result.embedding


def query_boundary_and_resolve_ambiguity(c: CWComplex, label: str, boundary, ambiguity_resolution_rule):
    while True:
        try:
            return query_boundary(label, boundary)
        except QueryError as e:
            ambiguity_resolution_rule(c, *e.offending)
