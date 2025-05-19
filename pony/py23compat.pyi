from typing import Any, Protocol

class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...

PYPY: bool
PY36: bool
PY37: bool
PY38: bool
PY39: bool
PY310: bool
PY311: bool
PY312: bool

unicode: type[str]
buffer: type[bytes]
int_types: tuple[type[int]]  # noqa: Y090

def cmp(a: Comparable, b: Comparable) -> int: ...
