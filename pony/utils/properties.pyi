from collections.abc import Callable
from typing import Any, Generic, overload

from typing_extensions import Self, TypeVar

_T = TypeVar("_T")

class cached_property(Generic[_T]):
    func: Callable[..., _T]

    def __init__(self, func: Callable[..., _T]) -> None: ...
    @overload
    def __get__(self, obj: None, cls: Any) -> Self: ...
    @overload
    def __get__(self, obj: object, cls: Any) -> _T: ...

class class_property(Generic[_T]):
    func: Callable[..., _T]

    def __init__(self, func: Callable[..., _T]) -> None: ...
    def __get__(self, instance: Any, cls: type) -> _T: ...

class class_cached_property(Generic[_T]):
    func: Callable[..., _T]

    def __init__(self, func: Callable[..., _T]) -> None: ...
    def __get__(self, obj: Any, cls: type) -> _T: ...
