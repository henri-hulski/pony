from ast import GeneratorExp, expr
from collections.abc import (
    Callable,
    Coroutine,
    Generator,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from io import StringIO
from logging import Logger
from threading import RLock
from types import CellType, FunctionType, GeneratorType, TracebackType
from typing import Any, ClassVar, Generic, Literal, Protocol, TextIO, TypeVar, overload
from uuid import UUID

import _typeshed
from _typeshed import MaybeNone
from typing_extensions import LiteralString, ParamSpec, Self, TypeAlias, Unpack

import pony as pony
from pony.orm.asttranslation import TranslationError as TranslationError
from pony.orm.dbapiprovider import Converter
from pony.orm.dbapiprovider import DatabaseError as DatabaseError
from pony.orm.dbapiprovider import DataError as DataError
from pony.orm.dbapiprovider import DBAPIProvider as DBAPIProvider
from pony.orm.dbapiprovider import DBException as DBException
from pony.orm.dbapiprovider import Error as Error
from pony.orm.dbapiprovider import IntegrityError as IntegrityError
from pony.orm.dbapiprovider import InterfaceError as InterfaceError
from pony.orm.dbapiprovider import InternalError as InternalError
from pony.orm.dbapiprovider import NotSupportedError as NotSupportedError
from pony.orm.dbapiprovider import OperationalError as OperationalError
from pony.orm.dbapiprovider import ProgrammingError as ProgrammingError
from pony.orm.dbapiprovider import Warning as Warning
from pony.orm.dbschema import DBSchema, Table
from pony.orm.ormtypes import Array as Array
from pony.orm.ormtypes import FloatArray as FloatArray
from pony.orm.ormtypes import FuncType
from pony.orm.ormtypes import IntArray as IntArray
from pony.orm.ormtypes import Json as Json
from pony.orm.ormtypes import LongStr as LongStr
from pony.orm.ormtypes import LongUnicode as LongUnicode
from pony.orm.ormtypes import MethodType, QueryType, RawSQL, RawSQLType, SetType
from pony.orm.ormtypes import StrArray as StrArray
from pony.orm.ormtypes import TrackedValue
from pony.orm.ormtypes import raw_sql as raw_sql
from pony.orm.sqltranslation import SQLTranslator
from pony.py23compat import buffer as buffer
from pony.py23compat import unicode as unicode
from pony.utils.utils import HashableDict
from pony.utils.utils import between as between
from pony.utils.utils import coalesce as coalesce
from pony.utils.utils import concat as concat
from pony.utils.utils import decorator, localbase

__all__ = [
    "pony",
    "DBException",
    "RowNotFound",
    "MultipleRowsFound",
    "TooManyRowsFound",
    "Warning",
    "Error",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",
    "OrmError",
    "ERDiagramError",
    "DBSchemaError",
    "MappingError",
    "BindingError",
    "TableDoesNotExist",
    "TableIsNotEmpty",
    "ConstraintError",
    "CacheIndexError",
    "ObjectNotFound",
    "MultipleObjectsFoundError",
    "TooManyObjectsFoundError",
    "OperationWithDeletedObjectError",
    "TransactionError",
    "ConnectionClosedError",
    "TransactionIntegrityError",
    "IsolationError",
    "CommitException",
    "RollbackException",
    "UnrepeatableReadError",
    "OptimisticCheckError",
    "UnresolvableCyclicDependency",
    "UnexpectedError",
    "DatabaseSessionIsOver",
    "PonyRuntimeWarning",
    "DatabaseContainsIncorrectValue",
    "DatabaseContainsIncorrectEmptyValue",
    "TranslationError",
    "ExprEvalError",
    "PermissionError",
    "Database",
    "sql_debug",
    "set_sql_debug",
    "sql_debugging",
    "show",
    "PrimaryKey",
    "Required",
    "Optional",
    "Set",
    "Discriminator",
    "composite_key",
    "composite_index",
    "flush",
    "commit",
    "rollback",
    "db_session",
    "make_proxy",
    "LongStr",
    "LongUnicode",
    "Json",
    "IntArray",
    "StrArray",
    "FloatArray",
    "select",
    "left_join",
    "get",
    "exists",
    "delete",
    "count",
    "sum",
    "min",
    "max",
    "avg",
    "group_concat",
    "distinct",
    "JOIN",
    "desc",
    "between",
    "concat",
    "coalesce",
    "raw_sql",
    "buffer",
    "unicode",
]

Numeric: TypeAlias = bool | int | float | Decimal
_DateTime: TypeAlias = datetime | date | time | timedelta
Comparable: TypeAlias = str | Numeric | _DateTime | UUID | Array
SingleAttrValue: TypeAlias = str | Numeric | _DateTime | UUID | Json | bytes
AttrValue: TypeAlias = SingleAttrValue | Array
OptAttrValue: TypeAlias = AttrValue | None
_UniqueAttrValue: TypeAlias = (  # same as AttrValue but without float
    str | bool | int | Decimal | _DateTime | UUID | Json | bytes | Array
)
_PkValue: TypeAlias = _UniqueAttrValue | Entity | tuple[_UniqueAttrValue | Entity, ...]
_KeyValue: TypeAlias = OptAttrValue | Entity | Sequence[OptAttrValue | Entity]
PyType: TypeAlias = type[AttrValue]
ConstType: TypeAlias = type[bytes | Decimal | _DateTime]
Constant: TypeAlias = str | Numeric | _DateTime | Json | bytes | ellipsis | None
CodeKey: TypeAlias = str | int
VarKey: TypeAlias = tuple[int, str, CodeKey]
VarType: TypeAlias = (
    EntityMeta
    | PyType
    | SetType
    | FuncType
    | MethodType
    | QueryType
    | RawSQLType
    | type[None]
)
ExprType: TypeAlias = VarType | tuple[VarType, ...]
VarTypes: TypeAlias = HashableDict[VarKey, ExprType] | dict[VarKey, ExprType]
QueryVars: TypeAlias = dict[
    VarKey, Query | QueryResult | QueryResultIterator | SetIterator
]
_AvDict: TypeAlias = dict[Attribute, OptAttrValue | Entity]
AttrOffsets: TypeAlias = dict[Attribute, list[int]]
AdapterValue: TypeAlias = bool | int | float | bytes | str | None
AdapterResult: TypeAlias = tuple[AdapterValue, ...] | dict[str, AdapterValue]
Adapter: TypeAlias = Callable[[_AvDict], AdapterResult]
CachedSqlSimple: TypeAlias = tuple[str, Adapter]
_CachedSql: TypeAlias = tuple[str, Adapter, AttrOffsets]
DbRow: TypeAlias = Sequence[OptAttrValue]
_DbTypeCode: TypeAlias = Any
_DbCursorDescription: TypeAlias = tuple[
    str, _DbTypeCode, int | None, int | None, int | None, int | None, bool | None
]
ParamKey: TypeAlias = tuple[VarKey | int, int | None, int | None]
QueryKey: TypeAlias = HashableDict[str, Any]
TableName: TypeAlias = str | tuple[str, str]

_OAET_co = TypeVar("_OAET_co", bound=OptAttrValue | Entity, covariant=True)
_AET_co = TypeVar("_AET_co", bound=AttrValue | Entity, covariant=True)
_OAT_co = TypeVar("_OAT_co", bound=OptAttrValue, covariant=True)
_AT_co = TypeVar("_AT_co", bound=AttrValue, covariant=True)
_ET_co = TypeVar("_ET_co", bound=Entity, covariant=True)
_AT = TypeVar("_AT", bound=AttrValue)
_ET = TypeVar("_ET", bound=Entity)
_CT = TypeVar("_CT", bound=Coroutine)
_GT = TypeVar("_GT", bound=Generator)
_P = ParamSpec("_P")
_T = TypeVar("_T")

class DbCursor(Protocol):
    arraysize: int

    @property
    def description(self) -> Sequence[_DbCursorDescription]: ...
    @property
    def rowcount(self) -> int: ...
    @property
    def lastrowid(self) -> int | None: ...
    def execute(
        self,
        sql: str,
        arguments: Sequence | Mapping[str, Any] = ...,
        /,
    ) -> object: ...
    def executemany(self, sql: str, arguments: Sequence[Sequence], /) -> object: ...
    def fetchone(self) -> DbRow | None: ...
    def fetchmany(self, size: int = ..., /) -> Sequence[DbRow]: ...
    def fetchall(self) -> Sequence[DbRow]: ...
    def var(
        self, typ: type, size: int, arrazsize: int, /, outconverter: Callable
    ) -> Any: ...

class DbConnection(Protocol):
    autocommit: bool
    server_version: int | tuple[int, ...] | MaybeNone

    def close(self) -> object: ...
    def commit(self) -> object: ...
    def rollback(self) -> Any: ...
    def cursor(self) -> DbCursor: ...
    def executescript(self, sql: str, /) -> None: ...

const_functions: set[ConstType]
db_session: DBSessionContextManager
local: Local
orm_logger: Logger
sql_logger: Logger
suppress_debug_change: bool
special_functions: set[Callable]
sql_debugging: SQLDebuggingContextManager

def make_aggrfunc(std_func: Callable) -> Callable: ...

count: Callable[..., int]
sum: Callable[..., Numeric]
min: Callable
max: Callable
avg: Callable[..., float]
group_concat: Callable[..., str | None]
distinct: Callable

def _define_index(
    func_name: str, attrs: tuple[Attribute, ...], is_unique: bool = False
) -> None: ...
def _get_caches() -> list[SessionCache]: ...
def args2str(args: tuple | list | dict) -> str: ...
@decorator
def db_decorator(func: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> _T: ...
def commit() -> None: ...
def composite_index(*attrs) -> None: ...
def composite_key(*attrs) -> None: ...
def construct_batchload_criteria_list(
    alias: str | None,
    columns: Sequence[str],
    converters: Sequence[Converter],
    batch_size: int,
    row_value_syntax: bool,
    start: int = 0,
    from_seeds: bool = True,
) -> list[list]: ...
def delete(*args: str | Iterator | dict[str, object]) -> int: ...
def JOIN(expr: _T) -> _T: ...
@overload
def desc(expr: Attribute) -> DescWrapper: ...
@overload
def desc(expr: DescWrapper) -> Attribute: ...
@overload
def desc(expr: _AT) -> _AT: ...
def exists(*args: str | Iterator | dict[str, object]) -> bool: ...
def extract_vars(
    code_key: CodeKey,
    filter_num: int,
    extractors: dict[str, Callable],
    globals: dict[str, object],
    locals: dict[str, object],
    cells: dict[str, CellType] | None = None,
) -> tuple[QueryVars, VarTypes]: ...
def flush() -> None: ...
def format_arguments(arguments: tuple | list | dict) -> str: ...
def get(*args: str | Iterator | dict[str, object]) -> Any: ...
@overload
def get_globals_and_locals(
    args: (
        tuple[str | FunctionType]  # noqa: Y090
        | tuple[str | FunctionType, dict[str, object]]
        | tuple[str | FunctionType, dict[str, object], dict[str, object]]
    ),
    /,
    kwargs: dict[str, object] | None,
    frame_depth: int | None,
    from_generator: Literal[False] = False,
) -> tuple[str | FunctionType, dict[str, object], dict[str, object]]: ...
@overload
def get_globals_and_locals(
    args: (
        tuple[str | Iterator]  # noqa: Y090
        | tuple[str | Iterator, dict[str, object]]
        | tuple[str | Iterator, dict[str, object], dict[str, object]]
    ),
    /,
    kwargs: dict[str, object] | None,
    frame_depth: int | None,
    from_generator: Literal[True],
) -> tuple[str | GeneratorType, dict[str, object], dict[str, object]]: ...
def left_join(*args: str | Iterator | dict[str, object]) -> Query: ...
def log_orm(msg: str) -> None: ...
def log_sql(sql: str, arguments: tuple | list | dict | None = None) -> None: ...
def make_proxy(obj: Entity) -> EntityProxy: ...
def make_query(
    args: (
        tuple[str | Iterator]  # noqa: Y090
        | tuple[str | Iterator, dict[str, object]]
        | tuple[str | Iterator, dict[str, object], dict[str, object]]
    ),
    frame_depth: int | None,
    left_join: bool = False,
) -> Query: ...
def make_query_result_method_error_stub(
    name: str, title: str | None = None
) -> Callable: ...
def populate_criteria_list(
    criteria_list: list[
        (
            str
            | list[
                (
                    str
                    | list[str | None]
                    | list[str | tuple[int, None, None] | Converter | bool]
                )
            ]
        )
    ],
    columns: Iterable[str],
    converters: Iterable[Converter],
    operations: Iterable[str],
    params_count: int = 0,
    table_alias: str | None = None,
    optimistic: bool = False,
) -> int: ...
def rollback() -> None: ...
def safe_repr(obj: Entity) -> str: ...
def select(*args: str | Iterator | dict[str, object]) -> Query: ...
def set_sql_debug(debug: bool = True, show_values: bool | None = None) -> None: ...
def show(entity: Entity | EntityMeta) -> None: ...
def sql_debug(value: bool) -> None: ...
def strcut(s: str, width: int) -> str: ...
def string2ast(s: str) -> expr: ...
def throw_db_session_is_over(
    action: str, obj: Entity, attr: Attribute | None = None
): ...
def unpickle_entity(d: dict[str, Any]) -> Entity: ...
def unpickle_query(query_result: QueryResult) -> QueryResult: ...

class NotLoadedValueType: ...

NOT_LOADED: NotLoadedValueType

class DefaultValueType: ...

DEFAULT: DefaultValueType

class Attribute(Generic[_OAET_co]):
    args: tuple[int, ...]
    auto: bool
    cascade_delete: bool | None
    col_paths: list[str]
    column: str | None
    columns: list[str]
    composite_keys: list[tuple[tuple[Attribute, ...], int]]
    converters: list[Converter]
    default: OptAttrValue | Callable[..., OptAttrValue]
    entity: EntityMeta | MaybeNone
    fk_name: str | None
    hidden: bool
    id: int
    index: str | None
    interleave: bool | None
    is_basic: bool
    is_collection: bool
    is_discriminator: bool
    is_implicit: bool
    is_part_of_unique_index: bool | None
    is_pk: bool
    is_relation: bool
    is_required: bool
    is_string: bool
    is_unique: bool | None
    is_volatile: bool
    kwargs: dict[str, Any]
    lazy: bool
    lazy_sql_cache: tuple[str, Callable, tuple[int, ...]] | None
    name: str | MaybeNone
    nullable: bool
    optimistic: bool | None
    original_default: OptAttrValue | Callable
    pk_columns_offset: int
    pk_offset: int | None
    py_check: Callable[[object], bool] | None
    py_type: type[_OAET_co]
    reverse: Attribute
    reverse_index: str | None
    sql_default: str | bool | None
    sql_type: str | None
    type_has_empty_value: bool

    def __add__(attr, other: Any) -> Any: ...
    def __deepcopy__(attr, memo: dict[int, object]) -> Self: ...
    @overload
    def __get__(attr, obj: EntityMeta | None, cls: Any | None = None) -> Self: ...
    @overload
    def __get__(
        attr: Set[_ET_co], obj: Entity, cls: Any | None = None
    ) -> SetInstance[_ET_co]: ...
    @overload
    def __get__(attr, obj: Entity, cls: Any | None = None) -> _OAET_co: ...
    @overload
    def __get__(
        attr, obj: SetInstance[_ET_co], cls: Any | None = None
    ) -> Set[_ET_co]: ...
    @overload
    def __get__(attr, obj: Attribute | TrackedValue, cls: Any | None) -> Attribute: ...
    @overload
    def __get__(
        attr, obj: DescWrapper[_OAT_co] | Converter[_OAT_co], cls: Any | None = None
    ) -> Attribute[_OAT_co]: ...
    def __init__(
        attr,
        py_type: type[_OAET_co] | LiteralString | Callable[..., type[_OAET_co]],
        *args: int,
        **kwargs,
    ) -> None: ...
    def __lt__(attr, other: Any) -> bool: ...
    def __gt__(attr, other: Any) -> bool: ...
    @overload
    def __set__(
        attr,
        obj: Entity,
        new_val: (
            OptAttrValue
            | Entity
            | EntityProxy
            | TrackedValue
            | Table
            | Iterable[OptAttrValue | Entity]
        ),
        undo_funcs: list[Callable] | None = None,
    ) -> None: ...
    @overload
    def __set__(
        attr,
        obj: SetInstance[_ET_co],
        new_val: Set[_ET_co],
        undo_funcs: list[Callable] | None = None,
    ) -> None: ...
    @overload
    def __set__(
        attr,
        obj: Attribute | TrackedValue,
        new_val: Attribute,
        undo_funcs: list[Callable] | None = None,
    ) -> None: ...
    @overload
    def __set__(
        attr,
        obj: DescWrapper[_OAT_co] | Converter[_OAT_co],
        new_val: Attribute[_OAT_co],
        undo_funcs: list[Callable] | None = None,
    ) -> None: ...
    def _get_entity(
        attr, obj: Entity | None, entity: EntityMeta | None
    ) -> EntityMeta: ...
    def _init_(attr, entity: EntityMeta, name: str) -> None: ...
    @property
    def asc(attr) -> Self: ...
    def db_set(
        attr,
        obj: Entity,
        new_dbval: OptAttrValue | Entity | NotLoadedValueType,
        is_reverse_call: bool = False,
    ) -> None: ...
    def db_update_reverse(
        attr,
        obj: Entity,
        old_dbval: Entity | NotLoadedValueType | None,
        new_dbval: Entity | None,
    ) -> None: ...
    def describe(attr) -> str: ...
    @property
    def desc(attr) -> DescWrapper: ...
    def get(attr, obj: Entity) -> _OAET_co: ...
    def get_columns(attr) -> list[str]: ...
    def get_raw_values(
        attr, val: Entity | OptAttrValue
    ) -> tuple[OptAttrValue | _PkValue, ...]: ...
    def linked(attr) -> None: ...
    def load(attr, obj: Entity) -> Any: ...
    def parse_value(
        attr,
        row: DbRow,
        offsets: Sequence[int],
        dbvals_deduplication_cache: dict[
            type[OptAttrValue | Entity],
            dict[OptAttrValue | Entity, OptAttrValue | Entity],
        ],
    ) -> OptAttrValue | Entity: ...
    def update_reverse(
        attr,
        obj: Entity,
        old_val: Entity | NotLoadedValueType | None,
        new_val: Entity | None,
        undo_funcs: list[Callable],
    ) -> None: ...
    def validate(
        attr,
        val: Any,
        obj: Entity | None = None,
        entity: EntityMeta | None = None,
        from_db: bool = False,
    ) -> OptAttrValue | Entity | Any: ...

class Optional(Attribute[_OAET_co]):
    @overload
    def __get__(attr, obj: EntityMeta | None, cls: Any | None = None) -> Self: ...
    @overload
    def __get__(attr, obj: Entity, cls: Any | None = None) -> _OAET_co: ...
    @overload
    def __get__(
        attr, obj: SetInstance[_ET_co], cls: Any | None = None
    ) -> Set[_ET_co]: ...
    @overload
    def __get__(
        attr, obj: Attribute | TrackedValue, cls: Any | None = None
    ) -> Attribute: ...
    @overload
    def __get__(
        attr, obj: DescWrapper[_OAT_co] | Converter[_OAT_co], cls: Any | None = None
    ) -> Attribute[_OAT_co]: ...
    def validate(
        attr,
        val: Any,
        obj: Entity | None = None,
        entity: EntityMeta | None = None,
        from_db: bool = False,
    ) -> OptAttrValue | Entity: ...

class Required(Attribute[_AET_co]):
    @overload
    def __get__(attr, obj: EntityMeta | None, cls: Any | None = None) -> Self: ...
    @overload
    def __get__(attr, obj: Entity, cls: Any | None = None) -> _AET_co: ...
    @overload
    def __get__(
        attr, obj: SetInstance[_ET_co], cls: Any | None = None
    ) -> Set[_ET_co]: ...
    @overload
    def __get__(
        attr, obj: Attribute | TrackedValue, cls: Any | None = None
    ) -> Attribute: ...
    @overload
    def __get__(
        attr, obj: DescWrapper[_OAT_co] | Converter[_OAT_co], cls: Any | None = None
    ) -> Attribute[_OAT_co]: ...
    def validate(
        attr,
        val: Any,
        obj: Entity | None = None,
        entity: EntityMeta | None = None,
        from_db: bool = False,
    ) -> AttrValue | Entity: ...

class Discriminator(Required[_AT_co]):
    code2cls: dict[AttrValue, EntityMeta]

    @overload
    def __get__(attr, obj: EntityMeta | None, cls: Any | None = None) -> Self: ...
    @overload
    def __get__(attr, obj: Entity, cls: Any | None = None) -> _AT_co: ...
    @overload
    def __get__(
        attr, obj: SetInstance[_ET_co], cls: Any | None = None
    ) -> Set[_ET_co]: ...
    @overload
    def __get__(
        attr, obj: Attribute | TrackedValue, cls: Any | None = None
    ) -> Attribute: ...
    @overload
    def __get__(
        attr, obj: DescWrapper[_OAT_co] | Converter[_OAT_co], cls: Any | None = None
    ) -> Attribute[_OAT_co]: ...
    def __init__(attr, py_type: type[_AT_co], *args, **kwargs) -> None: ...
    def _init_(attr, entity: EntityMeta, name: str) -> None: ...
    @staticmethod
    def create_default_attr(
        entity: EntityMeta,
    ) -> None: ...
    def process_entity_inheritance(
        attr,
        entity: EntityMeta,
    ) -> None: ...
    def validate(
        attr,
        val: Any,
        obj: Entity | None = None,
        entity: EntityMeta | None = None,
        from_db: bool = False,
    ) -> AttrValue: ...

class Index:
    attrs: tuple[Attribute, ...]
    entity: EntityMeta | None
    is_pk: bool
    is_unique: bool

    def __init__(index, *attrs: Attribute, **options: dict[str, bool]) -> None: ...
    def _init_(
        index,
        entity: EntityMeta,
    ) -> None: ...

class PrimaryKey(Required[_AET_co]):
    @overload
    def __new__(
        cls,
        py_type: type[_AET_co] | LiteralString | Callable[..., type[_AET_co]],
        *args: int,
        **kwargs,
    ) -> Self: ...
    @overload
    def __new__(
        cls,
        *args: Attribute,
    ) -> None: ...

class Collection(Attribute[_ET_co]):
    cached_add_m2m_sql: tuple[str, Callable] | None
    cached_count_sql: tuple[str, Callable] | None
    cached_empty_sql: _CachedSql | None
    cached_load_sql: dict[int, tuple[str, Callable]]
    cached_remove_m2m_sql: tuple[str, Callable] | None
    nplus1_threshold: int
    reverse_column: str | None
    reverse_columns: list[str]
    reverse_fk_name: str | None
    symmetric: bool
    table: TableName
    wrapper_class: type[SetInstance]

    def __init__(
        attr,
        py_type: type[_ET_co] | LiteralString | Callable[..., type[_ET_co]],
        *args,
        **kwargs,
    ) -> None: ...
    def _init_(
        attr,
        entity: EntityMeta,
        name: str,
    ) -> None: ...

class SetIterator(Generic[_ET_co]):
    _iter: Iterator[_ET_co] | None
    _query: Query | None
    _wrapper: SetInstance[_ET_co]

    def __init__(self, wrapper: SetInstance[_ET_co]) -> None: ...
    def __iter__(self) -> Self: ...
    def _get_query(self) -> Query: ...
    def _get_type_(self) -> QueryType: ...
    def _normalize_var(self, query_type: QueryType) -> tuple[QueryType, Query]: ...
    def next(self) -> _ET_co: ...
    __next__ = next

class SetInstance(Generic[_ET_co]):
    _attr_: Set[_ET_co]
    _attrnames_: tuple[str, ...]
    _obj_: _ET_co

    _parent_: ClassVar

    def __init__(wrapper, obj: _ET_co, attr: Set[_ET_co]) -> None: ...
    def __getattr__(self, name: str) -> Any: ...
    def __nonzero__(wrapper) -> bool: ...
    def __len__(wrapper) -> int: ...
    def __iter__(wrapper) -> SetIterator[_ET_co]: ...
    def __eq__(wrapper, other: Any) -> bool: ...  # noqa: Y032
    def __ne__(wrapper, other: Any) -> bool: ...  # noqa: Y032
    def __add__(wrapper, new_items: Iterable[Entity]) -> Self: ...
    def __sub__(wrapper, items: Iterable[Entity]) -> Self: ...
    def __contains__(wrapper, item: Entity) -> bool: ...
    def __iadd__(wrapper, items: Iterable[Entity]) -> Self: ...
    def __isub__(wrapper, items: Iterable[Entity]) -> Self: ...
    def add(wrapper, new_items: Iterable[Entity]) -> None: ...
    def clear(wrapper) -> None: ...
    def copy(wrapper, obj: Any) -> set[Entity]: ...
    def count(wrapper) -> int: ...
    def create(wrapper, **kwargs) -> _ET_co: ...
    def is_empty(wrapper) -> bool: ...
    def limit(
        wrapper, limit: int | None = None, offset: int | None = None
    ) -> QueryResult: ...
    def load(wrapper) -> None: ...
    def order_by(wrapper, *args) -> QueryResult: ...
    def page(wrapper, pagenum: int, pagesize: int = 10) -> QueryResult: ...
    def random(wrapper, limit: int) -> QueryResult: ...
    def remove(wrapper, items: Iterable[Entity]) -> None: ...
    def select(wrapper, *args, **kwargs) -> Query: ...
    filter = select
    def sort_by(wrapper, *args) -> QueryResult: ...

class Set(Collection[_ET_co]):
    def add_m2m(attr, added: set[tuple[Entity, Entity]]) -> None: ...
    def construct_sql_m2m(
        attr, batch_size: int = 1, items_count: int = 0
    ) -> tuple[str, Callable]: ...
    def copy(attr, obj: Entity) -> set[Entity]: ...
    def db_reverse_add(attr, objects: Iterable[Entity], item: Entity) -> None: ...
    def drop_table(attr, with_all_data: bool = False) -> None: ...
    def get_m2m_columns(attr, is_reverse: bool = False) -> list[str]: ...
    def load(attr, obj: Entity, items: Iterable[Entity] | None = None) -> SetData: ...
    def prefetch_load_all(attr, objects: Iterable[Entity]) -> set[Entity]: ...
    def remove_m2m(attr, removed: set[tuple[Entity, Entity]]) -> None: ...
    def reverse_add(
        attr,
        objects: Iterable[Entity],
        item: Entity,
        undo_funcs: list[Callable],
    ) -> None: ...
    def reverse_remove(
        attr,
        objects: Iterable[Entity],
        item: Entity,
        undo_funcs: list[Callable],
    ) -> None: ...
    def validate(
        attr,
        val: Entity | Iterable[Entity] | DefaultValueType,
        obj: Entity | None = None,
        entity: EntityMeta | None = None,
        from_db: bool = False,
    ) -> set[Entity]: ...

class DBSessionContextManager:
    allowed_exceptions: Iterable[type[Exception]] | Callable
    ddl: bool
    immediate: bool
    optimistic: bool
    retry: int
    retry_exceptions: Iterable[type[Exception]] | Callable
    serializable: bool
    show_values: bool | None
    sql_debug: bool | None
    strict: bool

    @overload
    def __call__(db_session, /, **kwargs) -> Self: ...
    @overload
    def __call__(db_session, func: Callable[_P, _T], /) -> Callable[_P, _T]: ...
    def __enter__(db_session) -> None: ...
    def __exit__(
        db_session,
        exc_type: type[BaseException] | None = None,
        exc: BaseException | None = None,
        tb: TracebackType | None = None,
    ) -> None: ...
    def __init__(
        db_session,
        retry: int = 0,
        immediate: bool = False,
        ddl: bool = False,
        serializable: bool = False,
        strict: bool = False,
        optimistic: bool = True,
        retry_exceptions: Iterable[type[Exception]] | Callable = ...,
        allowed_exceptions: Iterable[type[Exception]] | Callable = (),
        sql_debug: bool | None = None,
        show_values: bool | None = None,
    ) -> None: ...
    def _commit_or_rollback(
        db_session,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
    def _enter(db_session) -> None: ...
    @overload
    def _wrap_coroutine_or_generator_function(
        db_session, gen_func: Callable[_P, _CT]
    ) -> Callable[_P, _CT]: ...
    @overload
    def _wrap_coroutine_or_generator_function(
        db_session, gen_func: Callable[_P, _GT]
    ) -> Callable[_P, _GT]: ...
    def _wrap_function(db_session, func: Callable[_P, _T]) -> Callable[_P, _T]: ...

class Database:
    _Entity: TypeAlias = Entity

    _constructed_sql_cache: dict[HashableDict, _CachedSql | CachedSqlSimple]
    _dblocal: DbLocal
    _global_stats: dict[str | None, QueryStat]
    _global_stats_lock: RLock
    _insert_cache: dict[
        tuple[str, Unpack[tuple[str, ...]], str] | tuple[str, Unpack[tuple[str, ...]]],
        CachedSqlSimple,
    ]
    _on_connect_funcs: list[tuple[Callable, str | None]]
    _translator_cache: dict[QueryKey, SQLTranslator]
    entities: dict[str, EntityMeta]
    id: int
    on_connect: OnConnectDecorator
    priority: int
    provider: DBAPIProvider | MaybeNone
    provider_name: str | None
    schema: DBSchema | MaybeNone
    Entity: type[_Entity]

    def __init__(self, *args, **kwargs) -> None: ...
    def __deepcopy__(self, memo: dict[int, object]) -> Self: ...
    def __getattr__(self, name: str) -> EntityMeta: ...
    def _ast2sql(database, sql_ast: list) -> tuple[str, Callable]: ...
    def bind(self, *args, **kwargs) -> None: ...
    def _bind(self, *args, **kwargs) -> None: ...
    def _drop_tables(
        database,
        table_names: Iterable[TableName],
        if_exists: bool,
        with_all_data: bool,
        try_normalized: bool = False,
    ) -> None: ...
    def _exec_raw_sql(
        database,
        sql: str,
        globals: dict[str, object] | None,
        locals: dict[str, object] | None,
        frame_depth: int,
        start_transaction: bool = False,
    ) -> DbCursor: ...
    @overload
    def _exec_sql(
        database,
        sql: str,
        arguments: Any | None = None,
        *,
        returning_id: Literal[False] = False,
        start_transaction: bool = False,
    ) -> DbCursor: ...
    @overload
    def _exec_sql(
        database,
        sql: str,
        arguments: Any | None = None,
        *,
        returning_id: Literal[True],
        start_transaction: bool = False,
    ) -> int: ...
    def _get_cache(database) -> SessionCache: ...
    def _get_table_name(
        database,
        table_name: TableName | EntityMeta | Set,
    ) -> TableName: ...
    def _update_local_stat(database, sql: str, query_start_time: float) -> None: ...
    def call_on_connect(database, con: DbConnection) -> None: ...
    def check_tables(database) -> None: ...
    def commit(database) -> None: ...
    def create_tables(database, check_tables: bool = False) -> None: ...
    def disconnect(database) -> None: ...
    def drop_table(
        database,
        table_name: TableName,
        if_exists: bool = False,
        with_all_data: bool = False,
    ) -> None: ...
    def drop_all_tables(database, with_all_data: bool = False) -> None: ...
    def execute(
        database,
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
    ) -> DbCursor: ...
    def exists(
        database,
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
    ) -> bool: ...
    def flush(database) -> None: ...
    def generate_mapping(
        database,
        filename: str | None = None,
        check_tables: bool = True,
        create_tables: bool = False,
    ) -> None: ...
    def get(
        database,
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
    ) -> OptAttrValue: ...
    def get_connection(database) -> DbConnection: ...
    @property
    def global_stats(database) -> dict[str | None, QueryStat]: ...
    def insert(
        database,
        table_name: TableName | EntityMeta | type[Collection] | Set,
        returning: str | None = None,
        **kwargs,
    ) -> int | None: ...
    @property
    def last_sql(database) -> str | MaybeNone: ...
    @property
    def local_stats(database) -> dict[str | None, QueryStat]: ...
    def merge_local_stats(database) -> None: ...
    def rollback(database) -> None: ...
    def select(
        database,
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        frame_depth: int = 0,
    ) -> list[tuple[OptAttrValue, ...]] | list[OptAttrValue]: ...
    def to_json(
        database,
        data: _Entity | QueryResult,
        include: Iterable[Attribute] = (),
        exclude: Iterable[Attribute] = (),
        converter: Callable | None = None,
        with_schema: bool = True,
        schema_hash: str | None = None,
    ) -> str: ...

class DbLocal(localbase):
    stats: dict[str | None, QueryStat]
    last_sql: str | None

    def __init__(dblocal) -> None: ...

class DescWrapper(Generic[_OAT_co]):
    attr: Attribute[_OAT_co]

    def __init__(self, attr: Attribute[_OAT_co]) -> None: ...
    def __call__(self) -> Self: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class EntityMeta(type):
    _adict_: dict[str, Attribute]
    _all_bases_: set[EntityMeta]
    _all_bits_: int
    _all_bits_except_volatile_: int
    _attrnames_cache_: dict[
        tuple[tuple[str, ...] | str | None, tuple[str, ...] | str | None, bool, bool],
        tuple[Attribute, ...],
    ]
    _attrs_: list[Attribute]
    _attrs_with_columns_: list[Attribute]
    _batchload_sql_cache_: dict[
        tuple[int, Attribute | None, bool, frozenset[Attribute] | tuple[()]],
        _CachedSql,
    ]
    _base_attrs_: list[Attribute]
    _bits_: dict[Attribute, int]
    _bits_except_volatile_: dict[Attribute, int]
    _cached_max_id_sql_: str | None
    _columns_: list[str]
    _columns_without_pk_: list[str]
    _composite_keys_: list[tuple[Attribute, ...]]
    _converters_: list[Converter]
    _converters_without_pk_: list[Converter]
    _database_: Database | MaybeNone
    _default_genexpr_: GeneratorExp
    _delete_sql_cache_: dict[tuple[()], tuple[str, Callable]]
    _direct_bases_: list[EntityMeta]
    _discriminator_: AttrValue | MaybeNone
    _discriminator_attr_: Discriminator | None
    _find_sql_cache_: dict[
        tuple[tuple[Attribute, ...], bool, int | None, bool, bool, bool],
        _CachedSql,
    ]
    _id_: int
    _indexes_: list[Index]
    _insert_sql_cache_: dict[tuple[Attribute, ...], tuple[str, Callable]]
    _interleave_: Attribute[Entity] | None
    _keys_: list[tuple[Attribute, ...]]
    _load_sql_cache_: dict[tuple[Attribute, ...], _CachedSql]
    _multiset_subclass_: type[Multiset] | None
    _new_attrs_: list[Attribute]
    _pk_: PrimaryKey | tuple[Attribute, ...]
    _pk_attrs_: tuple[Attribute, ...]
    _pk_columns_: list[str] | MaybeNone
    _pk_converters_: list[Converter]
    _pk_is_composite_: bool
    _pk_nones_: tuple[None, ...]
    _pk_paths_: list[str]
    _propagation_mixin_: type | None
    _root_: EntityMeta
    _set_wrapper_subclass_: type[SetInstance] | None
    _simple_keys_: list[Attribute]
    _subclass_adict_: dict[str, Attribute]
    _subclass_attrs_: list[Attribute]
    _subclasses_: set[EntityMeta]
    _table_: TableName | MaybeNone
    _table_options_: dict[str, object]
    _update_sql_cache_: dict[
        tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]], tuple[str, Callable]
    ]
    classtype: Discriminator
    id: PrimaryKey[int] | Any

    def __getitem__(entity, key: _PkValue) -> Entity: ...
    def __init__(
        entity,
        name: str,
        bases: tuple[type, ...],
        cls_dict: dict[str, object],
    ) -> None: ...
    def __iter__(entity) -> EntityIter: ...
    @staticmethod
    def __new__(
        meta: type[_typeshed.Self],
        name: str,
        bases: tuple[type, ...],
        cls_dict: dict[str, object],
    ) -> _typeshed.Self: ...
    def _check_table_options_(entity) -> None: ...
    def _construct_batchload_sql_(
        entity, batch_size: int, attr: Attribute | None = None, from_seeds: bool = True
    ) -> _CachedSql: ...
    def _construct_discriminator_criteria_(
        entity, alias: str | None = None
    ) -> list[str | list[str | None] | list[list[str]] | list[str]] | None: ...
    def _construct_select_clause_(
        entity,
        alias: str | None = None,
        distinct: bool = False,
        query_attrs: dict[Attribute, bool] | tuple[()] = (),
        all_attributes: bool = False,
    ) -> tuple[Sequence[str | list[str]], AttrOffsets]: ...
    def _construct_sql_(
        entity,
        query_attrs: dict[Attribute, bool],
        order_by_pk: bool = False,
        limit: int | None = None,
        for_update: bool = False,
        nowait: bool = False,
        skip_locked: bool = False,
    ) -> _CachedSql: ...
    def _fetch_objects(
        entity,
        cursor: DbCursor,
        attr_offsets: AttrOffsets | None,
        max_fetch_count: int | None = None,
        for_update: bool = False,
        used_attrs: set[Attribute] | tuple[()] = (),
    ) -> list[Entity]: ...
    def _find_by_sql_(
        entity,
        max_fetch_count: int | None,
        sql: str,
        globals: dict[str, object] | None,
        locals: dict[str, object] | None,
        frame_depth: int,
    ) -> list[Entity]: ...
    def _find_in_cache_(
        entity, pkval: _KeyValue, avdict: _AvDict, for_update: bool = False
    ) -> tuple[Entity | None, bool]: ...
    def _find_in_db_(
        entity,
        avdict: _AvDict,
        unique: bool = False,
        for_update: bool = False,
        nowait: bool = False,
        skip_locked: bool = False,
    ) -> Entity | None: ...
    def _find_one_(
        entity,
        kwargs: dict[str, Any],
        for_update: bool = False,
        nowait: bool = False,
        skip_locked: bool = False,
    ) -> Entity: ...
    def _get_attrs_(
        entity,
        only: Iterable[str] | str | None = None,
        exclude: Iterable[str] | str | None = None,
        with_collections: bool = False,
        with_lazy: bool = False,
    ) -> tuple[Attribute, ...]: ...
    def _get_by_raw_pkval_(
        entity,
        raw_pkval: Sequence[OptAttrValue],
        for_update: bool = False,
        from_db: bool = True,
        seed: bool = True,
    ) -> Entity: ...
    def _get_from_identity_map_(
        entity,
        pkval: _PkValue | None,
        status: str,
        for_update: bool = False,
        undo_funcs: list[Callable] | None = None,
        obj_to_init: Entity | None = None,
    ) -> Entity: ...
    def _get_multiset_subclass_(entity) -> type[Multiset]: ...
    def _get_pk_columns_(entity) -> list[str]: ...
    def _get_propagation_mixin_(entity) -> type: ...
    def _get_set_wrapper_subclass_(entity) -> type[SetInstance]: ...
    def _initialize_bits_(entity) -> None: ...
    def _link_reverse_attrs_(entity) -> None: ...
    def _load_many_(entity, objects: Iterable[Entity]) -> None: ...
    def _parse_row_(
        entity,
        row: DbRow,
        attr_offsets: AttrOffsets,
    ) -> tuple[EntityMeta, _PkValue, _AvDict]: ...
    def _query_from_args_(
        entity,
        args: tuple[str | Callable | Iterator],  # noqa: Y090
        kwargs: dict[Any, Any],
        frame_depth: int,
    ) -> Query: ...
    def _resolve_attr_types_(entity) -> None: ...
    def _select_all(entity) -> Query: ...
    def _set_rbits(
        entity,
        objects: Iterable[Entity],
        attrs: set[Attribute],
    ) -> None: ...
    def describe(entity) -> str: ...
    def drop_table(entity, with_all_data: bool = False) -> None: ...
    def exists(entity, *args, **kwargs) -> bool: ...
    @overload
    def get(entity: type[_ET], *args, **kwargs) -> _ET | None: ...
    @overload
    def get(entity, *args, **kwargs) -> Entity | None: ...
    @overload
    def get_by_sql(
        entity: type[_ET],
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
    ) -> _ET | None: ...
    @overload
    def get_by_sql(
        entity,
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
    ) -> Entity | None: ...
    @overload
    def get_for_update(entity: type[_ET], *args, **kwargs) -> _ET | None: ...
    @overload
    def get_for_update(entity, *args, **kwargs) -> Entity | None: ...
    def select(entity, *args, **kwargs) -> Query: ...
    @overload
    def select_by_sql(
        entity: type[_ET],
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
    ) -> list[_ET]: ...
    @overload
    def select_by_sql(
        entity,
        sql: str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
    ) -> list[Entity]: ...
    @overload
    def select_random(entity: type[_ET], limit: int) -> list[_ET]: ...
    @overload
    def select_random(entity, limit: int) -> list[Entity]: ...

class Entity(metaclass=EntityMeta):
    _attrs_with_columns_: Sequence[Attribute]
    _dbvals_: dict[Attribute, OptAttrValue | Entity] | MaybeNone
    _newid_: int | None
    _pkval_: _PkValue | MaybeNone
    _rbits_: int | MaybeNone
    _save_pos_: int | None
    _session_cache_: SessionCache | MaybeNone
    _status_: str | None
    _vals_: dict[Attribute, Any] | MaybeNone
    _wbits_: int | MaybeNone

    def __init__(obj, *args, **kwargs) -> None: ...
    def __add__(entity, other: list[None]) -> list[Entity | None]: ...
    def __lt__(entity, other: Any) -> bool: ...
    def __le__(entity, other: Any) -> bool: ...
    def __gt__(entity, other: Any) -> bool: ...
    def __ge__(entity, other: Any) -> bool: ...
    def __getattr__(obj, name: str) -> Any: ...
    def __setattr__(obj, name: str, value: Any) -> None: ...
    def _after_save_(obj, status: str) -> None: ...
    def _attr_changed_(obj, attr: Attribute) -> None: ...
    @classmethod
    def _attrs_with_bit_(
        entity, attrs: Sequence[Attribute], mask: int = -1
    ) -> Iterator[Attribute]: ...
    def _before_save_(obj) -> None: ...
    def _cmp_(entity, other: Self) -> int: ...
    def _construct_optimistic_criteria_(
        obj,
    ) -> tuple[list[str], list[str], list[Converter], list[OptAttrValue]]: ...
    def _db_set_(obj, avdict: _AvDict, unpickling: bool = False) -> None: ...
    def _delete_(obj, undo_funcs: list[Callable] | None = None) -> None: ...
    def _get_raw_pkval_(
        obj,
    ) -> tuple[_PkValue, ...]: ...
    def _keyargs_to_avdicts_(
        obj, kwargs: dict[str, list[Self] | str | int | None]
    ) -> tuple[_AvDict, dict[Collection, object]]: ...
    def _load_(obj) -> None: ...
    def load(obj, *attrs: str | Attribute) -> None: ...
    @classmethod
    def _prefetch_load_all_(entity, objects: Iterable[Self]) -> None: ...
    def _save_(obj, dependent_objects: Iterable[Self] | None = None) -> None: ...
    def _save_created_(obj) -> None: ...
    def _save_deleted_(obj) -> None: ...
    def _save_principal_objects_(obj, dependent_objects: list[Self] | None) -> None: ...
    def _save_updated_(obj) -> None: ...
    def _update_dbvals_(
        obj,
        after_create: bool,
        new_dbvals: dict[Attribute, AttrValue | Self],
    ) -> None: ...
    def after_delete(obj) -> None: ...
    def after_insert(obj) -> None: ...
    def after_update(obj) -> None: ...
    def before_delete(obj) -> None: ...
    def before_insert(obj) -> None: ...
    def before_update(obj) -> None: ...
    def delete(obj) -> None: ...
    def flush(obj) -> None: ...
    def get_pk(obj) -> _PkValue | tuple[_PkValue, ...]: ...
    def set(obj, **kwargs) -> None: ...
    def to_dict(
        obj,
        only: Iterable[str] | str | None = None,
        exclude: Iterable[str] | str | None = None,
        with_collections: bool = False,
        with_lazy: bool = False,
        related_objects: bool = False,
    ) -> dict[str, object]: ...
    def to_json(
        obj,
        include: Iterable[Attribute] = (),
        exclude: Iterable[Attribute] = (),
        converter: Callable | None = None,
        with_schema: bool = True,
        schema_hash: str | None = None,
    ) -> str: ...

class EntityIter:
    def __init__(
        self,
        entity: EntityMeta,
    ) -> None: ...
    def next(self) -> Any: ...
    __next__ = next

class EntityProxy:
    _entity_: type[Entity]
    _obj_pk_: tuple[AttrValue, ...] | AttrValue

    def __eq__(self, other: object) -> bool: ...
    def __getattr__(self, name: str) -> Any: ...
    def __init__(self, obj: Entity) -> None: ...
    def __ne__(self, other: object) -> bool: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def _get_object(self) -> Entity: ...

class Local(localbase):
    db2cache: dict[Database, SessionCache]
    db_context_counter: int
    db_session: DBSessionContextManager | None
    debug: bool
    debug_stack: list[tuple[bool, bool | None]]
    prefetch_context_stack: list[PrefetchContext]
    show_values: bool | None

    def __init__(local) -> None: ...
    @property
    def prefetch_context(local) -> PrefetchContext | None: ...

class Multiset:
    _attrnames_: tuple[str, ...]
    _items_: dict[AttrValue, int]
    _obj_: Entity

    def __init__(
        multiset,
        obj: Entity,
        attrnames: tuple[str, ...],
        items: list[AttrValue] | dict[AttrValue, int],
    ) -> None: ...
    def __len__(multiset) -> int: ...
    def __iter__(multiset) -> Iterator[AttrValue]: ...
    def __eq__(multiset, other: object) -> bool: ...
    def __ne__(multiset, other: object) -> bool: ...

class OnConnectDecorator:
    provider: str | None
    database: Database

    @overload
    def __call__(self, func: str, provider: None = None) -> Self: ...
    @overload
    def __call__(
        self, func: Callable | None = None, provider: str | None = None
    ) -> Self: ...
    def __init__(self, database: Database, provider: str | None) -> None: ...
    @staticmethod
    def check_provider(provider: str | None) -> None: ...

class PrefetchContext:
    database: Database | None
    attrs_to_prefetch_dict: dict[EntityMeta, set[Attribute]]
    entities_to_prefetch: set[EntityMeta]
    relations_to_prefetch_cache: dict[EntityMeta, tuple[Attribute, ...]]

    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    def __init__(self, database: Database | None = None) -> None: ...
    def copy(self) -> PrefetchContext: ...
    def get_frozen_attrs_to_prefetch(
        self, entity: EntityMeta
    ) -> frozenset[Attribute]: ...
    def get_relations_to_prefetch(
        self, entity: EntityMeta
    ) -> tuple[Attribute, ...]: ...

class Query:
    _code_key: CodeKey
    _database: Database
    _distinct: bool | None
    _filter_num: int
    _filters: tuple[tuple[str, Unpack[tuple]], ...]
    _for_update: bool
    _key: QueryKey
    _next_kwarg_id: int
    _nowait: bool
    _prefetch: bool
    _prefetch_context: PrefetchContext
    _skip_locked: bool
    _translator: SQLTranslator
    _vars: QueryVars

    def __getitem__(query, key: slice) -> QueryResult: ...
    def __init__(
        query,
        code_key: CodeKey,
        tree: GeneratorExp,
        globals: dict[str, object],
        locals: dict[str, object],
        cells: dict[str, CellType] | None = None,
        left_join: bool = False,
    ) -> None: ...
    def __iter__(query) -> QueryResultIterator: ...
    def __len__(query) -> int: ...
    def __reduce__(query) -> tuple[Callable, tuple[QueryResult]]: ...  # noqa: Y090
    def _actual_fetch(
        query, limit: int | None = None, offset: int | None = None
    ) -> list[Any]: ...
    def _aggregate(
        query,
        aggr_func_name: str,
        distinct: bool | None = None,
        sep: str | None = None,
    ) -> Any: ...
    def _apply_kwargs(
        query, kwargs: dict[str, object], original_names: bool = False
    ) -> Query: ...
    def _clone(query, **kwargs) -> Query: ...
    def _construct_sql_and_arguments(
        query,
        limit: int | None = None,
        offset: int | None = None,
        range: None = None,
        aggr_func_name: str | None = None,
        aggr_func_distinct: bool | None = None,
        sep: str | None = None,
    ) -> tuple[
        str,
        AdapterResult,
        AttrOffsets | None,
        QueryKey | None,
    ]: ...
    def _do_prefetch(
        query, query_result: Iterable[Entity | tuple[str, Entity]]
    ) -> None: ...
    def _get_query(query) -> Self: ...
    def _get_translator(
        query, query_key: QueryKey, vars: QueryVars
    ) -> tuple[SQLTranslator | None, QueryVars]: ...
    def _get_type_(query) -> QueryType: ...
    def _normalize_var(query, query_type: QueryType) -> tuple[QueryType, Self]: ...
    def _order_by(query, method_name: str, *args) -> Self: ...
    def _process_lambda(
        query,
        func: str | Callable,
        globals: dict[str, object],
        locals: dict[str, object],
        order_by: bool = False,
        original_names: bool = False,
    ) -> Query: ...
    def _reapply_filters(query, translator: SQLTranslator) -> SQLTranslator: ...
    def avg(query, distinct: bool | None = None) -> float: ...
    def count(query, distinct: bool | None = None) -> int: ...
    def delete(query, bulk: bool | None = None) -> int: ...
    def distinct(query) -> Query: ...
    def exists(query) -> bool: ...
    def _fetch(
        query, limit: int | None = None, offset: int | None = None, lazy: bool = False
    ) -> QueryResult: ...
    def fetch(
        query, limit: int | None = None, offset: int | None = None
    ) -> QueryResult: ...
    @overload
    def filter(
        query,
        func: Callable | str | RawSQL,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        /,
    ) -> Self: ...
    @overload
    def filter(query, **kwargs) -> Self: ...
    def first(query) -> Any: ...
    def for_update(query, nowait: bool = False, skip_locked: bool = False) -> Query: ...
    def get(query) -> Any: ...
    def get_sql(query) -> str: ...
    def group_concat(
        query, sep: str | None = None, distinct: bool | None = None
    ) -> str: ...
    def limit(
        query, limit: int | None = None, offset: int | None = None
    ) -> QueryResult: ...
    def max(query) -> int: ...
    def min(query) -> int: ...
    @overload
    def order_by(query, *attrs: Attribute | DescWrapper) -> Query: ...
    @overload
    def order_by(query, *pos: int) -> Query: ...
    @overload
    def order_by(
        query,
        func: Callable | str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        /,
    ) -> Query: ...
    @overload
    def order_by(query, raw: RawSQL | None, /) -> Query: ...
    @overload
    def sort_by(query, *attrs: Attribute | DescWrapper) -> Query: ...
    @overload
    def sort_by(query, *pos: int) -> Query: ...
    @overload
    def sort_by(
        query,
        func: Callable | str,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        /,
    ) -> Query: ...
    @overload
    def sort_by(query, raw: RawSQL | None, /) -> Query: ...
    def page(query, pagenum: int, pagesize: int = 10) -> QueryResult: ...
    def prefetch(query, *args: EntityMeta | Attribute) -> Query: ...
    def random(query, limit: int) -> QueryResult: ...
    def show(
        query, width: int | None = None, stream: StringIO | None = None
    ) -> None: ...
    def sum(query, distinct: bool | None = None) -> int: ...
    def to_json(
        query,
        include: Iterable[Attribute] = (),
        exclude: Iterable[Attribute] = (),
        converter: Callable | None = None,
        with_schema: bool = True,
        schema_hash: str | None = None,
    ) -> str: ...
    @overload
    def where(
        query,
        func: Callable | str | RawSQL,
        globals: dict[str, object] | None = None,
        locals: dict[str, object] | None = None,
        /,
    ) -> Self: ...
    @overload
    def where(query, **kwargs) -> Self: ...
    def without_distinct(query) -> Query: ...

class QueryResult:
    _col_names: list[str]
    _expr_type: ExprType
    _items: list[Any] | None
    _limit: int | None
    _offset: int | None
    _query: Query

    def __add__(self, other: Iterable) -> list[Entity]: ...
    def __contains__(self, item: object) -> bool: ...
    def __eq__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __lt__(self, other: Any) -> bool: ...
    def __le__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...
    def __ge__(self, other: Any) -> bool: ...
    def __getitem__(self, key: slice | int) -> Any: ...
    def __getstate__(
        self,
    ) -> tuple[list[Entity], int | None, int | None, ExprType, list[str]]: ...
    def __init__(
        self, query: Query, limit: int | None, offset: int | None, lazy: bool
    ) -> None: ...
    def __iter__(self) -> QueryResultIterator: ...
    def __len__(self) -> int: ...
    def __radd__(self, other: Iterable) -> list[Entity]: ...
    def __reversed__(self) -> Iterator: ...
    def __setstate__(
        self, state: tuple[list[Entity], int | None, int | None, EntityMeta, list[str]]
    ) -> None: ...
    def _get_items(self) -> list: ...
    def _get_query(self) -> Query: ...
    def _get_type_(self) -> QueryType | tuple[ExprType, ...]: ...
    def _normalize_var(
        self, query_type: QueryType
    ) -> (
        tuple[QueryType, Query]
        | tuple[
            tuple[ExprType, ...], tuple[tuple[type[OptAttrValue], OptAttrValue], ...]
        ]
    ): ...
    def _other_items(self, other: list[Entity] | list[OptAttrValue]) -> list: ...
    def index(self, item: object) -> int: ...
    def reverse(self) -> None: ...
    def show(
        self, width: int | None = None, stream: StringIO | TextIO | None = None
    ) -> None: ...
    def shuffle(self) -> None: ...
    def sort(self, *args, **kwargs) -> None: ...
    def to_list(self) -> list[Entity]: ...
    def to_json(
        self,
        include: Iterable[Attribute] = (),
        exclude: Iterable[Attribute] = (),
        converter: Callable | None = None,
        with_schema: bool = True,
        schema_hash: str | None = None,
    ) -> str: ...

class QueryResultIterator:
    _position: int
    _query_result: QueryResult

    def __init__(self, query_result: QueryResult) -> None: ...
    __next__ = next
    def __length_hint__(self) -> int: ...
    def _get_type_(self) -> QueryType: ...
    def _normalize_var(self, query_type: QueryType) -> tuple[QueryType, Query]: ...
    def next(self) -> Any: ...

class QueryStat:
    cache_count: int
    db_count: int
    max_time: float | MaybeNone
    min_time: float | MaybeNone
    sql: str
    sum_time: float | MaybeNone

    def __init__(stat, sql: str | None, duration: float | None = None) -> None: ...
    def merge(stat, stat2: QueryStat) -> None: ...
    def query_executed(stat, duration: float) -> None: ...
    @property
    def avg_time(stat) -> float | None: ...

class SQLDebuggingContextManager:
    def __init__(self, debug: bool = True, show_values: bool | None = None) -> None: ...
    def __call__(db_session, *args, **kwargs) -> type[Self] | Callable: ...
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    def _wrap_function(db_session, func: Callable[_P, _T]) -> Callable[_P, _T]: ...
    def _wrap_generator_function(
        db_session, func: Callable[_P, _T]
    ) -> Callable[_P, _T]: ...

class SessionCache:
    collection_statistics: dict[Set, int] | MaybeNone
    connection: DbConnection | MaybeNone
    database: Database
    db_session: DBSessionContextManager | None
    dbvals_deduplication_cache: (
        dict[
            type[OptAttrValue | Entity],
            dict[OptAttrValue | Entity, OptAttrValue | Entity],
        ]
        | MaybeNone
    )
    for_update: set[Entity] | MaybeNone
    immediate: bool
    in_transaction: bool
    indexes: (
        dict[
            Attribute | tuple[Attribute, ...],
            dict[_KeyValue, Entity],
        ]
        | MaybeNone
    )
    is_alive: bool
    max_id_cache: dict[Attribute, int] | MaybeNone
    modified: bool
    modified_collections: dict[Set, set[Entity]] | MaybeNone
    noflush_counter: int
    num: int
    objects: set[Entity] | MaybeNone
    objects_to_save: list[Entity | None] | MaybeNone
    query_results: dict[QueryKey, list[Entity]] | MaybeNone
    saved_fk_state: bool | None
    saved_objects: list[tuple[Entity, LiteralString]] | MaybeNone
    seeds: dict[tuple[Attribute, ...], set[Entity]] | MaybeNone

    def __init__(cache, database: Database) -> None: ...
    def _calc_modified_m2m(
        cache,
    ) -> dict[Collection, tuple[set[Any], set[Any]]]: ...
    def call_after_save_hooks(cache) -> None: ...
    def close(cache, rollback: bool = True) -> None: ...
    def commit(cache) -> None: ...
    def connect(cache) -> DbConnection: ...
    def db_update_composite_index(
        cache,
        obj: Entity,
        attrs: tuple[Attribute, ...],
        prev_vals: tuple[OptAttrValue, ...],
        new_vals: tuple[OptAttrValue, ...],
    ) -> None: ...
    def db_update_simple_index(
        cache,
        obj: Entity,
        attr: Attribute,
        old_dbval: OptAttrValue | Entity,
        new_dbval: OptAttrValue | Entity,
    ) -> None: ...
    def flush(cache) -> None: ...
    def flush_disabled(cache) -> Iterator[None]: ...
    def prepare_connection_for_query_execution(cache) -> DbConnection: ...
    def reconnect(cache, exc: Exception): ...
    def release(cache) -> None: ...
    def rollback(cache) -> None: ...
    def update_composite_index(
        cache,
        obj: Entity,
        attrs: tuple[Attribute, ...],
        prev_vals: tuple[OptAttrValue, ...],
        new_vals: tuple[OptAttrValue, ...],
        undo: list[Any],
    ) -> None: ...
    def update_simple_index(
        cache,
        obj: Entity,
        attr: Attribute,
        old_val: OptAttrValue | NotLoadedValueType,
        new_val: OptAttrValue,
        undo: list[Any],
    ) -> None: ...

class SetData(set):
    absent: set[Entity] | None
    added: set[Entity] | None
    count: int | None
    is_fully_loaded: bool
    removed: set[Entity] | None

    def __init__(setdata) -> None: ...

class OrmError(Exception): ...
class ERDiagramError(OrmError): ...
class DBSchemaError(OrmError): ...
class MappingError(OrmError): ...
class BindingError(OrmError): ...
class TableDoesNotExist(OrmError): ...
class TableIsNotEmpty(OrmError): ...
class ConstraintError(OrmError): ...
class CacheIndexError(OrmError): ...

class ObjectNotFound(OrmError):
    entity: EntityMeta
    pkval: _PkValue | None

    def __init__(
        exc,
        entity: EntityMeta,
        pkval: _PkValue | None = None,
    ) -> None: ...

class MultipleObjectsFoundError(OrmError): ...
class TooManyObjectsFoundError(OrmError): ...
class OperationWithDeletedObjectError(OrmError): ...
class RowNotFound(OrmError): ...
class MultipleRowsFound(OrmError): ...
class TooManyRowsFound(OrmError): ...
class PermissionError(OrmError): ...
class TransactionError(OrmError): ...
class ConnectionClosedError(TransactionError): ...

class TransactionIntegrityError(TransactionError):
    original_exc: Exception | None

    def __init__(exc, msg: str, original_exc: Exception | None = None) -> None: ...

class CommitException(TransactionError):
    exceptions: Iterable[Exception]

    def __init__(exc, msg: str, exceptions: Iterable[Exception]) -> None: ...

class PartialCommitException(TransactionError):
    exceptions: Iterable[Exception]

    def __init__(exc, msg: str, exceptions: Iterable[Exception]) -> None: ...

class RollbackException(TransactionError):
    exceptions: Iterable[Exception]

    def __init__(exc, msg: str, exceptions: Iterable[Exception]) -> None: ...

class DatabaseSessionIsOver(TransactionError): ...

TransactionRolledBack = DatabaseSessionIsOver

class IsolationError(TransactionError): ...
class UnrepeatableReadError(IsolationError): ...
class OptimisticCheckError(IsolationError): ...
class UnresolvableCyclicDependency(TransactionError): ...

class UnexpectedError(TransactionError):
    original_exc: Exception

    def __init__(exc, msg: str, original_exc: Exception) -> None: ...

class ExprEvalError(TranslationError):
    cause: Exception

    def __init__(exc, src: str, cause: Exception) -> None: ...

class PonyInternalException(Exception): ...
class OptimizationFailed(PonyInternalException): ...

class UseAnotherTranslator(PonyInternalException):
    translator: SQLTranslator

    def __init__(self, translator: SQLTranslator) -> None: ...

class PonyRuntimeWarning(RuntimeWarning): ...
class DatabaseContainsIncorrectValue(PonyRuntimeWarning): ...
class DatabaseContainsIncorrectEmptyValue(DatabaseContainsIncorrectValue): ...
