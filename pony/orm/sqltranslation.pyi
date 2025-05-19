from ast import AST
from ast import Attribute as AstAttribute
from ast import BinOp, BoolOp, Bytes, Call, Compare
from ast import Constant as AstConstant
from ast import (
    Expr,
    FormattedValue,
    GeneratorExp,
    IfExp,
    JoinedStr,
    List,
    Name,
    NameConstant,
    Num,
    Slice,
    Str,
    Subscript,
    Tuple,
    UnaryOp,
    expr,
    keyword,
)
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, Sequence
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from io import BytesIO
from itertools import count as _count
from types import TracebackType
from typing import Any, ClassVar, Generic, NoReturn, TypeVar, overload
from uuid import UUID

import _typeshed
from _typeshed import MaybeNone
from typing_extensions import LiteralString, Self, TypeAlias

from pony.orm.asttranslation import ASTTranslator
from pony.orm.asttranslation import TranslationError as TranslationError
from pony.orm.core import (
    Attribute,
    AttrOffsets,
    AttrValue,
    CodeKey,
    Constant,
    Database,
    DescWrapper,
    Entity,
    EntityMeta,
    ExprType,
    Numeric,
    OptAttrValue,
    ParamKey,
    PyType,
    Query,
    QueryVars,
    VarType,
    VarTypes,
)
from pony.orm.dbapiprovider import Converter
from pony.orm.ormtypes import Array, FuncType, Json, RawSQL, RawSQLType, SetType
from pony.utils.utils import localbase

_Ast: TypeAlias = list[str | list[str | int | bool | list]]
_Conditions: TypeAlias = list[list[list[Sequence[str]]]]
_Sql: TypeAlias = list[str | bool | type[str | int | float | bool | None] | list | None]

_T = TypeVar("_T")
_CT = TypeVar("_CT", bound=Constant)

def check_comparable(left_monad: Monad, right_monad: Monad, op: str = "==") -> None: ...
def coerce_monads(
    m1: Monad, m2: Monad, for_comparison: bool = False
) -> tuple[EntityMeta | type[AttrValue] | SetType | None, Monad, Monad]: ...
def combine_limit_and_offset(
    limit: int | None, offset: int | None, limit2: int | None, offset2: int | None
) -> tuple[int | None, int | None]: ...
@overload
def distinct_from_monad(
    distinct: NumericConstMonad, default: bool | None = None
) -> bool: ...
@overload
def distinct_from_monad(distinct: None, default: bool) -> bool: ...
def find_or_create_having_ast(sections: list) -> list: ...
def get_classes(classinfo: EntityMonad | ListMonad) -> Iterator[EntityMeta]: ...
def join_tables(
    alias1: str, alias2: str, columns1: list[str], columns2: list[str]
) -> list[str | list[str]]: ...
def make_attrset_binop(
    op: str, sqlop: str
) -> Callable[[Monad, Monad], NumericSetExprMonad]: ...
def make_datetime_binop(
    op: str, sqlop: str
) -> Callable[[DateMixin, TimedeltaMixin], DateExprMonad | DatetimeExprMonad]: ...
def make_numeric_binop(
    op: str, sqlop: str
) -> Callable[[Monad, Monad], NumericExprMonad | NumericSetExprMonad]: ...
def make_numericset_binop(
    op: str, sqlop: str
) -> Callable[[Monad, Monad], NumericSetExprMonad]: ...
def make_string_binop(
    op: str, sqlop: str
) -> Callable[[Monad, Monad], StringExprMonad]: ...
def make_string_func(sqlop: str) -> Callable[[Monad], StringExprMonad]: ...
def minmax(monad: FuncMaxMonad | FuncMinMonad, sqlop: str, *args) -> ExprMonad: ...
def numeric_attr_factory(name: str) -> Callable[[Monad], NumericExprMonad]: ...
def raise_forgot_parentheses(monad) -> NoReturn: ...
def reraise_improved_typeerror(
    exc: TypeError, func_name: str, orig_func_name: str
) -> NoReturn: ...
def sqland(items: list[list[str | list[str]]]) -> list[str] | list[str | list[str]]: ...
def sqlor(items: list[list[str | list[str]]]) -> list[str] | list[str | list[str]]: ...
def type2str(t: ExprType) -> str: ...
def wrap_monad_method(cls_name: str, func: Callable[..., _T]) -> Callable[..., _T]: ...

translator_counter: _count
local: Local

class IncomparableTypesError(TypeError):
    def __init__(
        exc,
        type1: ExprType,
        type2: ExprType,
    ) -> None: ...

class Local(localbase):
    translators: list[SQLTranslator]

    def __init__(local) -> None: ...
    @property
    def translator(self) -> SQLTranslator: ...

class SQLTranslator(ASTTranslator):
    aggregated: bool
    aggregated_subquery_paths: set[str]
    alias: str | None
    can_be_cached: bool
    code_key: CodeKey
    col_names: list[str]
    conditions: _Conditions
    database: Database | MaybeNone
    distinct: bool
    expr_columns: list[list[str]]
    expr_monads: Sequence[Monad]
    expr_type: ExprType
    extractors: dict[str, Callable] | MaybeNone
    filter_num: int
    fixed_param_values: dict[ParamKey, OptAttrValue]
    from_optimized: bool
    func_extractors_map: dict[Callable, dict[str, Callable]]
    func_vartypes: VarTypes
    groupby_monads: Sequence[Monad | MonadMixin] | None
    having_conditions: list[list[list[str | list]]]
    id: int
    injected: bool
    inside_order_by: bool
    left_join: bool
    limit: int | None
    namespace_stack: list[dict[str, Monad | MonadMixin]]
    offset: int | None
    optimize: str | None
    optimization_failed: bool
    order: list[str]
    original_code_key: CodeKey | None
    original_filter_num: int | None
    parent: SQLTranslator | None
    pickled_tree: BytesIO
    query_result_is_cacheable: bool
    registered_functions: dict[FuncType, type[Monad]]
    root_translator: SQLTranslator
    row_layout: list[tuple[Callable, int | slice, str]] | None
    sqlquery: SqlQuery
    tableref: TableRef | JoinedTableRef | ExprJoinedTableRef
    vars: QueryVars | None
    vartypes: VarTypes | MaybeNone

    dialect: ClassVar[str | MaybeNone]
    json_path_wildcard_syntax: ClassVar[bool]
    json_values_are_comparable: ClassVar[bool]
    row_value_syntax: ClassVar[bool]
    rowid_support: ClassVar[bool]

    def __enter__(translator) -> None: ...
    def __exit__(
        translator,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
    def __init__(
        translator,
        tree: GeneratorExp,
        parent_translator: SQLTranslator | None,
        code_key: CodeKey | None = None,
        filter_num: int | None = None,
        extractors: dict[str, Callable] | None = None,
        vars: QueryVars | None = None,
        vartypes: VarTypes | None = None,
        left_join: bool = False,
        optimize: str | None = None,
    ) -> None: ...
    def apply_kwfilters(
        translator,
        filterattrs: Iterable[tuple[Attribute, int, bool]],
        original_names: bool = False,
    ) -> SQLTranslator: ...
    def apply_lambda(
        translator,
        func_id: str | int,
        filter_num: int,
        order_by: bool,
        func_ast: expr,
        argnames: list[str],
        original_names: bool,
        extractors: dict[str, Callable],
        vars: QueryVars | None,
        vartypes: VarTypes,
    ) -> SQLTranslator: ...
    def call(translator, method: Callable, node: AST) -> Monad | None: ...
    def can_be_optimized(translator) -> str | bool: ...
    def construct_delete_sql_ast(
        translator,
    ) -> list[str | list[str | list[str | int | None | list]]] | None: ...
    def construct_sql_ast(
        translator,
        limit: int | None = None,
        offset: int | None = None,
        distinct: bool | None = None,
        aggr_func_name: str | None = None,
        aggr_func_distinct: bool | None = None,
        sep: str | None = None,
        for_update: bool = False,
        nowait: bool = False,
        skip_locked: bool = False,
        is_not_null_checks: bool = False,
    ) -> tuple[list[str | list[str | int | list]], AttrOffsets | None]: ...
    def construct_subquery_ast(
        translator,
        limit: int | None = None,
        offset: int | None = None,
        aliases: list[str] | None = None,
        star: str | None = None,
        distinct: bool | None = None,
        is_not_null_checks: bool = False,
    ) -> _Ast: ...
    def deepcopy(translator) -> SQLTranslator: ...
    def dispatch(translator, node: expr) -> None: ...
    def dispatch_external(translator, node: AST) -> None: ...
    def get_used_attrs(translator) -> set[Attribute] | Any: ...
    def init(
        translator,
        tree: GeneratorExp,
        parent_translator: SQLTranslator | None,
        code_key: CodeKey | None = None,
        filter_num: int | None = None,
        extractors: dict[str, Callable] | None = None,
        vars: QueryVars | None = None,
        vartypes: VarTypes | None = None,
        left_join: bool = False,
        optimize: str | None = None,
    ) -> None: ...
    @property
    def namespace(
        translator,
    ) -> dict[str, Monad | MonadMixin]: ...
    def order_by_attributes(
        translator, attrs: tuple[Attribute | DescWrapper, ...]
    ) -> SQLTranslator: ...
    def order_by_numbers(translator, numbers: tuple[int, ...]) -> SQLTranslator: ...
    def postAdd(translator, node: BinOp) -> ExprMonad: ...
    def postAnd(translator, node: BoolOp) -> AndMonad: ...
    def postAttribute(translator, node: AstAttribute) -> Monad: ...
    def postBytes(translator, node: Bytes) -> BufferConstMonad: ...
    def postCall(translator, node: Call) -> Monad: ...
    def postConstant(translator, node: AstConstant) -> ConstMonad | ListMonad: ...
    def postDiv(translator, node: BinOp) -> NumericExprMonad: ...
    def postExpr(translator, node: Expr) -> ExprMonad: ...
    def postFormattedValue(translator, node: FormattedValue) -> AttrMonad: ...
    def postIfExp(translator, node: IfExp) -> Monad: ...
    def postJoinedStr(translator, node: JoinedStr) -> StringExprMonad: ...
    def postList(translator, node: List) -> ListMonad: ...
    def postMult(translator, node: BinOp) -> NumericExprMonad: ...
    def postName(translator, node: Name) -> Monad: ...
    def postNameConstant(translator, node: NameConstant) -> ConstMonad: ...
    def postNot(translator, node: UnaryOp) -> BoolMonad: ...
    def postNum(translator, node: Num) -> NumericConstMonad: ...
    def postOr(translator, node: BoolOp) -> OrMonad: ...
    def postPow(translator, node: BinOp) -> NumericExprMonad: ...
    def postSlice(translator, node: Slice) -> None: ...
    def postStr(translator, node: Str) -> StringConstMonad: ...
    def postSub(translator, node: BinOp) -> ExprMonad: ...
    def postSubscript(translator, node: Subscript) -> Monad: ...
    def postTuple(translator, node: Tuple) -> ListMonad: ...
    def postUSub(translator, node: UnaryOp) -> NumericExprMonad: ...
    def postkeyword(translator, node: keyword) -> None: ...
    def preCall(translator, node: Call) -> Monad | None: ...
    def preCompare(translator, node: Compare) -> BoolMonad: ...
    def preGeneratorExp(translator, node: GeneratorExp) -> QuerySetMonad: ...
    def process_query_qual(
        translator,
        prev_translator: SQLTranslator,
        prev_limit: int | None,
        prev_offset: int | None,
        names: tuple[str, ...],
        try_extend_prev_query: bool = False,
    ) -> None: ...
    def resolve_name(translator, name: str) -> Monad: ...
    def without_order(translator) -> SQLTranslator: ...

class SqlQuery:
    alias_counters: dict[str, int]
    conditions: _Conditions
    expr_counter: _count[int]
    expr_list: list[list[str]]
    from_ast: _Ast
    left_join: bool
    outer_conditions: _Conditions
    parent_sqlquery: SqlQuery | None
    tablerefs: dict[str, TableRef | JoinedTableRef]
    translator: SQLTranslator
    used_from_subquery: bool

    def __init__(
        sqlquery,
        translator: SQLTranslator,
        parent_sqlquery: SqlQuery | None = None,
        left_join: bool = False,
    ) -> None: ...
    def add_tableref(
        sqlquery,
        name_path: str,
        parent_tableref: TableRef | JoinedTableRef,
        attr: Attribute,
    ) -> JoinedTableRef: ...
    def get_tableref(sqlquery, name_path: str) -> TableRef | JoinedTableRef | None: ...
    def join_table(
        sqlquery,
        parent_alias: str,
        alias: str,
        table_name: str,
        join_cond: list[
            str
            | list[list[str] | str]
            | list[str]
            | list[str | list[str] | list[list[str]]]
        ],
    ) -> None: ...
    def make_alias(sqlquery, name: str) -> str: ...

class TableRef:
    alias: str
    can_affect_distinct: bool
    entity: EntityMeta
    joined: bool
    name_path: str
    sqlquery: SqlQuery
    used_attrs: set[Attribute]

    def __init__(
        tableref, sqlquery: SqlQuery, name: str, entity: EntityMeta
    ) -> None: ...
    def make_join(tableref, pk_only: bool = False) -> tuple[str, list[str] | None]: ...

class ExprTableRef(TableRef):
    subquery_ast: _Ast
    expr_names: tuple[str, ...]
    expr_aliases: list[str]

    def __init__(
        tableref,
        sqlquery: SqlQuery,
        name: str,
        subquery_ast: _Ast,
        expr_names: tuple[str, ...],
        expr_aliases: list[str],
    ) -> None: ...
    def make_join(tableref, pk_only: bool = False) -> tuple[str, list[str] | None]: ...

class StarTableRef(TableRef):
    subquery_ast: _Ast

    def __init__(
        tableref,
        sqlquery: SqlQuery,
        name: str,
        entity: EntityMeta,
        subquery_ast: _Ast,
    ) -> None: ...
    def make_join(tableref, pk_only: bool = False) -> tuple[str, list[str]]: ...

class ExprJoinedTableRef:
    alias: str | MaybeNone
    can_affect_distinct: bool
    entity: EntityMeta
    joined: bool
    name: str
    name_path: str
    parent_columns: list[str]
    parent_tableref: ExprTableRef
    pk_columns: list[str] | MaybeNone
    sqlquery: SqlQuery
    used_attrs: set[Attribute]

    def __init__(
        tableref,
        sqlquery: SqlQuery,
        parent_tableref: ExprTableRef,
        parent_columns: list[str],
        name: str,
        entity: EntityMeta,
    ) -> None: ...
    def make_join(tableref, pk_only: bool = False) -> tuple[str, list[str] | None]: ...

class JoinedTableRef:
    alias: str | MaybeNone
    attr: Attribute
    can_affect_distinct: bool
    entity: EntityMeta
    joined: bool
    name_path: str
    optimized: bool | None
    parent_tableref: TableRef | JoinedTableRef
    pk_columns: list[str] | MaybeNone
    sqlquery: SqlQuery
    used_attrs: set[Attribute]
    var_name: str | None

    def __init__(
        tableref,
        sqlquery: SqlQuery,
        name_path: str,
        parent_tableref: TableRef | JoinedTableRef,
        attr: Attribute,
    ) -> None: ...
    def make_join(tableref, pk_only: bool = False) -> tuple[str, list[str]]: ...

class MonadMeta(type):
    aggregated: bool
    nullable: bool
    orderby_columns: Sequence[int]
    tableref: TableRef | JoinedTableRef | ExprJoinedTableRef | MaybeNone
    type: Any

    @staticmethod
    def __new__(
        meta: type[_typeshed.Self],
        cls_name: str,
        bases: (
            tuple[type[Monad | object]]  # noqa: Y090
            | tuple[type[object], _typeshed.Self]
        ),
        cls_dict: dict[str, Any],
    ) -> type[_typeshed.Self]: ...

class MonadMixin(metaclass=MonadMeta):
    def getsql(monad, sqlquery: SqlQuery | None = None) -> Any: ...

class Monad(metaclass=MonadMeta):
    node: AST | MaybeNone
    nogroup: bool
    translator: SQLTranslator

    disable_distinct: ClassVar[bool]
    disable_ordering: ClassVar[bool]

    def __init__(monad, type: VarType, nullable: bool | None = None) -> None: ...
    def __call__(monad, *args, **kwargs) -> Any: ...
    def __getitem__(monad, key: Monad | slice, /) -> Any: ...
    def __add__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def __sub__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def __mul__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def __truediv__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def __floordiv__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def __pow__(monad, monad2: Monad, /) -> Any: ...
    def __neg__(monad) -> Any: ...
    def __or__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def __and__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def __xor__(monad, monad2: Monad, /) -> Callable[[Monad, Monad], Monad]: ...
    def abs(monad) -> Any: ...
    def aggregate(
        monad,
        func_name: str,
        distinct: NumericConstMonad | None = None,
        sep: str | None = None,
    ) -> ExprMonad | NoneMonad: ...
    def cast_from_json(monad, type: type) -> Any: ...
    def cmp(monad, op: str, monad2: Monad) -> CmpMonad: ...
    def contains(
        monad, item: Monad, /, not_in: bool = False
    ) -> BoolExprMonad | NoneMonad: ...
    def count(monad, distinct: NumericConstMonad | None = None) -> ExprMonad: ...
    def getattr(monad, attrname: str) -> Monad: ...
    def len(monad) -> Any: ...
    def mixin_init(monad) -> NoneMonad | None: ...
    def negate(monad) -> BoolMonad | JsonItemMonad | NoneMonad: ...
    def nonzero(monad) -> BoolMonad | RawSQLMonad | NoneMonad: ...
    def to_int(monad) -> NumericExprMonad | NoneMonad: ...
    def to_real(monad) -> NumericExprMonad | NoneMonad: ...
    def to_single_cell_value(monad) -> Monad: ...
    def to_str(monad) -> StringExprMonad | NoneMonad: ...

class RawSQLMonad(Monad):
    rawtype: RawSQLType
    varkey: tuple[int, str, int]

    def __init__(
        monad, rawtype: RawSQLType, varkey: tuple[int, str, int], nullable: bool = True
    ) -> None: ...
    def contains(monad, item: Monad, not_in: bool = False) -> BoolExprMonad: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> list[list[str | list]]: ...
    def nonzero(monad) -> Self: ...

class MethodMonad(Monad):
    parent: StringAttrMonad
    attrname: str

    def __call__(monad, *args, **kwargs) -> StringExprMonad: ...
    def __init__(monad, parent: StringAttrMonad, attrname: str) -> None: ...

class EntityMonad(Monad):
    def __getitem__(monad, key: Monad | slice) -> Any: ...
    def __init__(
        monad,
        entity: EntityMeta,
    ) -> None: ...

class ListMonad(Monad):
    items: list

    def __init__(
        monad,
        items: list,
    ) -> None: ...
    def contains(monad, x: Monad, /, not_in: bool = False) -> BoolExprMonad: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> list[list[str]]: ...

class BufferMixin(MonadMixin): ...
class UuidMixin(MonadMixin): ...

class NumericMixin(MonadMixin):
    forced_distinct: bool
    translator: SQLTranslator

    __add__: Callable[[Monad, Monad], Monad]
    __sub__: Callable[[Monad, Monad], Monad]
    __mul__: Callable[[Monad, Monad], Monad]
    __truediv__: Callable[[Monad, Monad], Monad]
    __floordiv__: Callable[[Monad, Monad], Monad]
    __mod__: Callable[[Monad, Monad], Monad]
    __and__: Callable[[Monad, Monad], Monad]
    __or__: Callable[[Monad, Monad], Monad]
    __xor__: Callable[[Monad, Monad], Monad]

    def __neg__(monad) -> NumericExprMonad: ...
    def __pow__(
        monad, monad2: StringConstMonad | NumericConstMonad
    ) -> NumericExprMonad: ...
    def abs(monad) -> NumericExprMonad: ...
    def mixin_init(monad) -> None: ...
    def negate(monad) -> BoolExprMonad: ...
    def nonzero(monad) -> BoolExprMonad: ...

class DateMixin(MonadMixin):
    attr_year: ClassVar[Callable[[Monad], NumericExprMonad]]
    attr_month: ClassVar[Callable[[Monad], NumericExprMonad]]
    attr_day: ClassVar[Callable[[Monad], NumericExprMonad]]

    def __add__(monad, other: TimedeltaMixin) -> DateExprMonad | DatetimeExprMonad: ...
    def __sub__(
        monad,
        other: TimedeltaMixin | DateMixin,
    ) -> TimedeltaExprMonad | DateExprMonad | DatetimeExprMonad: ...
    def mixin_init(monad) -> None: ...

class TimeMixin(MonadMixin):
    attr_hour: ClassVar[Callable[[Monad], NumericExprMonad]]
    attr_minute: ClassVar[Callable[[Monad], NumericExprMonad]]
    attr_second: ClassVar[Callable[[Monad], NumericExprMonad]]

    def mixin_init(monad) -> None: ...

class TimedeltaMixin(MonadMixin):
    def mixin_init(monad) -> None: ...

class DatetimeMixin(DateMixin):
    attr_hour: ClassVar[Callable[[Monad], NumericExprMonad]]
    attr_minute: ClassVar[Callable[[Monad], NumericExprMonad]]
    attr_second: ClassVar[Callable[[Monad], NumericExprMonad]]

    def __add__(monad, other: TimedeltaMixin) -> DatetimeExprMonad: ...
    def call_date(monad) -> DateExprMonad: ...
    def __sub__(
        monad,
        other: TimedeltaMixin | DateMixin,
    ) -> TimedeltaExprMonad | DatetimeExprMonad: ...
    def mixin_init(monad) -> None: ...

class StringMixin(MonadMixin):
    translator: SQLTranslator

    call_upper: ClassVar[Callable[[Monad], StringExprMonad]]
    call_lower: ClassVar[Callable[[Monad], StringExprMonad]]

    __add__: Callable[[Monad, Monad], StringExprMonad]

    def __getitem__(
        monad,
        index: NumericMixin | slice,
    ) -> StringMixin | ConstMonad | ListMonad: ...
    def _like(
        monad,
        item: RawSQLMonad | StringConstMonad | StringAttrMonad | StringParamMonad,
        before: str | None = None,
        after: str | None = None,
        not_like: bool = False,
    ) -> BoolExprMonad: ...
    def call_endswith(
        monad, arg: NumericConstMonad | StringConstMonad | StringParamMonad
    ) -> BoolExprMonad: ...
    def call_lstrip(
        monad, chars: StringConstMonad | None = None
    ) -> StringExprMonad: ...
    def call_rstrip(
        monad, chars: StringConstMonad | StringParamMonad | None = None
    ) -> StringExprMonad: ...
    def call_startswith(
        monad,
        arg: StringParamMonad | RawSQLMonad | StringConstMonad | NumericConstMonad,
    ) -> BoolExprMonad: ...
    def call_strip(
        monad, chars: NumericConstMonad | None = None
    ) -> StringExprMonad: ...
    def contains(monad, item: Monad, not_in: bool = False) -> BoolExprMonad: ...
    def len(monad) -> NumericExprMonad | ConstMonad | ListMonad: ...
    def mixin_init(monad) -> None: ...
    def negate(monad) -> BoolExprMonad: ...
    def nonzero(monad) -> BoolExprMonad: ...
    def strip(
        monad,
        chars: StringParamMonad | StringConstMonad | NumericConstMonad | None,
        strip_type: str,
    ) -> StringExprMonad: ...

class JsonMixin:
    translator: SQLTranslator
    type: type

    disable_distinct: ClassVar[bool]
    disable_ordering: ClassVar[bool]

    def __getitem__(
        monad,
        key: EllipsisMonad | NumericMixin | slice | StringMixin,
    ) -> JsonItemMonad: ...
    def cast_from_json(monad, type) -> Self | ExprMonad: ...
    def contains(monad, key: Monad, not_in: bool = False) -> BoolExprMonad: ...
    def get_path(monad) -> tuple[JsonMixin, list]: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> Any: ...
    def len(monad) -> NumericExprMonad: ...
    def mixin_init(monad) -> None: ...
    def nonzero(monad) -> BoolExprMonad: ...

class ArrayMixin(MonadMixin):
    translator: SQLTranslator

    def __getitem__(monad, index: slice | NumericMixin) -> ExprMonad: ...
    def _index(
        monad, index: NumericMixin | None, from_one: bool, plus_one: bool
    ) -> list[str | list | None] | None: ...
    def contains(monad, key: Monad, /, not_in: bool = False) -> BoolExprMonad: ...
    def len(monad) -> NumericExprMonad: ...

class ObjectMixin(MonadMixin):
    attr: Attribute
    parent: ObjectMixin
    tableref: TableRef | JoinedTableRef | ExprJoinedTableRef
    type: EntityMeta

    def getattr(monad, attrname: str) -> Monad: ...
    def mixin_init(monad) -> None: ...
    def negate(monad) -> BoolMonad: ...
    def nonzero(monad) -> CmpMonad: ...
    def requires_distinct(monad, joined: bool = False) -> bool: ...

class ObjectIterMonad(ObjectMixin, Monad):
    tableref: TableRef | JoinedTableRef | ExprJoinedTableRef

    def __init__(
        monad,
        tableref: TableRef | JoinedTableRef | ExprJoinedTableRef,
        entity: EntityMeta,
    ) -> None: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> list[list[str]]: ...
    def requires_distinct(monad, joined: bool = False) -> bool: ...

class SetMixin(MonadMixin):
    forced_distinct: bool

    def call_distinct(monad) -> SetMixin: ...

class AttrSetMonad(SetMixin, Monad):
    parent: AttrSetMonad | ObjectIterMonad
    attr: Attribute
    sqlquery: SqlQuery | None
    tableref: TableRef | None

    __add__: Callable[[Monad, Monad], NumericSetExprMonad]
    __sub__: Callable[[Monad, Monad], NumericSetExprMonad]
    __mul__: Callable[[Monad, Monad], NumericSetExprMonad]
    __truediv__: Callable[[Monad, Monad], NumericSetExprMonad]
    __floordiv__: Callable[[Monad, Monad], NumericSetExprMonad]

    def __init__(
        monad, parent: AttrSetMonad | ObjectIterMonad, attr: Attribute
    ) -> None: ...
    def _aggregated_scalar_subselect(
        monad, make_aggr: Callable, extra_grouping: bool = False
    ) -> tuple[list, bool]: ...
    def _joined_subselect(
        monad,
        make_aggr: Callable,
        extra_grouping: bool = False,
        coalesce_to_zero: bool = False,
    ) -> tuple[list, bool]: ...
    def _subselect(
        monad, sqlquery: SqlQuery | None = None, extract_outer_conditions: bool = True
    ) -> SqlQuery: ...
    def aggregate(
        monad,
        func_name: str,
        distinct: NumericConstMonad | None = None,
        sep: str | None = None,
    ) -> ExprMonad: ...
    def call_select(monad) -> AttrSetMonad: ...
    def cmp(monad, op: str, monad2: Monad): ...
    def contains(monad, item: Monad, not_in: bool = False) -> BoolExprMonad: ...
    def count(monad, distinct: NumericConstMonad | None = None) -> ExprMonad: ...
    def getattr(monad, attrname: str) -> Monad: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> list[list[str]]: ...
    def make_expr_list(monad) -> list[list[str]]: ...
    def make_tableref(
        monad, sqlquery: SqlQuery
    ) -> TableRef | JoinedTableRef | ExprJoinedTableRef: ...
    def negate(monad) -> BoolExprMonad: ...
    def nonzero(monad) -> BoolExprMonad: ...
    def requires_distinct(
        monad, joined: bool = False, for_count: bool = False
    ) -> bool: ...

class NumericSetExprMonad(SetMixin, Monad):
    op: str
    sqlop: str
    left: Monad
    right: Monad

    __add__: Callable[[Monad, Monad], NumericSetExprMonad]
    __sub__: Callable[[Monad, Monad], NumericSetExprMonad]
    __mul__: Callable[[Monad, Monad], NumericSetExprMonad]
    __truediv__: Callable[[Monad, Monad], NumericSetExprMonad]
    __floordiv__: Callable[[Monad, Monad], NumericSetExprMonad]

    def __init__(monad, op: str, sqlop: str, left: Monad, right: Monad) -> None: ...
    def aggregate(
        monad,
        func_name: str,
        distinct: NumericConstMonad | None = None,
        sep: str | None = None,
    ) -> ExprMonad: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> list[list[str]]: ...

class QuerySetMonad(SetMixin, Monad):
    subtranslator: SQLTranslator
    item_type: ExprType
    limit: Numeric | None
    nogroup: bool = True
    offset: Numeric | None

    def __init__(monad, subtranslator: SQLTranslator) -> None: ...
    def aggregate(
        monad,
        func_name: str,
        distinct: NumericConstMonad | None = None,
        sep: str | None = None,
    ) -> ExprMonad: ...
    def call_avg(monad, distinct: NumericConstMonad | None = None) -> ExprMonad: ...
    def call_count(monad, distinct: NumericConstMonad | None = None) -> ExprMonad: ...
    def call_group_concat(
        monad, sep: str | None = None, distinct: NumericConstMonad | None = None
    ) -> ExprMonad: ...
    def call_limit(
        monad,
        limit: int | NumericConstMonad | NoneMonad | None = None,
        offset: int | NumericConstMonad | None = None,
    ) -> QuerySetMonad: ...
    def call_max(monad) -> ExprMonad: ...
    def call_min(monad) -> ExprMonad: ...
    def call_sum(monad, distinct: NumericConstMonad | None = None) -> ExprMonad: ...
    def contains(monad, item: Monad, not_in: bool = False) -> BoolExprMonad: ...
    def getsql(
        monad,
        sqlquery: SqlQuery | None = None,
    ) -> list[list[str | list]]: ...
    def negate(monad) -> BoolExprMonad: ...
    def nonzero(monad) -> BoolExprMonad: ...
    def to_single_cell_value(monad) -> ExprMonad: ...

class AttrMonad(Monad):
    attr: Attribute
    parent: ObjectMixin

    def __init__(
        monad, parent: ObjectAttrMonad | ObjectIterMonad, attr: Attribute
    ) -> None: ...
    def __new__(cls, *args) -> Self: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> list[list[str]]: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[Numeric],
        *args,
        **kwargs,
    ) -> NumericAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin, attr: Attribute[str], *args, **kwargs
    ) -> StringAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[date],
        *args,
        **kwargs,
    ) -> DateAttrMonad | DatetimeAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[time],
        *args,
        **kwargs,
    ) -> TimeAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[timedelta],
        *args,
        **kwargs,
    ) -> TimedeltaAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[bytes],
        *args,
        **kwargs,
    ) -> BufferAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[UUID],
        *args,
        **kwargs,
    ) -> UuidAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[Json],
        *args,
        **kwargs,
    ) -> JsonAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[Array],
        *args,
        **kwargs,
    ) -> ArrayAttrMonad: ...
    @overload
    @staticmethod
    def new(
        parent: ObjectMixin,
        attr: Attribute[Entity],
        *args,
        **kwargs,
    ) -> ObjectAttrMonad: ...

class ObjectAttrMonad(ObjectMixin, AttrMonad):
    tableref: TableRef | JoinedTableRef | MaybeNone

    def __init__(
        monad, parent: ObjectAttrMonad | ObjectIterMonad, attr: Attribute
    ) -> None: ...

class StringAttrMonad(StringMixin, AttrMonad): ...
class NumericAttrMonad(NumericMixin, AttrMonad): ...
class DateAttrMonad(DateMixin, AttrMonad): ...
class TimeAttrMonad(TimeMixin, AttrMonad): ...
class TimedeltaAttrMonad(TimedeltaMixin, AttrMonad): ...
class DatetimeAttrMonad(DatetimeMixin, AttrMonad): ...
class BufferAttrMonad(BufferMixin, AttrMonad): ...
class UuidAttrMonad(UuidMixin, AttrMonad): ...
class JsonAttrMonad(JsonMixin, AttrMonad): ...
class ArrayAttrMonad(ArrayMixin, AttrMonad): ...

class ParamMonad(Monad):
    paramkey: ParamKey

    def __init__(monad, t: EntityMeta | PyType, paramkey: ParamKey) -> None: ...
    def __new__(cls, *args, **kwargs) -> Self: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> Sequence[
        Sequence[
            str
            | ParamKey
            | Converter
            | None
            | Sequence[str | ParamKey | Converter | None]
        ]
    ]: ...
    @overload
    @staticmethod
    def new(t: type[Numeric], paramkey: ParamKey) -> NumericParamMonad: ...
    @overload
    @staticmethod
    def new(t: type[str], paramkey: ParamKey) -> StringParamMonad: ...
    @overload
    @staticmethod
    def new(
        t: type[date], paramkey: ParamKey
    ) -> DateParamMonad | DatetimeParamMonad: ...
    @overload
    @staticmethod
    def new(t: type[time], paramkey: ParamKey) -> TimeParamMonad: ...
    @overload
    @staticmethod
    def new(t: type[timedelta], paramkey: ParamKey) -> TimedeltaParamMonad: ...
    @overload
    @staticmethod
    def new(t: type[bytes], paramkey: ParamKey) -> BufferParamMonad: ...
    @overload
    @staticmethod
    def new(t: type[UUID], paramkey: ParamKey) -> UuidParamMonad: ...
    @overload
    @staticmethod
    def new(t: type[Json], paramkey: ParamKey) -> JsonParamMonad: ...
    @overload
    @staticmethod
    def new(t: type[Array], paramkey: ParamKey) -> ArrayParamMonad: ...
    @overload
    @staticmethod
    def new(t: EntityMeta, paramkey: ParamKey) -> ObjectParamMonad: ...

class ObjectParamMonad(ObjectMixin, ParamMonad):
    params: tuple[ParamKey, ...]

    def __init__(
        monad,
        entity: EntityMeta,
        paramkey: ParamKey,
    ) -> None: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> Sequence[Sequence[str | ParamKey | Converter]]: ...

class StringParamMonad(StringMixin, ParamMonad): ...
class NumericParamMonad(NumericMixin, ParamMonad): ...
class DateParamMonad(DateMixin, ParamMonad): ...
class TimeParamMonad(TimeMixin, ParamMonad): ...
class TimedeltaParamMonad(TimedeltaMixin, ParamMonad): ...
class DatetimeParamMonad(DatetimeMixin, ParamMonad): ...
class BufferParamMonad(BufferMixin, ParamMonad): ...
class UuidParamMonad(UuidMixin, ParamMonad): ...

class ArrayParamMonad(ArrayMixin, ParamMonad):
    list_monad: ListMonad | None

    def __init__(
        monad,
        t: type[Array],
        paramkey: ParamKey,
        list_monad: ListMonad | None = None,
    ) -> None: ...
    def contains(monad, key: Monad, not_in: bool = False) -> BoolExprMonad: ...

class JsonParamMonad(JsonMixin, ParamMonad):
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> Sequence[Sequence[str | Sequence[str | ParamKey | Converter | None]]]: ...

class ExprMonad(Monad):
    sql: _Sql

    def __init__(
        monad,
        type: PyType,
        sql: _Sql,
        nullable: bool = True,
    ) -> None: ...
    def __new__(cls, *args, **kwargs) -> Self: ...
    def getsql(monad, sqlquery: SqlQuery | None = None) -> list[_Sql] | _Sql: ...
    @overload
    @staticmethod
    def new(t: type[Numeric], sql: _Sql, nullable: bool = True) -> NumericExprMonad: ...
    @overload
    @staticmethod
    def new(t: type[str], sql: _Sql, nullable: bool = True) -> StringExprMonad: ...
    @overload
    @staticmethod
    def new(
        t: type[date], sql: _Sql, nullable: bool = True
    ) -> DateExprMonad | DatetimeExprMonad: ...
    @overload
    @staticmethod
    def new(t: type[time], sql: _Sql, nullable: bool = True) -> TimeExprMonad: ...
    @overload
    @staticmethod
    def new(
        t: type[timedelta], sql: _Sql, nullable: bool = True
    ) -> TimedeltaExprMonad: ...
    @overload
    @staticmethod
    def new(t: type[Json], sql: _Sql, nullable: bool = True) -> JsonExprMonad: ...
    @overload
    @staticmethod
    def new(t: type[Array], sql: _Sql, nullable: bool = True) -> ArrayExprMonad: ...
    @overload
    @staticmethod
    def new(t: type[Entity], sql: _Sql, nullable: bool = True) -> ObjectExprMonad: ...

class ObjectExprMonad(ObjectMixin, ExprMonad):
    def getsql(monad, sqlquery: SqlQuery | None = None) -> _Sql: ...

class StringExprMonad(StringMixin, ExprMonad): ...
class NumericExprMonad(NumericMixin, ExprMonad): ...
class DateExprMonad(DateMixin, ExprMonad): ...
class TimeExprMonad(TimeMixin, ExprMonad): ...
class TimedeltaExprMonad(TimedeltaMixin, ExprMonad): ...
class DatetimeExprMonad(DatetimeMixin, ExprMonad): ...
class JsonExprMonad(JsonMixin, ExprMonad): ...
class ArrayExprMonad(ArrayMixin, ExprMonad): ...

class JsonItemMonad(JsonMixin, Monad):
    parent: JsonItemMonad | JsonAttrMonad

    def __init__(
        monad,
        parent: JsonItemMonad | JsonAttrMonad,
        key: EllipsisMonad | NumericMixin | StringMixin | slice,
    ) -> None: ...
    @overload
    def cast_from_json(monad, type: type[Json]) -> Self: ...
    @overload
    def cast_from_json(monad, type: type[str]) -> StringExprMonad: ...
    @overload
    def cast_from_json(monad, type: type[float]) -> NumericExprMonad: ...
    def get_path(
        monad,
    ) -> tuple[JsonMixin, list]: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> list[list[str | list | None]]: ...
    def to_int(monad) -> NumericExprMonad: ...
    def to_real(monad) -> NumericExprMonad: ...
    def to_str(monad) -> StringExprMonad: ...

class ConstMonad(Monad, Generic[_CT]):
    value: _CT

    def __init__(
        monad,
        value: _CT,
    ) -> None: ...
    def __new__(cls, *args) -> Self: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> list[Sequence[str | _CT]]: ...
    @staticmethod
    @overload
    @staticmethod
    def new(value: tuple) -> ListMonad: ...
    @overload
    @staticmethod
    def new(value: Numeric) -> NumericConstMonad: ...
    @overload
    @staticmethod
    def new(value: str) -> StringConstMonad: ...
    @overload
    @staticmethod
    def new(value: date) -> DateConstMonad | DatetimeConstMonad: ...
    @overload
    @staticmethod
    def new(value: time) -> TimeConstMonad: ...
    @overload
    @staticmethod
    def new(value: timedelta) -> TimedeltaConstMonad: ...
    @overload
    @staticmethod
    def new(value: None) -> NoneMonad: ...
    @overload
    @staticmethod
    def new(value: bytes) -> BufferConstMonad: ...
    @overload
    @staticmethod
    def new(value: Json) -> JsonConstMonad: ...
    @overload
    @staticmethod
    def new(value: ellipsis) -> EllipsisMonad: ...

class NoneMonad(ConstMonad[None]):
    def __init__(monad, value: None = None) -> None: ...
    def __call__(monad, *args, **kwargs) -> NoneMonad: ...
    def __getitem__(monad, key: Monad | slice) -> NoneMonad: ...
    def __add__(monad, monad2: Monad) -> NoneMonad: ...
    def __sub__(monad, monad2: Monad) -> NoneMonad: ...
    def __mul__(monad, monad2: Monad) -> NoneMonad: ...
    def __truediv__(monad, monad2: Monad) -> NoneMonad: ...
    def __floordiv__(monad, monad2: Monad) -> NoneMonad: ...
    def __pow__(monad, monad2: Monad) -> NoneMonad: ...
    def __neg__(monad) -> NoneMonad: ...
    def __or__(monad, monad2: Monad) -> NoneMonad: ...
    def __and__(monad, monad2: Monad) -> NoneMonad: ...
    def __xor__(monad, monad2: Monad) -> NoneMonad: ...
    def abs(monad) -> NoneMonad: ...
    def aggregate(
        monad,
        func_name: str,
        distinct: NumericConstMonad | None = None,
        sep: str | None = None,
    ) -> NoneMonad: ...
    def cmp(monad, op: str, monad2: Monad) -> CmpMonad: ...
    def contains(monad, item: Monad, not_in: bool = False) -> NoneMonad: ...
    def count(monad, distinct: NumericConstMonad | None = None) -> NumericExprMonad: ...
    def len(monad) -> NoneMonad: ...
    def mixin_init(monad) -> NoneMonad: ...
    def negate(monad) -> NoneMonad: ...
    def nonzero(monad) -> NoneMonad: ...
    def to_int(monad) -> NoneMonad: ...
    def to_real(monad) -> NoneMonad: ...
    def to_str(monad) -> NoneMonad: ...

class EllipsisMonad(ConstMonad[ellipsis]): ...

class StringConstMonad(StringMixin, ConstMonad[str]):
    def len(monad) -> NumericConstMonad: ...

class JsonConstMonad(JsonMixin, ConstMonad[Json]): ...
class BufferConstMonad(BufferMixin, ConstMonad[bytes]): ...
class NumericConstMonad(NumericMixin, ConstMonad[Numeric]): ...
class DateConstMonad(DateMixin, ConstMonad[date]): ...
class TimeConstMonad(TimeMixin, ConstMonad[time]): ...
class TimedeltaConstMonad(TimedeltaMixin, ConstMonad[timedelta]): ...
class DatetimeConstMonad(DatetimeMixin, ConstMonad[datetime]): ...

class BoolMonad(Monad):
    def __init__(monad, nullable: bool | None = None) -> None: ...
    def nonzero(monad) -> Self: ...

class BoolExprMonad(BoolMonad):
    sql: Sequence[str | bool | list]

    def __init__(
        monad,
        sql: Sequence[str | bool | list],
        nullable: bool = True,
    ) -> None: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> Sequence[Sequence[str | bool | list]]: ...
    def negate(monad) -> BoolMonad: ...

class CmpMonad(BoolMonad):
    op: str
    aggregated: bool
    left: Monad
    right: Monad

    EQ: ClassVar[str] = "EQ"
    NE: ClassVar[str] = "NE"

    def __init__(
        monad,
        op: str,
        left: Monad,
        right: Monad,
    ) -> None: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> list[Sequence[str | list]]: ...
    def negate(monad) -> CmpMonad: ...

class LogicalBinOpMonad(BoolMonad):
    binop: LiteralString

    def __init__(
        monad,
        operands: Sequence[BoolMonad | NumericMixin],
    ) -> None: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> list[Sequence[str | list]]: ...

class AndMonad(LogicalBinOpMonad): ...
class OrMonad(LogicalBinOpMonad): ...

class NotMonad(BoolMonad):
    operant: BoolMonad

    def __init__(monad, operand: BoolMonad) -> None: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> list[
        list[
            str
            | list[str | list[str | int]]
            | list[str | list[str | list[str] | list[list[str]]]]
        ]
    ]: ...
    def negate(monad) -> BoolMonad: ...

class HybridFuncMonad(Monad):
    def __call__(monad, *args, **kwargs) -> Monad: ...
    def __init__(monad, func_type: FuncType, func_name: str, *params) -> None: ...

class HybridMethodMonad(HybridFuncMonad):
    def __init__(
        monad, parent: ObjectIterMonad, attrname: str, func: Callable
    ) -> None: ...

class FuncMonadMeta(MonadMeta):
    @staticmethod
    def __new__(
        meta: type[_typeshed.Self],
        cls_name: str,
        bases: tuple[type[Monad], ...],
        cls_dict: dict[str, str | type[AttrValue] | Callable | tuple],
    ) -> _typeshed.Self: ...

class FuncMonad(Monad, metaclass=FuncMonadMeta):
    def __call__(monad, *args, **kwargs) -> Monad: ...
    def call(monad, *args, **kwargs) -> Any: ...

class FuncIsinstanceMonad(FuncMonad):
    func: ClassVar[Callable[..., bool]]

    def call(
        monad, obj: ObjectMixin, classinfo: EntityMonad | ListMonad
    ) -> BoolExprMonad: ...

class FuncBufferMonad(FuncMonad):
    func: ClassVar[Callable[..., bytes]]

    def call(
        monad,
        source: StringConstMonad | str,
        encoding: StringConstMonad | str | None = None,
        errors: StringConstMonad | str | None = None,
    ) -> ConstMonad[bytes]: ...

class FuncBoolMonad(FuncMonad):
    func: ClassVar[Callable[..., bool]]

class FuncAbsMonad(FuncMonad):
    func: ClassVar[Callable]

    def call(monad, x: NumericAttrMonad) -> NumericExprMonad: ...

class FuncAvgMonad(FuncMonad):
    func: ClassVar[
        tuple[
            Callable[[Iterable[float]], float | None],
            Callable[[Iterable[float]], float | None],
        ]
    ]

    def call(
        monad,
        x: AttrSetMonad | JsonItemMonad | NumericAttrMonad | QuerySetMonad,
        distinct: NumericConstMonad | None = None,
    ) -> ExprMonad | NoneMonad: ...

class FuncBetweenMonad(FuncMonad):
    func: ClassVar[Callable[..., bool]]
    def call(monad, x: Monad, a: Monad, b: Monad) -> BoolExprMonad: ...

class FuncCoalesceMonad(FuncMonad):
    func: ClassVar[Callable[[Sequence[OptAttrValue]], OptAttrValue]]
    def call(monad, *args) -> ExprMonad: ...

class FuncConcatMonad(FuncMonad):
    func: ClassVar[Callable[..., str]]

    def call(monad, *args) -> StringExprMonad: ...

class FuncCountMonad(FuncMonad):
    func: ClassVar[
        tuple[
            Callable[..., int | _count[int]],
            Callable[..., int | _count[int]],
            Callable[..., int | _count[int]],
        ]
    ]

    def call(
        monad,
        x: (
            AttrSetMonad
            | NumericAttrMonad
            | StringConstMonad
            | QuerySetMonad
            | ObjectIterMonad
            | None
        ) = None,
        distinct: BoolExprMonad | NumericConstMonad | None = None,
    ) -> ExprMonad: ...

class FuncDateMonad(FuncMonad):
    func: ClassVar[Callable[..., date]]

    def call(
        monad,
        year: NumericConstMonad,
        month: StringConstMonad | NumericConstMonad,
        day: NumericConstMonad,
        hour: Any = None,
        minute: Any = None,
        second: Any = None,
        microsecond: Any = None,
    ) -> DateConstMonad | DatetimeConstMonad: ...

class FuncTimeMonad(FuncMonad):
    func: ClassVar[Callable[..., time]]

    def call(monad, *args) -> TimeConstMonad: ...

class FuncTimedeltaMonad(FuncMonad):
    func: ClassVar[Callable[..., timedelta]]

    def call(
        monad,
        days: NumericConstMonad | None = None,
        seconds: NumericConstMonad | None = None,
        microseconds: NumericConstMonad | None = None,
        milliseconds: NumericConstMonad | None = None,
        minutes: NumericConstMonad | None = None,
        hours: NumericConstMonad | None = None,
        weeks: NumericConstMonad | None = None,
    ) -> TimedeltaConstMonad: ...

class FuncDatetimeMonad(FuncDateMonad):
    func: ClassVar[Callable[..., datetime]]

    def call(
        monad,
        year: NumericConstMonad,
        month: StringConstMonad | NumericConstMonad,
        day: NumericConstMonad,
        hour: NumericConstMonad | None = None,
        minute: NumericConstMonad | None = None,
        second: NumericConstMonad | None = None,
        microsecond: NumericConstMonad | None = None,
    ) -> DatetimeConstMonad: ...

class FuncDecimalMonad(FuncMonad):
    func: ClassVar[Callable[..., Decimal]]

    def call(monad, x: StringConstMonad) -> NumericConstMonad: ...

class FuncDistinctMonad(FuncMonad):
    func: ClassVar[
        tuple[
            Callable[[Sequence], defaultdict[Any, int]],
            Callable[[Sequence], defaultdict[Any, int]],
        ]
    ]

    def call(monad, x: Monad) -> MonadMixin: ...

class FuncExistsMonad(FuncMonad):
    func: ClassVar[Callable[..., bool]]

    def call(monad, arg: AttrSetMonad | QuerySetMonad) -> BoolExprMonad: ...

class FuncFloatMonad(FuncMonad):
    func: ClassVar[Callable[..., float]]

    def call(monad, x: NumericAttrMonad) -> NumericExprMonad: ...

class FuncGetattrMonad(FuncMonad):
    func: ClassVar[Callable]

    def call(
        monad,
        obj_monad: AttrSetMonad | StringAttrMonad | ObjectIterMonad,
        name_monad: (
            NumericParamMonad | StringConstMonad | StringAttrMonad | StringParamMonad
        ),
    ) -> Monad: ...

class FuncGroupConcatMonad(FuncMonad):
    func: ClassVar[
        tuple[
            Callable[[Iterable | None, str], str | None],
            Callable[[Iterable | None, str], str | None],
        ]
    ]

    def call(
        monad,
        x: AttrSetMonad | NumericAttrMonad | QuerySetMonad,
        sep: StringConstMonad | str | None = None,
        distinct: NumericConstMonad | None = None,
    ) -> ExprMonad | NoneMonad: ...

class FuncIntMonad(FuncMonad):
    func: ClassVar[Callable[..., int]]

    def call(monad, x: JsonItemMonad | StringExprMonad) -> NumericExprMonad: ...

class FuncLenMonad(FuncMonad):
    func: ClassVar[Callable[..., int]]

    def call(
        monad,
        x: Monad,
    ) -> NumericExprMonad: ...

class FuncMaxMonad(FuncMonad):
    func: ClassVar[tuple[Callable, Callable]]

    def call(monad, *args) -> ExprMonad: ...

class FuncMinMonad(FuncMonad):
    func: ClassVar[tuple[Callable, Callable]]

    def call(monad, *args) -> ExprMonad: ...

class FuncRandomMonad(FuncMonad):
    func: ClassVar[Callable[[], float]]

    def __call__(monad) -> NumericExprMonad: ...
    def __init__(monad, type: Callable) -> None: ...

class FuncRawSQLMonad(FuncMonad):
    func: ClassVar[Callable[..., RawSQL]]

    def call(monad, *args): ...

class FuncSelectMonad(FuncMonad):
    func: ClassVar[Callable[..., Query]]
    def call(monad, queryset: QuerySetMonad) -> QuerySetMonad: ...

class FuncStrMonad(FuncMonad):
    func: ClassVar[Callable[..., str]]

    def call(monad, x: StringAttrMonad) -> StringExprMonad: ...

class FuncSumMonad(FuncMonad):
    func: ClassVar[
        tuple[
            Callable[[Iterable[Numeric]], Numeric],
            Callable[[Iterable[Numeric]], Numeric],
        ]
    ]

    def call(
        monad,
        x: AttrSetMonad | NumericAttrMonad | QuerySetMonad,
        distinct: NumericConstMonad | None = None,
    ) -> NumericExprMonad: ...

class FuncDescMonad(FuncMonad):
    func: ClassVar[Callable[..., DescWrapper | Attribute | AttrValue]]

    def call(monad, expr: NumericAttrMonad | StringAttrMonad) -> DescMonad: ...

class DescMonad(Monad):
    expr: NumericAttrMonad | StringAttrMonad

    def __init__(monad, expr: NumericAttrMonad | StringAttrMonad) -> None: ...
    def getsql(
        monad, sqlquery: SqlQuery | None = None
    ) -> list[list[list[str] | str]]: ...

class JoinMonad(Monad):
    hint_join_prev: bool

    def __init__(monad, type: Callable) -> None: ...
    def __call__(monad, x: CmpMonad | BoolExprMonad) -> BoolMonad: ...
