import sys, platform
from typing import Any, Protocol


class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...


PYPY = platform.python_implementation() == "PyPy"
PY36 = sys.version_info[:2] >= (3, 6)
PY37 = sys.version_info[:2] >= (3, 7)
PY38 = sys.version_info[:2] >= (3, 8)
PY39 = sys.version_info[:2] >= (3, 9)
PY310 = sys.version_info[:2] >= (3, 10)
PY311 = sys.version_info[:2] >= (3, 11)
PY312 = sys.version_info[:2] >= (3, 12)

unicode: type[str] = str
buffer: type[bytes] = bytes
int_types: tuple[type[int]] = (int,)


def cmp(a: Comparable, b: Comparable) -> int:
    return (a > b) - (a < b)
