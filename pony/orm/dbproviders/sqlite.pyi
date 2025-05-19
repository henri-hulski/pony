from collections.abc import Callable, Iterable, Sequence
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from re import Pattern
from types import ModuleType
from typing import Any, ClassVar, Literal, NoReturn, TypeVar

from pony.orm.core import (
    Database,
    DbConnection,
    Entity,
    OptAttrValue,
    ParamKey,
    PyType,
    SessionCache,
    TableName,
)
from pony.orm.dbapiprovider import (
    ArrayConverter,
    BlobConverter,
    Converter,
    DateConverter,
    DatetimeConverter,
    DBAPIProvider,
    DecimalConverter,
    IntConverter,
    JsonConverter,
    Pool,
    TimeConverter,
    TimedeltaConverter,
    wrap_dbapi_exceptions,
)
from pony.orm.dbschema import DBSchema, ForeignKey
from pony.orm.ormtypes import TrackedArray, TrackedValue
from pony.orm.sqlbuilding import Param, SQLBuilder, Value
from pony.orm.sqltranslation import SQLTranslator
from pony.utils import localbase

_T = TypeVar("_T")

json_path_re: Pattern[str]
local_exceptions: LocalExceptions
NoneType: type[None]
path_cache: dict[str, tuple[str, ...] | None]
provider_cls: type[SQLiteProvider]
py_lower: Callable[[str], Any]
py_upper: Callable[[str], Any]

def _parse_path(path: str) -> tuple[str, ...] | None: ...
def _text_factory(s: bytes) -> str: ...
def _traverse(
    obj: object,
    keys: Iterable[str | int] | None,
) -> Any: ...
def dumps(items: object) -> str: ...
def keep_exception(func: Callable[..., _T]) -> Callable[..., _T]: ...
def make_overriden_string_func(sqlop: str) -> Callable: ...
def make_string_function(
    name: str, base_func: Callable[[object], _T]
) -> Callable[[str], _T | None]: ...
def py_array_contains(array: list, item: object) -> bool: ...
def py_array_index(array: list, index: int) -> float | None: ...
def py_array_length(array: list) -> int: ...
def py_array_slice(array: list, start: int | None, stop: int | None) -> str: ...
def py_array_subset(array: list, items: str) -> bool: ...
def py_json_array_length(expr, path=...) -> int: ...
def py_json_contains(expr: str, path: str, key: str) -> bool: ...
def py_json_extract(expr, *paths) -> str | list[Any]: ...
def py_json_nonzero(expr, path) -> bool: ...
def py_json_query(expr, path, with_wrapper) -> str | None: ...
def py_json_unwrap(value: str) -> str | None: ...
def py_json_value(expr, path) -> list[Any] | None: ...
def py_make_array(*items) -> str: ...
def py_string_slice(s: str, start: int | None, end: int | None) -> str: ...
def wrap_array_func(func: Callable[..., _T]) -> Callable[..., _T | None]: ...

class LocalExceptions(localbase):
    exc_info: tuple | None
    keep_traceback: bool

    def __init__(self) -> None: ...

class RealConverter(Converter): ...

class SQLiteArrayConverter(ArrayConverter):
    array_types: ClassVar[dict[type[str | float], tuple[str, type[Converter]]]]

    def dbval2val(
        converter, dbval: OptAttrValue | Entity, obj: Entity | None = None
    ) -> TrackedArray | list[str | int | float] | None: ...
    def val2dbval(
        converter, val: TrackedValue | OptAttrValue, obj: Entity | None = None
    ) -> str: ...

class SQLiteBlobConverter(BlobConverter): ...

class SQLiteBuilder(SQLBuilder):
    json_value_type_mapping: dict[type[str | bool | float], str]

    dialect: ClassVar[str]
    greatest_func_name: ClassVar[str]
    least_func_name: ClassVar[str]
    value_class: type[Value]

    PY_UPPER: Callable
    PY_LOWER: Callable

    def __init__(
        builder, provider: SQLiteProvider, ast: list[str | list | None]
    ) -> None: ...
    def datetime_add(
        builder, funcname: str, expr: list[str], td: timedelta
    ) -> tuple[str, str, Any, list[str], str]: ...
    def ARRAY_CONTAINS(
        builder, key: Sequence[str | float], not_in: bool, col: Sequence[str]
    ) -> tuple[str, str, Any, str, Any, str]: ...
    def ARRAY_INDEX(
        builder,
        col: Sequence[str],
        index: Sequence[
            str
            | int
            | Sequence[
                str | int | Sequence[str | int | ParamKey | IntConverter | Sequence]
            ]
            | None
        ],
    ) -> tuple[str, Any, str, Any, str]: ...
    def ARRAY_LENGTH(builder, array: Sequence[str]) -> tuple[str, Any, str]: ...
    def ARRAY_SLICE(
        builder,
        array: Sequence[str],
        start: Sequence[str | int | Sequence | None] | None,
        stop: Sequence[str | int | Sequence | None] | None,
    ) -> tuple[
        str, Any, str, Any | Literal["null"], str, Any | Literal["null"], str
    ]: ...
    def ARRAY_SUBSET(
        builder,
        array1: Sequence[(str | ParamKey | ArrayConverter | Sequence[str | int])],
        not_in: bool,
        array2: Sequence[str],
    ) -> tuple[str, str, Any, str, Any, str]: ...
    def DATE_ADD(
        builder,
        expr: list[str],
        delta: list[(str | timedelta | ParamKey | SQLiteTimedeltaConverter)],
    ) -> tuple[str, Any, str, Any, str]: ...
    def DATE_DIFF(
        builder, expr1: list[str | ParamKey | SQLiteDateConverter], expr2: list[str]
    ) -> tuple[str, Any, str, Any, str]: ...
    def DATE_SUB(
        builder,
        expr: list[str],
        delta: list[(str | timedelta | ParamKey | SQLiteTimedeltaConverter)],
    ) -> tuple[str, Any, str, Any, str]: ...
    def DATETIME_ADD(
        builder,
        expr: list[str],
        delta: list[(str | timedelta | ParamKey | SQLiteTimedeltaConverter)],
    ) -> tuple[str, Any, str, Any, str]: ...
    def DATETIME_DIFF(
        builder, expr1: list[str | ParamKey | SQLiteDatetimeConverter], expr2: list[str]
    ) -> tuple[str, Any, str, Any, str]: ...
    def DATETIME_SUB(
        builder,
        expr: list[str],
        delta: list[(str | timedelta | ParamKey | SQLiteTimedeltaConverter)],
    ) -> tuple[str, Any, str, Any, str]: ...
    def DAY(builder, expr: list[str]) -> tuple[str, Any, str]: ...
    def FLOAT_EQ(
        builder, a, b
    ) -> tuple[str, Any, str, Any, str, Any, str, Any, str]: ...
    def FLOAT_NE(
        builder, a, b
    ) -> tuple[str, Any, str, Any, str, Any, str, Any, str]: ...
    def HOUR(builder, expr: list[str]) -> tuple[str, Any, str]: ...
    def IN(
        builder,
        expr1: list[str | int | ParamKey | Converter | list[str] | None],
        x: list,
    ) -> str | tuple[Any, str, Any] | tuple[Any, str, list, str]: ...
    def INSERT(
        builder,
        table_name: str,
        columns: Iterable[str | Iterable],
        values: Iterable[Sequence[str | tuple[int, None, None] | Converter]],
        returning: str | None = None,
    ) -> Sequence[str | list[str]]: ...
    def JSON_ARRAY_LENGTH(
        builder, value: Sequence[str | Sequence[str | list[str]]]
    ) -> (
        tuple[str, str, tuple[str, str, str, list[str], str, Value, str], str]
        | tuple[str, str, list[str], str]
    ): ...
    def JSON_CONTAINS(
        builder,
        expr: Sequence[str],
        path: Sequence[Sequence[str]],
        key: Sequence[str | ParamKey | Converter],
    ) -> tuple[str, list[str], str, Param | Value, str, Param | Value, str]: ...
    def JSON_NONZERO(
        builder, expr: Sequence[str | Sequence[str | list[str]]]
    ) -> tuple[tuple[str, str, str, list[str], str, Value, str], str]: ...
    def JSON_QUERY(
        builder,
        expr: Sequence[str],
        path: Sequence[Sequence[(str | int | ParamKey | Converter)]],
    ) -> tuple[str, str, str, list[str], str, Param | Value, str]: ...
    def JSON_VALUE(
        builder,
        expr: Sequence[str],
        path: Sequence[Sequence[str | int | ParamKey | Converter]],
        type: type[OptAttrValue] | None = None,
    ) -> (
        tuple[str, str, list[str], str, Value | Param, str]
        | tuple[str, tuple[str, str, list[str], str, Value | Param, str], str, str, str]
    ): ...
    def MAKE_ARRAY(builder, *items) -> tuple[str, list, str]: ...
    def MINUTE(builder, expr: list[str]) -> tuple[str, Any, str]: ...
    def MONTH(builder, expr: list[str]) -> tuple[str, Any, str]: ...
    def NOT_IN(
        builder, expr1: list[str | int | ParamKey | Converter | list[str]], x: list
    ) -> str | tuple[Any, str, Any] | tuple[Any, str, list, str]: ...
    def NOW(builder) -> str: ...
    def RANDOM(builder) -> str: ...
    def SECOND(builder, expr: list[str]) -> tuple[str, Any, str]: ...
    def SELECT_FOR_UPDATE(
        builder, nowait: bool, skip_locked: bool, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | list[str]]]: ...
    def STRING_SLICE(
        builder,
        expr: Sequence[str],
        start: Sequence[str | int | Sequence | None] | None,
        stop: Sequence[str | int | Sequence | None] | None,
    ) -> tuple[
        str,
        list[str],
        str,
        Value | list[str] | tuple,
        str,
        Value | list[str] | tuple,
        str,
    ]: ...
    def TODAY(builder) -> str: ...
    def YEAR(builder, expr: list[str]) -> tuple[str, Any, str]: ...

class SQLiteDateConverter(DateConverter):
    def py2sql(converter, val: date) -> str: ...
    def sql2py(converter, val: str | date) -> date: ...

class SQLiteDatetimeConverter(DatetimeConverter):
    def py2sql(converter, val: datetime) -> str: ...
    def sql2py(converter, val: str | datetime) -> datetime: ...

class SQLiteDecimalConverter(DecimalConverter):
    inf: Decimal
    NaN: Decimal
    neg_inf: Decimal

    def py2sql(converter, val: Decimal) -> str: ...
    def sql2py(converter, val: Decimal | float | str) -> Decimal: ...

class SqliteExtensionUnavailable(Exception): ...

class SQLiteForeignKey(ForeignKey):
    def get_create_command(foreign_key: object) -> NoReturn: ...

class SQLiteIntConverter(IntConverter):
    def sql_type(converter) -> str: ...

class SQLiteJsonConverter(JsonConverter):
    json_kwargs: ClassVar[dict[str, tuple[str, ...] | bool]] = ...

class SQLitePool(Pool):
    def __init__(
        pool, is_shared_memory_db: bool, filename: str, create_db: bool, **kwargs
    ) -> None: ...
    def _connect(pool) -> None: ...
    def disconnect(pool) -> None: ...
    def drop(pool, con: DbConnection) -> None: ...

class SQLiteProvider(DBAPIProvider):
    array_converter_cls: type[SQLiteArrayConverter]
    converter_classes: list[
        tuple[PyType | type[None] | tuple[type[int]], type[Converter]]  # noqa: Y090
    ]
    dbapi_module: ModuleType
    dbschema_cls: type[SQLiteSchema]
    dialect: str
    local_exceptions: LocalExceptions
    max_name_len: int
    name_before_table: str
    server_version: int | tuple[int, ...] | None
    sqlbuilder_cls: type[SQLiteBuilder]
    translator_cls: type[SQLiteTranslator]

    def __init__(provider, database: Database, filename: str, **kwargs) -> None: ...
    def _exists(
        provider,
        connection: DbConnection,
        table_name: str,
        index_name: str | None = None,
        case_sensitive: bool = True,
    ) -> str | None: ...
    def acquire_lock(provider) -> None: ...
    def check_json1(provider, connection: DbConnection) -> bool: ...
    def commit(
        provider, connection: DbConnection, cache: SessionCache | None = ...
    ) -> None: ...
    def drop(
        provider, connection: DbConnection, cache: SessionCache | None = ...
    ) -> None: ...
    def get_pool(
        provider,
        is_shared_memory_db: bool,
        filename: str,
        create_db: bool = False,
        **kwargs,
    ) -> SQLitePool: ...
    def index_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        index_name: str,
        case_sensitive: bool = True,
    ) -> str | None: ...
    @wrap_dbapi_exceptions
    def inspect_connection(provider, connection: DbConnection) -> None: ...
    @wrap_dbapi_exceptions
    def release(
        provider, connection: DbConnection, cache: SessionCache | None = None
    ) -> None: ...
    def release_lock(provider) -> None: ...
    def restore_exception(provider) -> None: ...
    def rollback(
        provider, connection: DbConnection, cache: SessionCache | None = None
    ) -> None: ...
    @wrap_dbapi_exceptions
    def set_transaction_mode(
        provider, connection: DbConnection, cache: SessionCache
    ) -> None: ...
    def table_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        case_sensitive: bool = True,
    ) -> str | None: ...

class SQLiteSchema(DBSchema):
    dialect: ClassVar[str]
    fk_class: ClassVar[type[ForeignKey]]
    named_foreign_keys: ClassVar[bool]

class SQLiteTimeConverter(TimeConverter):
    def py2sql(converter, val) -> Any: ...
    def sql2py(converter, val) -> time: ...

class SQLiteTimedeltaConverter(TimedeltaConverter):
    def py2sql(converter, val: timedelta) -> float: ...
    def sql2py(converter, val) -> timedelta: ...

class SQLiteTranslator(SQLTranslator):
    dialect: ClassVar[str]
    row_value_syntax: ClassVar[bool]
    rowid_support: ClassVar[bool]
    StringMixin_LOWER: ClassVar[Callable[[str], str]] = ...
    StringMixin_UPPER: ClassVar[Callable[[str], str]] = ...
    sqlite_version: ClassVar[tuple[int, int, int]] = ...

class SQLiteValue(Value): ...
