from collections.abc import Callable, Iterable, Sequence
from typing import Any, ClassVar, TypeVar

from _typeshed import MaybeNone
from typing_extensions import Concatenate, ParamSpec, Unpack

from pony.orm.core import Adapter, Attribute, Entity, OptAttrValue, ParamKey, QueryVars
from pony.orm.dbapiprovider import (
    ArrayConverter,
    Converter,
    DBAPIProvider,
    IntConverter,
    StrConverter,
)

_T = TypeVar("_T", bound=str | Value | Param | Sequence)
_PT = TypeVar("_PT", bound=Param)
_P = ParamSpec("_P")

class AstError(Exception): ...

class Value:
    paramstyle: str
    value: OptAttrValue

    def __init__(
        self,
        paramstyle: str,
        value: OptAttrValue,
    ) -> None: ...
    def quote_str(self, s: str) -> str: ...

def flat(tree: Any) -> list: ...
def flat_conditions(
    conditions: (
        tuple[
            list[
                str
                | list[str | float | bool | None | type[str | float | bool | None]]
                | Converter
                | list
                | tuple
            ],
            ...,
        ]
        | tuple[  # noqa: Y090
            tuple[str, list[str | float | Converter | Sequence], bool, list[str]]
        ]
    ),
) -> list[
    (
        list[
            str
            | list[
                str | int | float | bool | None | type[str | int | float | bool | None]
            ]
            | Converter
            | list
            | tuple
        ]
        | tuple[str, list[str | int | float | Converter | Sequence], bool, list[str]]
    )
]: ...
def indentable(
    method: Callable[Concatenate[SQLBuilder, _P], _T],
) -> Callable[Concatenate[SQLBuilder, _P], _T | tuple[str, _T]]: ...
def join(delimiter: str, items: Iterable[_T]) -> list[_T | str]: ...
def make_binary_op(symbol: str, default_parentheses: bool = False) -> Callable: ...
def make_unary_func(symbol: str) -> Callable: ...
def move_conditions_from_inner_join_to_where(
    sections: tuple[Sequence[str | list[str]], ...],
) -> Sequence[Sequence[str | list[str]]]: ...

class Param:
    style: str
    id: int | None
    paramkey: ParamKey
    converter: Converter | None
    optimistic: bool

    def __init__(
        param,
        paramstyle: str,
        paramkey: ParamKey,
        converter: Converter | None = None,
        optimistic: bool = False,
    ) -> None: ...
    def eval(param, values: QueryVars) -> Any: ...

class CompositeParam(Param):
    items: list[Param | Value]
    func: Callable

    def __init__(
        param,
        paramstyle: str,
        paramkey: tuple[ParamKey | str, ...],
        items: list[Param | Value],
        func: Callable,
    ) -> None: ...
    def eval(
        param,
        values: (
            QueryVars
            | dict[Attribute, Entity | OptAttrValue]
            | list[Entity]
            | list[OptAttrValue]
            | tuple[int | str, ...]
        ),
    ) -> str: ...

class SQLBuilder:
    provider: DBAPIProvider
    quote_name: Callable[[str | Iterable[str]], str]
    paramstyle: str
    ast: list[str | list | None]
    indent: int
    keys: dict[str | ParamKey | tuple[ParamKey | str, ...], Param]
    inner_join_syntax: bool
    suppress_aliases: bool
    result: list[str | Value | Param]
    params: tuple[Param, ...]
    layout: list[str | ParamKey | tuple[ParamKey | str, ...]]
    sql: str
    adapter: Adapter

    dialect: ClassVar[str | MaybeNone]
    param_class: ClassVar[type[Param]]
    composite_param_class: ClassVar[type[CompositeParam]]
    value_class: type[Value]
    indent_spaces: ClassVar[str]
    least_func_name: ClassVar[str]
    greatest_func_name: ClassVar[str]

    def ALL(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def AGGREGATES(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def AND(builder, *cond_list) -> list[str | tuple[list[str], str]]: ...
    def AS(builder, expr: list, alias: str) -> tuple[Sequence, str, str]: ...
    def AVG(
        builder, distinct: bool | None, expr: list
    ) -> tuple[str, Sequence, str]: ...
    def CASE(builder, expr: None, cases: list, default: list | None = None) -> list: ...
    def COALESCE(builder, *args) -> tuple[str, list, str]: ...
    def COLUMN(builder, table_alias: str | None, col_name: str) -> list[str]: ...
    def CONCAT(builder, *args) -> tuple[str, list, str]: ...
    def COUNT(builder, distinct: bool | None, *expr_list) -> Sequence: ...
    def DELETE(
        builder,
        alias: str | None,
        from_ast: list[str | list[str | None] | list[str]],
        where: list[str | list] | None = None,
    ) -> tuple: ...
    def DESC(builder, expr: list[int | str]) -> tuple[Value | Sequence, str]: ...
    def DISTINCT(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def EXCEPT(
        builder, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def EXISTS(
        builder, *sections: Sequence[str | list[str]]
    ) -> tuple[str, str, str, list, str, str]: ...
    def GROUP_BY(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def GROUP_CONCAT(
        builder, distinct: bool | None, expr: list[str], sep: list[str] | None = None
    ) -> tuple[tuple, str]: ...
    def HAVING(builder, *conditions) -> str | list[str]: ...
    def IF(
        builder, cond: list[str | list], then: list[str | list], else_: list[str | list]
    ) -> list[str | Param | list[str] | tuple]: ...
    def FROM(builder, *sources) -> list[str]: ...
    def IN(builder, expr1: list, x: list) -> (
        str
        | tuple[
            list[str] | tuple[str, list, str],
            str,
            list[str | Param | Value | tuple[str, list, str]],
            str,
        ]
        | tuple[Value | Param | list[str], str, tuple[str, list, str]]
    ): ...
    def INNER_JOIN(builder, *sources) -> list[str]: ...
    def INSERT(
        builder,
        table_name: str,
        columns: Iterable[str | Iterable],
        values: Iterable[Sequence[str | tuple[int, None, None] | Converter]],
        returning: str | None = None,
    ) -> Sequence[str | list[str]]: ...
    def INTERSECT(
        builder, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def IS_NOT_NULL(
        builder, expr: list[str | list | type[None]]
    ) -> tuple[Sequence, str]: ...
    def IS_NULL(
        builder, expr: list[str | list[str | list] | type[None]]
    ) -> tuple[Sequence, str]: ...
    def JSON_PARAM(builder, expr: list[str | Sequence | Converter]) -> tuple: ...
    def LEFT_JOIN(builder, *sources) -> Sequence[str | Sequence[str | list[str]]]: ...
    def LIKE(
        builder,
        expr: list[str | list[str | list]],
        template: list[str | list[str | list]],
        escape: list[str] | None = None,
    ) -> tuple[Unpack[tuple], str, Value]: ...
    def LIMIT(
        builder, limit: int | None, offset: int | None = None
    ) -> str | Sequence[str]: ...
    def LTRIM(
        builder, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> (
        tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]
    ): ...
    def MAX(builder, distinct: bool | None, *args) -> tuple[str, str, list, str]: ...
    def MIN(builder, distinct: bool | None, *args) -> tuple[str, str, list, str]: ...
    def NEG(builder, expr: list[str]) -> tuple[str, list[str], str]: ...
    def NOT(builder, condition: list[str | list]) -> tuple[str, tuple, str]: ...
    def NOT_EXISTS(
        builder, *sections: Sequence[str | list[str]]
    ) -> tuple[str, tuple[str, str, str, list, str, str]]: ...
    def NOT_IN(builder, expr1: list, x: list) -> (
        str
        | tuple[
            list[str] | tuple[str, list, str],
            str,
            list[str | Param | Value | tuple[str, list, str]],
            str,
        ]
        | tuple[Value | Param | list[str], str, tuple[str, list, str]]
    ): ...
    def NOT_LIKE(
        builder,
        expr: list[str],
        template: list[str | list[str | list]],
        escape: list[str] | None = None,
    ) -> tuple[Unpack[tuple], str, Value]: ...
    def OR(
        builder, *cond_list
    ) -> tuple[str, list[str | tuple[list[str], str]], str]: ...
    def ORDER_BY(
        builder, *order_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def PARAM(
        builder,
        paramkey: str | ParamKey,
        converter: Converter | None = None,
        optimistic: bool = False,
    ) -> Param: ...
    def POW(
        builder, expr1: list[int | str | list], expr2: list[int | str | list]
    ) -> tuple[str, Value | tuple, str, Value | tuple, str]: ...
    def RAWSQL(
        builder,
        sql: list[str | list[str | ParamKey | Converter]],
    ) -> str | list[str | Param]: ...
    def REPLACE(
        builder,
        str: list[str | StrConverter | Sequence],
        from_: list[str],
        to: list[str],
    ) -> tuple[str, Param | Sequence, str, Value, str, Value, str]: ...
    def ROW(builder, *items) -> tuple[str, list[Value | str | list[str]], str]: ...
    def RTRIM(
        builder, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> (
        tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]
    ): ...
    def SELECT(
        builder, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | list[str]]]: ...
    def SELECT_FOR_UPDATE(
        builder, nowait: bool, skip_locked: bool, *sections: Sequence[str | list[str]]
    ) -> (
        Sequence[str | Sequence[str | list[str]]]
        | tuple[Sequence[str | Sequence[str | list[str]]], str, str, str, str]
    ): ...
    def STAR(builder, table_alias: str) -> tuple[str, str]: ...
    def STRING_SLICE(
        builder,
        expr: Sequence[str],
        start: Sequence[str | int | list[str | int | list] | None] | None,
        stop: Sequence[str | int | list[str | int | list] | None] | None,
    ) -> tuple[
        str,
        list[str],
        str,
        Value | list[str] | tuple,
        str,
        Value | list[str] | tuple,
        str,
    ]: ...
    def SUBSTR(
        builder,
        expr: list[str | list[str]],
        start: list[str | int | list[str | int | list]],
        len: list[str | int] | None = None,
    ) -> tuple: ...
    def SUM(
        builder, distinct: bool | None, expr: list[str]
    ) -> tuple[str, list[str], str]: ...
    def TO_INT(
        builder, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]: ...
    def TO_REAL(
        builder, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]: ...
    def TO_STR(
        builder, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]: ...
    def TRIM(
        builder, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> (
        tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]
    ): ...
    def UNION(
        builder, kind, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def UPDATE(
        builder,
        table_name: str,
        pairs: list[tuple[str, list[str | tuple[int, None, None] | Converter]]],
        where: list[str | list[str | list]] | None = None,
    ) -> list[str | list]: ...
    def VALUE(builder, value: OptAttrValue) -> Value: ...
    def WHERE(builder, *conditions) -> str | list[str]: ...
    def JSON_ARRAY_LENGTH(builder, value: Sequence[str | Sequence]) -> tuple: ...
    def JSON_CONTAINS(
        builder, expr: Sequence[str], path: list[Sequence[str]], key: Sequence
    ) -> Sequence: ...
    def JSON_NONZERO(builder, expr: Sequence[str | Sequence]) -> tuple: ...
    def JSON_QUERY(builder, expr: Sequence[str], path: Sequence[Sequence]) -> tuple: ...
    def JSON_VALUE(
        builder,
        expr: Sequence[str],
        path: Sequence[Sequence],
        type: type[OptAttrValue] | MaybeNone,
    ) -> tuple: ...
    def ARRAY_CONTAINS(
        builder, key: Sequence[str | float], not_in: bool, col: Sequence[str]
    ) -> tuple: ...
    def ARRAY_INDEX(
        builder,
        col: Sequence[str],
        index: Sequence,
    ) -> tuple: ...
    def ARRAY_LENGTH(builder, array: Sequence[str]) -> tuple: ...
    def ARRAY_SLICE(
        builder,
        array: Sequence[str],
        start: Sequence[str | int | Sequence | None] | None,
        stop: Sequence[str | int | Sequence | None] | None,
    ) -> tuple: ...
    def ARRAY_SUBSET(
        builder, array1: Sequence, not_in: bool, array2: Sequence
    ) -> tuple: ...
    def MAKE_ARRAY(builder, *items) -> tuple: ...
    def __call__(builder, ast: Sequence[str | list[str]]) -> Any: ...
    def __init__(
        builder, provider: DBAPIProvider, ast: list[str | list | None]
    ) -> None: ...
    def _subquery(
        builder, *sections: Sequence[str | list[str]]
    ) -> list[str | list[str]]: ...
    def build_json_path(
        builder,
        path: list[list[(str | int | ParamKey | Converter)]],
    ) -> tuple[Param | Value, bool, bool]: ...
    def eval_json_path(cls, values: list[str | int]) -> str: ...
    def make_param(
        builder,
        param_class: type[_PT],
        paramkey: str | ParamKey | tuple[ParamKey | str, ...],
        *args,
    ) -> _PT: ...
    def make_composite_param(
        builder,
        paramkey: tuple[ParamKey | str, ...],
        items: list[Param | Value],
        func: Callable,
    ) -> CompositeParam: ...
    def sql_join(
        builder, join_type: str, sources: tuple[list[str | list], ...]
    ) -> list[str]: ...
