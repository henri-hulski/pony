from collections.abc import Iterable, Sequence
from datetime import date, datetime, timedelta
from decimal import Decimal
from types import ModuleType
from typing import Any, ClassVar
from typing_extensions import LiteralString

from pony.orm.core import (
    DbConnection,
    DbCursor,
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
    RealConverter,
    TimedeltaConverter,
    UuidConverter,
    wrap_dbapi_exceptions,
)
from pony.orm.dbschema import Column, DBSchema
from pony.orm.ormtypes import TrackedArray, TrackedValue
from pony.orm.sqlbuilding import Param, SQLBuilder, Value
from pony.orm.sqltranslation import SQLTranslator

ADMIN_SHUTDOWN: str
provider_cls: type[PGProvider]
NoneType: type[None]

class PGArrayConverter(ArrayConverter):
    array_types: ClassVar[dict[type[str | float], tuple[str, type[Converter]]]]

    def dbval2val(
        converter, dbval: OptAttrValue | Entity, obj: Entity | None = None
    ) -> TrackedArray | list[str | int | float] | None: ...
    def val2dbval(
        converter,
        val: TrackedValue | OptAttrValue,
        obj: Entity | None = None,
    ) -> str: ...

class PGBlobConverter(BlobConverter):
    def sql_type(converter) -> str: ...

class PGColumn(Column):
    auto_template: ClassVar[str | None]

class PGDateConverter(DateConverter):
    def py2sql(converter, val: date) -> str: ...
    def sql2py(converter, val: str | date) -> date: ...

class PGDatetimeConverter(DatetimeConverter):
    sql_type_name: LiteralString

    def py2sql(converter, val: datetime) -> str: ...
    def sql2py(converter, val: str | datetime) -> datetime: ...

class PGDecimalConverter(DecimalConverter):
    def py2sql(converter, val: Decimal) -> str: ...
    def sql2py(
        converter, val: Decimal | float | str | tuple[int, Sequence[int], int]
    ) -> Decimal: ...

class PGIntConverter(IntConverter):
    signed_types: dict[int | None, str]
    unsigned_types: dict[int | None, str] | None

    def sql_type(converter) -> str: ...

class PGJsonConverter(JsonConverter):
    def sql_type(self) -> str: ...

class PGPool(Pool):
    def _connect(pool) -> None: ...
    def release(pool, con: DbConnection) -> None: ...

class PGProvider(DBAPIProvider):
    array_converter_cls: type[PGArrayConverter]
    converter_classes: list[
        tuple[PyType | type[None] | tuple[type[int]], type[Converter]]  # noqa: Y090
    ]
    dbapi_module: ModuleType
    dbschema_cls: type[PGSchema]
    default_schema_name: str
    dialect: str
    fk_types: dict[str, str]
    index_if_not_exists_syntax: bool
    max_name_len: int
    max_params_count: int
    paramstyle: str
    sqlbuilder_cls: type[PGSQLBuilder]
    translator_cls: type[PGTranslator]

    def drop_table(
        provider, connection: DbConnection, table_name: TableName
    ) -> None: ...
    @wrap_dbapi_exceptions
    def execute(
        provider,
        cursor: DbCursor,
        sql: str,
        arguments: Any | None = None,
        returning_id: bool = False,
    ) -> int | None: ...
    def fk_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        fk_name: str,
        case_sensitive: bool = True,
    ) -> str | None: ...
    def get_pool(provider, *args, **kwargs) -> PGPool: ...
    def index_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        index_name: str,
        case_sensitive: bool = True,
    ) -> str | None: ...
    @wrap_dbapi_exceptions
    def inspect_connection(provider, connection: DbConnection) -> None: ...
    def normalize_name(provider, name: str) -> str: ...
    @wrap_dbapi_exceptions
    def set_transaction_mode(
        provider, connection: DbConnection, cache: SessionCache
    ) -> None: ...
    def should_reconnect(provider, exc: Exception) -> bool: ...
    def table_exists(
        provider,
        connection: DbConnection,
        table_name: TableName,
        case_sensitive: bool = True,
    ) -> str | None: ...

class PGRealConverter(RealConverter):
    def sql_type(converter) -> str: ...

class PGSchema(DBSchema):
    column_class: ClassVar[type[Column]]
    dialect: ClassVar[str]

class PGSQLBuilder(SQLBuilder):
    dialect: ClassVar[str]
    json_value_type_mapping: dict[type[bool | float], str]
    value_class: type[Value]

    def ARRAY_CONTAINS(builder, key, not_in, col) -> tuple[Any, str, Any, str]: ...
    def ARRAY_INDEX(builder, col, index) -> tuple[Any, str, Any, str]: ...
    def ARRAY_LENGTH(builder, array) -> tuple[str, Any, str]: ...
    def ARRAY_SLICE(
        builder, array, start, stop
    ) -> tuple[Any, str, Any | str, str, Any | str, str]: ...
    def ARRAY_SUBSET(
        builder, array1, not_in, array2
    ) -> tuple[str, tuple[Any, str, Any], str] | tuple[Any, str, Any]: ...
    def DATE(builder, expr: Sequence[str | list[str]]) -> tuple[str, Any, str]: ...
    def DATE_ADD(
        builder,
        expr: list[str],
        delta: list[(str | timedelta | ParamKey | PGTimedeltaConverter)],
    ) -> tuple[str, Any, str, Any, str]: ...
    def DATE_DIFF(builder, expr1, expr2) -> tuple[str, Any, str, Any, str]: ...
    def DATE_SUB(builder, expr, delta) -> tuple[str, Any, str, Any, str]: ...
    def DATETIME_ADD(builder, expr, delta) -> tuple[str, Any, str, Any, str]: ...
    def DATETIME_DIFF(
        builder,
        expr1: list[
            str | tuple[tuple[int, str, int], None, None] | PGDatetimeConverter
        ],
        expr2: list[str],
    ) -> tuple[str, Any, str, Any, str]: ...
    def DATETIME_SUB(builder, expr, delta) -> tuple[str, Any, str, Any, str]: ...
    def eval_json_path(builder, values) -> str: ...
    def GROUP_CONCAT(
        builder,
        distinct: bool | None,
        expr: Sequence[str],
        sep: Sequence[str] | None = None,
    ) -> tuple[
        tuple[tuple[str, Any, str], str] | tuple[tuple[str, Any, str], str, Any], str
    ]: ...
    def INSERT(
        builder,
        table_name: str,
        columns: Iterable[str | Iterable],
        values: Iterable[Sequence[str | tuple[int, None, None] | Converter]],
        returning: str | None = None,
    ) -> Sequence[str | list[str]]: ...
    def JSON_ARRAY_LENGTH(builder, value) -> tuple[str, Any, str]: ...
    def JSON_CONCAT(builder, left, right) -> tuple[str, Any, str, Any, str]: ...
    def JSON_CONTAINS(
        builder, expr: Sequence[str], path: list[Sequence[str]], key: Sequence
    ) -> tuple[tuple[str, Any, str, Param | Value, str], str, Any]: ...
    def JSON_NONZERO(builder, expr) -> tuple[str, Any, str]: ...
    def JSON_QUERY(
        builder,
        expr: Sequence[str],
        path: Sequence[Sequence[(str | int | ParamKey | Converter)]],
    ) -> tuple[str, Any, str, Param | Value, str]: ...
    def JSON_VALUE(
        builder,
        expr: Sequence[str],
        path: Sequence[Sequence[str | int | ParamKey | Converter]],
        type: type,
    ) -> (
        tuple[str, Any, str, Param | Value, str]
        | tuple[tuple[str, Any, str, Param | Value, str], str, str]
    ): ...
    def MAKE_ARRAY(builder, *items) -> tuple[str, list[Any | str], str]: ...
    def RANDOM(builder) -> str: ...
    def TO_INT(builder, expr) -> tuple[str, Any, str]: ...
    def TO_REAL(builder, expr) -> tuple[str, Any, str]: ...
    def TO_STR(builder, expr) -> tuple[str, Any, str]: ...

class PGTimedeltaConverter(TimedeltaConverter):
    def py2sql(converter, val: timedelta) -> float: ...

class PGTranslator(SQLTranslator):
    dialect: ClassVar[str]

class PGUuidConverter(UuidConverter):
    def py2sql(converter, val) -> Any: ...

class PGValue(Value): ...
