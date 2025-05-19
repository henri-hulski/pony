import json
from collections.abc import Callable, Iterable, Sequence
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from types import ModuleType
from typing import (
    Any,
    ClassVar,
    Generic,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    TypeVar,
)
from uuid import UUID

from _typeshed import MaybeNone
from typing_extensions import Concatenate, LiteralString, ParamSpec, Self, TypeAlias

from pony.orm.core import (
    Attribute,
    CachedSqlSimple,
    Database,
    DbConnection,
    DbCursor,
    Entity,
    EntityMeta,
    OptAttrValue,
    PyType,
    QueryVars,
    SessionCache,
    Set,
    TableName,
    VarTypes,
)
from pony.orm.dbschema import DBSchema
from pony.orm.ormtypes import (
    Array,
    Json,
    LongStr,
    RawSQLType,
    TrackedArray,
    TrackedValue,
)
from pony.orm.sqlbuilding import SQLBuilder
from pony.orm.sqltranslation import SQLTranslator
from pony.orm.tests.testutils import TestPool
from pony.utils.utils import decorator, localbase

_ExtPyType: TypeAlias = PyType | RawSQLType | type[None]

_T = TypeVar("_T")
_P = ParamSpec("_P")
_OAT_co = TypeVar("_OAT_co", bound=OptAttrValue, covariant=True)

@decorator
def wrap_dbapi_exceptions(
    func: Callable[Concatenate[DBAPIProvider, _P], _T],
    provider: DBAPIProvider,
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> _T: ...
def get_version_tuple(s: str) -> tuple[int, ...] | None: ...

class Converter(Generic[_OAT_co]):
    attr: Attribute[_OAT_co] | MaybeNone
    provider: DBAPIProvider
    py_type: type

    EQ: ClassVar[LiteralString]
    NE: ClassVar[LiteralString]
    optimistic: ClassVar[bool]

    def __deepcopy__(
        converter,
        memo: dict[int, object],
    ) -> Self: ...
    def __init__(
        converter,
        provider: DBAPIProvider,
        py_type: _ExtPyType,
        attr: Attribute[_OAT_co] | None = None,
    ) -> None: ...
    def dbval2val(
        self, dbval: OptAttrValue | Entity, obj: Entity | MaybeNone = None
    ) -> Any: ...
    def dbvals_equal(self, x: Any, y: Any) -> bool: ...
    def get_fk_type(converter, sql_type: str) -> str: ...
    def get_sql_type(converter, attr: Attribute | None = None) -> str: ...
    def init(converter, kwargs: dict[str, Any]) -> None: ...
    def py2sql(converter, val: Any) -> OptAttrValue: ...
    def sql2py(converter, val: str | Any, /) -> OptAttrValue: ...
    def sql_type(converter) -> Any: ...
    def val2dbval(
        self, val: OptAttrValue | TrackedValue, obj: Entity | None = None
    ) -> Any: ...
    def validate(
        converter, val: Any, obj: Any | None = None
    ) -> OptAttrValue | TrackedValue | list: ...

class ArrayConverter(Converter):
    item_converter: Converter
    py_type: type[Array]

    array_types: ClassVar[dict[type[str | float], tuple[str, type[Converter]]]]

    def __init__(
        converter,
        provider: DBAPIProvider,
        py_type: type[Array],
        attr: Attribute | None = None,
    ) -> None: ...
    def sql_type(converter) -> str: ...
    def validate(
        converter, val: object, obj: Entity | None = None
    ) -> TrackedValue | list: ...
    def dbval2val(
        converter, dbval: OptAttrValue | Entity, obj: Entity | None = None
    ) -> Any: ...
    def val2dbval(
        converter,
        val: TrackedValue | OptAttrValue,
        obj: Entity | None = None,
    ) -> str | list[OptAttrValue] | None: ...

class BlobConverter(Converter):
    py_type: type[bytes]

    def sql2py(converter, val: bytes | str | Any) -> bytes: ...
    def sql_type(converter) -> str: ...
    def validate(converter, val: bytes | str, obj: Entity | None = None) -> bytes: ...

class BoolConverter(Converter):
    py_type: type[bool]

    def sql2py(converter, val: object) -> bool: ...
    def sql_type(converter) -> str: ...
    def validate(converter, val: bool | int, obj: Entity | None = None) -> bool: ...

class ConverterWithMicroseconds(Converter):
    precision: int | None
    sql_type_name: LiteralString

    def __init__(
        converter,
        provider: DBAPIProvider,
        py_type: type[datetime | time | timedelta],
        attr: Attribute | None = None,
    ) -> None: ...
    def init(converter, kwargs: dict[str, Any]) -> None: ...
    def round_microseconds_to_precision(
        converter, microseconds: int, precision: int
    ) -> int | None: ...
    def sql_type(converter) -> str: ...

class DBAPIProvider:
    database: Database | None
    pool: Pool | TestPool
    server_version: int | tuple[int, ...] | None

    array_converter_cls: type[ArrayConverter] | MaybeNone
    converter_classes: list[
        tuple[PyType | type[None] | tuple[type[int]], type[Converter]]  # noqa: Y090
    ]
    dbapi_module: ModuleType | MaybeNone
    dbschema_cls: type[DBSchema] | MaybeNone
    default_schema_name: str | MaybeNone
    default_time_precision: int
    dialect: str | MaybeNone
    fk_types: dict[str, str]
    index_if_not_exists_syntax: bool
    max_name_len: int
    max_params_count: int
    max_time_precision: int
    name_before_table: str
    paramstyle: str
    quote_char: str
    sqlbuilder_cls: type[SQLBuilder] | MaybeNone
    table_if_not_exists_syntax: bool
    translator_cls: type[SQLTranslator] | MaybeNone
    uint64_support: bool
    varchar_default_max_len: int | None

    def __init__(provider, _database: Database | None, *args, **kwargs) -> None: ...
    def ast2sql(provider, ast: list) -> CachedSqlSimple: ...
    def base_name(provider, name: TableName) -> str: ...
    def commit(
        provider, connection: DbConnection, cache: SessionCache | None = None
    ) -> None: ...
    def connect(
        provider,
    ) -> tuple[DbConnection, bool]: ...
    def disconnect(provider) -> None: ...
    def drop(
        provider, connection: DbConnection, cache: SessionCache | None = None
    ) -> None: ...
    def drop_table(provider, connection: DbConnection, table_name: str) -> None: ...
    def execute(
        provider,
        cursor: DbCursor,
        sql: str,
        arguments: Sequence | None = None,
        returning_id: bool = False,
    ) -> int | MaybeNone: ...
    def fk_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        fk_name: str,
        case_sensitive: bool = True,
    ) -> str | None: ...
    def format_table_name(provider, name: TableName) -> str: ...
    def get_converter_by_attr(provider, attr: Attribute) -> Converter: ...
    def get_converter_by_py_type(
        provider,
        py_type: _ExtPyType,
    ) -> Converter: ...
    def _get_converter_type_by_py_type(
        provider,
        py_type: _ExtPyType,
    ) -> type[Converter]: ...
    def get_default_column_names(
        provider, attr: Attribute, reverse_pk_columns: list[str] | None = None
    ) -> list[str]: ...
    def get_default_entity_table_name(provider, entity: EntityMeta) -> str: ...
    def get_default_fk_name(
        provider,
        child_table_name: TableName,
        parent_table_name: TableName,
        child_column_names: Iterable[str],
    ) -> str: ...
    def get_default_index_name(
        provider,
        table_name: TableName,
        column_names: Iterable[str],
        is_pk: bool = False,
        is_unique: bool | None = False,
        m2m: bool = False,
    ) -> str: ...
    def get_default_m2m_column_names(provider, entity: EntityMeta) -> list[str]: ...
    def get_default_m2m_table_name(provider, attr: Set, reverse: Set) -> str: ...
    def get_pool(provider, *args, **kwargs) -> Pool: ...
    def index_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        index_name: str,
        case_sensitive: bool = True,
    ) -> str | None: ...
    def inspect_connection(provider, connection: DbConnection) -> None: ...
    def normalize_name(provider, name: str) -> str: ...
    def normalize_vars(
        provider,
        vars: QueryVars,
        vartypes: VarTypes,
    ) -> None: ...
    def quote_name(provider, name: str | Iterable[str]) -> str: ...
    def release(
        provider,
        connection: DbConnection,
        cache: SessionCache | None = None,
    ) -> None: ...
    def rollback(
        provider, connection: DbConnection, cache: SessionCache | None = None
    ) -> None: ...
    def set_transaction_mode(
        provider, connection: DbConnection, cache: SessionCache
    ) -> None: ...
    def should_reconnect(provider, exc: Exception) -> bool: ...
    def split_table_name(provider, table_name: TableName) -> tuple[str, str]: ...
    def table_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        case_sensitive: bool = True,
    ) -> str | None: ...
    def table_has_data(
        provider, connection: DbConnection, table_name: TableName
    ) -> bool: ...

class DBException(Exception):
    def __init__(exc, original_exc: Exception, *args) -> None: ...

class Warning(DBException): ...
class Error(DBException): ...
class InterfaceError(Error): ...
class DatabaseError(Error): ...
class DataError(DatabaseError): ...
class OperationalError(DatabaseError): ...
class IntegrityError(DatabaseError): ...
class InternalError(DatabaseError): ...
class ProgrammingError(DatabaseError): ...
class NotSupportedError(DatabaseError): ...

class DateConverter(Converter):
    py_type: type[date]

    def sql_type(converter) -> str: ...
    def validate(converter, val: date | str, obj: Entity | None = None) -> date: ...
    def sql2py(converter, val: date | str) -> date: ...

class TimeConverter(ConverterWithMicroseconds):
    py_type: type[time]

    def validate(converter, val: time | str, obj: Entity | None = None) -> time: ...
    def sql2py(converter, val: time | str) -> time: ...

class TimedeltaConverter(ConverterWithMicroseconds):
    py_type: type[timedelta]

    def validate(
        converter, val: timedelta | str, obj: Entity | None = None
    ) -> timedelta: ...
    def sql2py(converter, val: timedelta | str) -> timedelta: ...

class DatetimeConverter(ConverterWithMicroseconds):
    py_type: type[datetime]

    def validate(
        converter, val: datetime | str, obj: Entity | None = None
    ) -> datetime: ...
    def sql2py(converter, val: datetime | str) -> datetime: ...

class UuidConverter(Converter):
    def validate(
        converter, val: UUID | bytes | str | int, obj: Entity | None = None
    ) -> UUID: ...
    def sql_type(converter) -> str: ...

class DecimalConverter(Converter):
    exp: Decimal
    max_val: Decimal | None
    min_val: Decimal | None
    precision: int
    scale: int
    py_type: type[Decimal]

    def __init__(
        converter,
        provider: DBAPIProvider,
        py_type: type[Decimal],
        attr: Attribute | None = None,
    ) -> None: ...
    def init(converter, kwargs: dict[str, Any]) -> None: ...
    def sql2py(converter, val: Decimal | float | str) -> Decimal: ...
    def sql_type(converter) -> str: ...
    def validate(
        converter,
        val: Decimal | float | str,
        obj: Entity | None = None,
    ) -> Decimal: ...

class IntConverter(Converter):
    max_val: int | None
    min_val: int | None
    signed_types: dict[int | None, str]
    size: int | None
    unsigned: bool
    unsigned_types: dict[int | None, str] | None
    py_type: type[int]

    def init(converter, kwargs: dict[str, Any]) -> None: ...
    def sql2py(converter, val: int | str | SupportsInt | SupportsIndex) -> int: ...
    def sql_type(converter) -> str: ...
    def validate(
        converter, val: int | SupportsIndex | str, obj: Entity | None = None
    ) -> int: ...

class JsonConverter(Converter):
    py_type: type[Json]

    json_kwargs: ClassVar[dict[str, Any]]

    class JsonEncoder(json.JSONEncoder):
        def default(converter, o: Json) -> dict[str, str] | list[str]: ...

    def dbval2val(
        converter, dbval: OptAttrValue | Entity, obj: Entity | None = None
    ) -> Any: ...
    def sql_type(converter) -> str: ...
    def val2dbval(
        converter,
        val: Any,
        obj: Entity | None = None,
    ) -> str: ...
    def validate(
        converter,
        val: Any,
        obj: Entity | None = None,
    ) -> TrackedValue: ...

class NoneConverter(Converter):
    py_type: type[None]

    def __init__(
        converter, provider: DBAPIProvider, py_type: type[None], attr: None = None
    ) -> None: ...

class Pool(localbase):
    args: tuple
    con: DbConnection | MaybeNone
    dbapi_module: DBAPIProvider
    kwargs: dict[str, Any]
    pid: int | MaybeNone

    forked_connections: ClassVar[list[tuple[DbConnection, int]]]

    def __init__(pool, dbapi_module: DBAPIProvider, *args, **kwargs) -> None: ...
    def connect(pool) -> tuple[DbConnection, bool]: ...
    def disconnect(pool) -> None: ...
    def drop(pool, con: DbConnection) -> None: ...
    def release(pool, con: DbConnection) -> None: ...

class RealConverter(Converter):
    max_val: float | None
    min_val: float | None
    tolerance: float
    py_type: type[float]

    default_tolerance: ClassVar[float]

    def init(converter, kwargs: dict[str, Any]) -> None: ...
    def sql2py(
        converter, val: float | str | SupportsFloat | SupportsIndex
    ) -> float: ...
    def sql_type(converter) -> str: ...
    def validate(
        converter,
        val: float | str | SupportsFloat | SupportsIndex,
        obj: Entity | None = None,
    ) -> float: ...

class StrConverter(Converter):
    autostrip: bool
    db_encoding: str | None
    max_len: int
    py_type: type[str | LongStr]

    def __init__(
        converter,
        provider: DBAPIProvider,
        py_type: type[str | LongStr],
        attr: Attribute | None = None,
    ) -> None: ...
    def init(converter, kwargs: dict[str, Any]) -> None: ...
    def sql_type(converter) -> str: ...
    def validate(converter, val: str, obj: Entity | None = None) -> str | MaybeNone: ...
