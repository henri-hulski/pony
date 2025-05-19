import types
from collections.abc import Callable, Iterable
from datetime import datetime
from decimal import Decimal
from typing import Any, ClassVar, SupportsIndex, TypeVar, overload
from weakref import ReferenceType

from typing_extensions import Self, TypeAlias

from pony.orm.core import (
    Attribute,
    Comparable,
    Entity,
    EntityIter,
    EntityMeta,
    ExprType,
    Numeric,
    OptAttrValue,
    PyType,
    Query,
    QueryKey,
    QueryResult,
    QueryResultIterator,
    SetIterator,
)
from pony.orm.sqltranslation import SQLTranslator
from types import BuiltinFunctionType, CodeType, FunctionType

_FuncType: TypeAlias = FunctionType | BuiltinFunctionType

_T = TypeVar("_T")
_FT = TypeVar("_FT", bound=_FuncType)
_QT = TypeVar("_QT", bound=Query | QueryResult | QueryResultIterator | SetIterator)
_OACT = TypeVar("_OACT", bound=OptAttrValue | ellipsis)
_TT = TypeVar("_TT", bound=PyType | EntityMeta | type[None] | slice | ellipsis)

numeric_types: set[type[Numeric]]
comparable_types: set[type[Comparable | Array]]
primitive_types: set[type[Comparable | Array | bytes]]
function_types: set[_FuncType | type]
array_types: dict[type[int | str | float], type[Array]]
LongUnicode: type[LongStr]
coercions: dict[tuple[type, type], type[int | float | Decimal | datetime]]

class LongStr(str):
    lazy: ClassVar[bool]

def are_comparable_types(
    t1: ExprType,
    t2: ExprType,
    op: str = "==",
) -> bool: ...
def coerce_types(t1: type | SetType, t2: type | SetType) -> type | SetType | None: ...
@overload
def normalize(value: tuple) -> tuple[tuple, tuple]: ...
@overload
def normalize(value: EntityMeta | EntityIter) -> tuple[SetType, Entity]: ...
@overload
def normalize(value: types.MethodType) -> tuple[MethodType, types.MethodType]: ...
@overload
def normalize(value: _FT) -> tuple[FuncType, _FT]: ...
@overload
def normalize(value: _QT) -> tuple[QueryType, _QT]: ...
@overload
def normalize(value: RawSQL) -> tuple[RawSQLType, RawSQL]: ...
@overload
def normalize(value: _OACT) -> tuple[type[_OACT], _OACT]: ...
@overload
def normalize_type(t: _TT) -> _TT: ...
@overload
def normalize_type(t: tuple[_TT, ...]) -> tuple[_TT, ...]: ...
def parse_raw_sql(
    sql: str,
) -> tuple[
    tuple[str | tuple[str, types.CodeType], ...], tuple[types.CodeType, ...]
]: ...
def raw_sql(sql: str, result_type: PyType | None = None) -> RawSQL: ...
def tracked_method(func: Callable[..., _T]) -> Callable[..., _T]: ...
def validate_item(
    item_type: type[str | float], item: str | int | SupportsIndex
) -> str | int | float: ...

class Array:
    item_type: ClassVar[Any]

    @classmethod
    def default_empty_value(cls) -> list[Any]: ...

class IntArray(Array):
    item_type: ClassVar[type[int]]

class StrArray(Array):
    item_type: ClassVar[type[str]]

class FloatArray(Array):
    item_type: ClassVar[type[float]]

class FuncType:
    func: Callable

    def __deepcopy__(self, memo: dict[int, object]) -> Self: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        func: Callable,
    ) -> None: ...

class Json:
    wrapped: dict[str, str] | list[str]

    def __init__(self, wrapped: dict[str, str] | list[str]) -> None: ...
    @classmethod
    def default_empty_value(cls) -> dict[Any, Any]: ...

class MethodType:
    obj: object
    func: Callable

    def __hash__(self) -> int: ...
    def __init__(self, method: types.MethodType) -> None: ...

class QueryType:
    query_key: QueryKey
    translator: SQLTranslator
    limit: int | None
    offset: int | None

    def __hash__(self) -> int: ...
    def __init__(
        self, query: Query, limit: int | None = None, offset: int | None = None
    ) -> None: ...

class RawSQL:
    sql: str
    items: tuple[str | tuple[str, types.CodeType], ...]
    codes: tuple[types.CodeType, ...]
    types: tuple[type, ...]
    values: tuple[Any, ...]
    result_type: PyType | None

    def _get_type_(self) -> RawSQLType: ...
    def __init__(
        self,
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        result_type: PyType | None = None,
    ) -> None: ...
    def __lt__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...

class RawSQLType:
    sql: str
    items: tuple[str | tuple[str, types.CodeType], ...]
    types: tuple[type, ...]
    result_type: PyType | None

    def __deepcopy__(self, memo: Any) -> Self: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        sql: str,
        items: tuple[str | tuple[str, CodeType], ...],
        types: tuple[type, ...],
        result_type: PyType | None = None,
    ) -> None: ...

class SetType:
    item_type: type

    def __deepcopy__(self, memo: dict[int, object]) -> Self: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(self, item_type: type) -> None: ...

class TrackedValue:
    obj_ref: ReferenceType[Entity] | None
    attr: Attribute | None

    def __init__(self, obj: Entity | None, attr: Attribute | None) -> None: ...
    def _changed_(self) -> None: ...
    @classmethod
    def make(cls, obj: Entity | Any, attr: Attribute | Any, value: Any) -> Any: ...
    def get_untracked(self) -> Any: ...

class TrackedList(TrackedValue, list):
    def __init__(
        self,
        obj: Entity,
        attr: Attribute,
        value: list[Any],
    ) -> None: ...
    def __reduce__(
        self,
    ) -> tuple[type[list], tuple[list]]: ...  # noqa: Y090
    def get_untracked(self) -> list: ...

class TrackedArray(TrackedList):
    item_type: type[str | int | float]

    def __contains__(self, item: Any) -> bool: ...
    def __init__(self, obj: Entity, attr: Attribute, value: list) -> None: ...
    def append(self, item: Any) -> None: ...
    def extend(self, items: Iterable[Any]) -> None: ...

class TrackedDict(TrackedValue, dict):
    def __init__(
        self,
        obj: Entity,
        attr: Attribute,
        value: dict[str, Any],
    ) -> None: ...
    def __reduce__(
        self,
    ) -> tuple[type[dict], tuple[dict[str, Any]]]: ...  # noqa: Y090
    def get_untracked(self) -> dict: ...
    def update(self, *args, **kwargs) -> None: ...
