from collections.abc import Callable, Iterable, Sequence
from typing import Any, ClassVar, Concatenate, TypeVar

from _typeshed import MaybeNone
from typing_extensions import ParamSpec, Unpack

from pony.orm.core import Adapter, Attribute, Entity, OptAttrValue, ParamKey, QueryVars
from pony.orm.dbapiprovider import (
    Converter,
    DBAPIProvider,
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
        self,
        paramstyle: str,
        paramkey: ParamKey,
        converter: Converter | None = None,
        optimistic: bool = False,
    ) -> None: ...
    def eval(self, values: QueryVars) -> Any: ...

class CompositeParam(Param):
    items: list[Param | Value]
    func: Callable

    def __init__(
        self,
        paramstyle: str,
        paramkey: tuple[ParamKey | str, ...],
        items: list[Param | Value],
        func: Callable,
    ) -> None: ...
    def eval(
        self,
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
        self, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def AGGREGATES(
        self, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def AND(self, *cond_list) -> list[str | tuple[list[str], str]]: ...
    def AS(self, expr: list, alias: str) -> tuple[Sequence, str, str]: ...
    def AVG(self, distinct: bool | None, expr: list) -> tuple[str, Sequence, str]: ...
    def CASE(self, expr: None, cases: list, default: list | None = None) -> list: ...
    def COALESCE(self, *args) -> tuple[str, list, str]: ...
    def COLUMN(self, table_alias: str | None, col_name: str) -> list[str]: ...
    def CONCAT(self, *args) -> tuple[str, list, str]: ...
    def COUNT(self, distinct: bool | None, *expr_list) -> Sequence: ...
    def DELETE(
        self,
        alias: str | None,
        from_ast: list[str | list[str | None] | list[str]],
        where: list[str | list] | None = None,
    ) -> tuple: ...
    def DESC(self, expr: list[int | str]) -> tuple[Value | Sequence, str]: ...
    def DISTINCT(
        self, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def EXCEPT(
        self, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def EXISTS(
        self, *sections: Sequence[str | list[str]]
    ) -> tuple[str, str, str, list, str, str]: ...
    def GROUP_BY(
        self, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def GROUP_CONCAT(
        self, distinct: bool | None, expr: list[str], sep: list[str] | None = None
    ) -> tuple[tuple, str]: ...
    def HAVING(self, *conditions) -> str | list[str]: ...
    def IF(
        self, cond: list[str | list], then: list[str | list], else_: list[str | list]
    ) -> list[str | Param | list[str] | tuple]: ...
    def FROM(self, *sources) -> list[str]: ...
    def IN(
        self, expr1: list, x: list
    ) -> (
        str
        | tuple[
            list[str] | tuple[str, list, str],
            str,
            list[str | Param | Value | tuple[str, list, str]],
            str,
        ]
        | tuple[Value | Param | list[str], str, tuple[str, list, str]]
    ): ...
    def INNER_JOIN(self, *sources) -> list[str]: ...
    def INSERT(
        self,
        table_name: str,
        columns: Iterable[str | Iterable],
        values: Iterable[Sequence[str | tuple[int, None, None] | Converter]],
        returning: str | None = None,
    ) -> Sequence[str | list[str]]: ...
    def INTERSECT(
        self, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def IS_NOT_NULL(
        self, expr: list[str | list | type[None]]
    ) -> tuple[Sequence, str]: ...
    def IS_NULL(
        self, expr: list[str | list[str | list] | type[None]]
    ) -> tuple[Sequence, str]: ...
    def JSON_PARAM(self, expr: list[str | Sequence | Converter]) -> tuple: ...
    def LEFT_JOIN(self, *sources) -> Sequence[str | Sequence[str | list[str]]]: ...
    def LIKE(
        self,
        expr: list[str | list[str | list]],
        template: list[str | list[str | list]],
        escape: list[str] | None = None,
    ) -> tuple[Unpack[tuple], str, Value]: ...
    def LIMIT(
        self, limit: int | None, offset: int | None = None
    ) -> str | Sequence[str]: ...
    def LTRIM(
        self, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> (
        tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]
    ): ...
    def MAX(self, distinct: bool | None, *args) -> tuple[str, str, list, str]: ...
    def MIN(self, distinct: bool | None, *args) -> tuple[str, str, list, str]: ...
    def NEG(self, expr: list[str]) -> tuple[str, list[str], str]: ...
    def NOT(self, condition: list[str | list]) -> tuple[str, tuple, str]: ...
    def NOT_EXISTS(
        self, *sections: Sequence[str | list[str]]
    ) -> tuple[str, tuple[str, str, str, list, str, str]]: ...
    def NOT_IN(
        self, expr1: list, x: list
    ) -> (
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
        self,
        expr: list[str],
        template: list[str | list[str | list]],
        escape: list[str] | None = None,
    ) -> tuple[Unpack[tuple], str, Value]: ...
    def OR(self, *cond_list) -> tuple[str, list[str | tuple[list[str], str]], str]: ...
    def ORDER_BY(
        self, *order_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def PARAM(
        self,
        paramkey: str | ParamKey,
        converter: Converter | None = None,
        optimistic: bool = False,
    ) -> Param: ...
    def POW(
        self, expr1: list[int | str | list], expr2: list[int | str | list]
    ) -> tuple[str, Value | tuple, str, Value | tuple, str]: ...
    def RAWSQL(
        self,
        sql: list[str | list[str | ParamKey | Converter]],
    ) -> str | list[str | Param]: ...
    def REPLACE(
        self,
        str: list[str | StrConverter | Sequence],
        from_: list[str],
        to: list[str],
    ) -> tuple[str, Param | Sequence, str, Value, str, Value, str]: ...
    def ROW(self, *items) -> tuple[str, list[Value | str | list[str]], str]: ...
    def RTRIM(
        self, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> (
        tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]
    ): ...
    def SELECT(
        self, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | list[str]]]: ...
    def SELECT_FOR_UPDATE(
        self, nowait: bool, skip_locked: bool, *sections: Sequence[str | list[str]]
    ) -> (
        Sequence[str | Sequence[str | list[str]]]
        | tuple[Sequence[str | Sequence[str | list[str]]], str, str, str, str]
    ): ...
    def STAR(self, table_alias: str) -> tuple[str, str]: ...
    def STRING_SLICE(
        self,
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
        self,
        expr: list[str | list[str]],
        start: list[str | int | list[str | int | list]],
        len: list[str | int] | None = None,
    ) -> tuple: ...
    def SUM(
        self, distinct: bool | None, expr: list[str]
    ) -> tuple[str, list[str], str]: ...
    def TO_INT(
        self, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]: ...
    def TO_REAL(
        self, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]: ...
    def TO_STR(
        self, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]: ...
    def TRIM(
        self, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> (
        tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]
    ): ...
    def UNION(
        self, kind, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]: ...
    def UPDATE(
        self,
        table_name: str,
        pairs: list[tuple[str, list[str | tuple[int, None, None] | Converter]]],
        where: list[str | list[str | list]] | None = None,
    ) -> list[str | list]: ...
    def VALUE(self, value: OptAttrValue) -> Value: ...
    def WHERE(self, *conditions) -> str | list[str]: ...
    def JSON_ARRAY_LENGTH(self, value: Sequence[str | Sequence]) -> tuple: ...
    def JSON_CONTAINS(
        self, expr: Sequence[str], path: list[Sequence[str]], key: Sequence
    ) -> Sequence: ...
    def JSON_NONZERO(self, expr: Sequence[str | Sequence]) -> tuple: ...
    def JSON_QUERY(self, expr: Sequence[str], path: Sequence[Sequence]) -> tuple: ...
    def JSON_VALUE(
        self,
        expr: Sequence[str],
        path: Sequence[Sequence],
        type: type[OptAttrValue] | MaybeNone,
    ) -> tuple: ...
    def ARRAY_CONTAINS(
        self, key: Sequence[str | float], not_in: bool, col: Sequence[str]
    ) -> tuple: ...
    def ARRAY_INDEX(
        self,
        col: Sequence[str],
        index: Sequence,
    ) -> tuple: ...
    def ARRAY_LENGTH(self, array: Sequence[str]) -> tuple: ...
    def ARRAY_SLICE(
        self,
        array: Sequence[str],
        start: Sequence[str | int | Sequence | None] | None,
        stop: Sequence[str | int | Sequence | None] | None,
    ) -> tuple: ...
    def ARRAY_SUBSET(
        self, array1: Sequence, not_in: bool, array2: Sequence
    ) -> tuple: ...
    def MAKE_ARRAY(self, *items) -> tuple: ...
    def __call__(self, ast: Sequence[str | list[str]]) -> Any: ...
    def __init__(
        self, provider: DBAPIProvider, ast: list[str | list | None]
    ) -> None: ...
    def _subquery(
        self, *sections: Sequence[str | list[str]]
    ) -> list[str | list[str]]: ...
    def build_json_path(
        self,
        path: list[list[(str | int | ParamKey | Converter)]],
    ) -> tuple[Param | Value, bool, bool]: ...
    def eval_json_path(self, values: list[str | int]) -> str: ...
    def make_param(
        self,
        param_class: type[_PT],
        paramkey: str | ParamKey | tuple[ParamKey | str, ...],
        *args,
    ) -> _PT: ...
    def make_composite_param(
        self,
        paramkey: tuple[ParamKey | str, ...],
        items: list[Param | Value],
        func: Callable,
    ) -> CompositeParam: ...
    def sql_join(
        self, join_type: str, sources: tuple[list[str | list], ...]
    ) -> list[str]: ...
