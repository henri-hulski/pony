from __future__ import absolute_import, annotations, print_function, division
from pony.py23compat import int_types

from decimal import Decimal
from datetime import date, datetime, timedelta
from binascii import hexlify

from pony import options
from pony.utils import datetime2timestamp, throw, is_ident
from pony.converting import timedelta2str
from pony.orm.ormtypes import RawSQL
from collections.abc import Callable, Iterable, Sequence
from pony.orm.core import (
    Adapter,
    Attribute,
    Entity,
    OptAttrValue,
    ParamKey,
    QueryResult,
    QueryVars,
)
from pony.orm.dbapiprovider import (
    ArrayConverter,
    Converter,
    DBAPIProvider,
    IntConverter,
    StrConverter,
)
import _typeshed
from typing import Any, ClassVar, TypeVar
from typing_extensions import Concatenate, Literal, ParamSpec, Unpack

_T = TypeVar("_T", bound="str | Value | Param | Sequence")
_PT = TypeVar("_PT", bound=Param)
_P = ParamSpec("_P")


class AstError(Exception):
    pass


class Param(object):
    __slots__ = "style", "id", "paramkey", "converter", "optimistic"
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
    ) -> None:
        param.style = paramstyle
        param.id = None
        param.paramkey = paramkey
        param.converter = converter
        param.optimistic = optimistic

    def eval(param, values: QueryVars) -> Any:
        varkey, i, j = param.paramkey
        value = values[varkey]
        if i is not None:
            t = type(value)
            if t is tuple:
                assert isinstance(value, tuple)
                value = value[i]
            elif t is RawSQL:
                assert isinstance(value, RawSQL)
                value = value.values[i]
            elif hasattr(value, "_get_items"):
                assert isinstance(value, QueryResult)
                value = value._get_items()[i]
            else:
                assert False, t
        if j is not None:
            assert type(type(value)).__name__ == "EntityMeta"
            assert isinstance(value, Entity)
            value = value._get_raw_pkval_()[j]
        converter = param.converter
        if value is not None and converter is not None:
            if converter.attr is None:
                value = converter.val2dbval(value)
            value = converter.py2sql(value)
        return value

    def __str__(param):
        paramstyle = param.style
        if paramstyle == "qmark":
            return "?"
        elif paramstyle == "format":
            return "%s"
        elif paramstyle == "numeric":
            return ":%d" % param.id
        elif paramstyle == "named":
            return ":p%d" % param.id
        elif paramstyle == "pyformat":
            return "%%(p%d)s" % param.id
        else:
            throw(NotImplementedError)

    def __repr__(param):
        return "%s(%r)" % (param.__class__.__name__, param.paramkey)


class CompositeParam(Param):
    __slots__ = "items", "func"

    def __init__(
        param,
        paramstyle: str,
        paramkey: tuple[ParamKey | str, ...],
        items: list[Param | Value],
        func: Callable,
    ) -> None:
        for item in items:
            assert isinstance(item, (Param, Value)), item
        Param.__init__(param, paramstyle, paramkey)
        param.items = items
        param.func = func

    def eval(
        param,
        values: (
            QueryVars
            | dict[Attribute, Entity | OptAttrValue]
            | list[Entity]
            | list[OptAttrValue]
            | tuple[int | str, ...]
        ),
    ) -> str:
        args = [
            item.eval(values) if isinstance(item, Param) else item.value
            for item in param.items
        ]
        return param.func(args)


class Value(object):
    __slots__ = "paramstyle", "value"

    def __init__(self, paramstyle: str, value: OptAttrValue) -> None:
        self.paramstyle = paramstyle
        self.value = value

    def __str__(self):
        value = self.value
        if value is None:
            return "null"
        if isinstance(value, bool):
            return value and "1" or "0"
        if isinstance(value, str):
            return self.quote_str(value)
        if isinstance(value, datetime):
            return "TIMESTAMP " + self.quote_str(datetime2timestamp(value))
        if isinstance(value, date):
            return "DATE " + self.quote_str(str(value))
        if isinstance(value, timedelta):
            return "INTERVAL '%s' HOUR TO SECOND" % timedelta2str(value)
        if isinstance(value, (int, float, Decimal)):
            return str(value)
        if isinstance(value, bytes):
            return "X'%s'" % hexlify(value).decode("ascii")
        assert False, repr(value)  # pragma: no cover

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

    def quote_str(self, s: str) -> str:
        if self.paramstyle in ("format", "pyformat"):
            s = s.replace("%", "%%")
        return "'%s'" % s.replace("'", "''")


def flat(tree: Any) -> list:
    stack = [tree]
    result = []
    stack_pop = stack.pop
    stack_extend = stack.extend
    result_append = result.append
    while stack:
        x = stack_pop()
        if isinstance(x, str):
            result_append(x)
        else:
            try:
                stack_extend(x)
            except TypeError:
                result_append(x)
    return result[::-1]


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
]:
    result = []
    for condition in conditions:
        if condition[0] == "AND":
            result.extend(flat_conditions(condition[1:]))
        else:
            result.append(condition)
    return result


def join(delimiter: str, items: Iterable[_T]) -> list[_T | str]:
    items = iter(items)
    try:
        result = [next(items)]
    except StopIteration:
        return []
    for item in items:
        result.append(delimiter)
        result.append(item)
    return result


def move_conditions_from_inner_join_to_where(
    sections: tuple[Sequence[str | list[str]], ...],
) -> Sequence[Sequence[str | list[str]]]:
    new_sections = list(sections)
    for i, section in enumerate(sections):
        if section[0] == "FROM":
            new_from_list = ["FROM"] + [list(item) for item in section[1:]]
            new_sections[i] = new_from_list
            if len(sections) > i + 1 and sections[i + 1][0] == "WHERE":
                new_where_list = list(sections[i + 1])
                new_sections[i + 1] = new_where_list
            else:
                new_where_list = ["WHERE"]
                new_sections.insert(i + 1, new_where_list)
            break
    else:
        return sections
    for join in new_from_list[2:]:
        assert isinstance(join, list)
        if join[1] in ("TABLE", "SELECT") and len(join) == 4:
            new_where_list.append(join.pop())
    return new_sections


def make_binary_op(symbol: str, default_parentheses: bool = False) -> Callable:
    def binary_op(builder, expr1, expr2, parentheses=None):
        if parentheses is None:
            parentheses = default_parentheses
        if parentheses:
            return "(", builder(expr1), symbol, builder(expr2), ")"
        return builder(expr1), symbol, builder(expr2)

    return binary_op


def make_unary_func(symbol: str) -> Callable:
    def unary_func(builder, expr):
        return "%s(" % symbol, builder(expr), ")"

    return unary_func


def indentable(
    method: Callable[Concatenate[SQLBuilder, _P], _T],
) -> Callable[Concatenate[SQLBuilder, _P], _T | tuple[str, _T]]:
    def new_method(
        builder: SQLBuilder, *args: _P.args, **kwargs: _P.kwargs
    ) -> _T | tuple[str, _T]:
        result = method(builder, *args, **kwargs)
        if builder.indent <= 1:
            return result
        return builder.indent_spaces * (builder.indent - 1), result

    new_method.__name__ = method.__name__
    return new_method


class SQLBuilder(object):
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

    dialect: ClassVar[str | _typeshed.MaybeNone] = None
    param_class: ClassVar[type[Param]] = Param
    composite_param_class: ClassVar[type[CompositeParam]] = CompositeParam
    value_class: type[Value] = Value
    indent_spaces: ClassVar[str] = " " * 4
    least_func_name: ClassVar[str] = "least"
    greatest_func_name: ClassVar[str] = "greatest"

    def __init__(
        builder, provider: DBAPIProvider, ast: list[str | list | None]
    ) -> None:
        builder.provider = provider
        builder.quote_name = provider.quote_name
        builder.paramstyle = paramstyle = provider.paramstyle
        builder.ast = ast
        builder.indent = 0
        builder.keys = {}
        builder.inner_join_syntax = options.INNER_JOIN_SYNTAX
        builder.suppress_aliases = False
        builder.result = flat(builder(ast))
        params = tuple(x for x in builder.result if isinstance(x, Param))
        layout = []
        for i, param in enumerate(params):
            if param.id is None:
                param.id = i + 1
            layout.append(param.paramkey)
        builder.layout = layout
        builder.sql = "".join(map(str, builder.result)).rstrip("\n")
        if paramstyle in ("qmark", "format"):

            def adapter(values):  # type: ignore[no-untyped-def]
                return tuple(param.eval(values) for param in params)

        elif paramstyle == "numeric":

            def adapter(values):  # type: ignore[no-untyped-def]
                return tuple(param.eval(values) for param in params)

        elif paramstyle in ("named", "pyformat"):

            def adapter(values):
                return {"p%d" % param.id: param.eval(values) for param in params}

        else:
            throw(NotImplementedError, paramstyle)
        builder.params = params
        builder.adapter = adapter

    def __call__(builder, ast: Sequence[str | list[str]]) -> Any:
        if isinstance(ast, str):
            throw(AstError, "An SQL AST list was expected. Got string: %r" % ast)
        symbol = ast[0]
        if not isinstance(symbol, str):
            throw(AstError, "Invalid node name in AST: %r" % ast)
        method = getattr(builder, symbol, None)
        if method is None:
            throw(AstError, "Method not found: %s" % symbol)
        try:
            assert method is not None
            return method(*ast[1:])
        except TypeError:
            raise

    ##            traceback = sys.exc_info()[2]
    ##            if traceback.tb_next is None:
    ##                del traceback
    ##                throw(AstError, 'Invalid data for method %s: %r'
    ##                               % (symbol, ast[1:]))
    ##            else:
    ##                del traceback
    ##                raise
    def INSERT(
        builder,
        table_name: str,
        columns: Iterable[str | Iterable],
        values: Iterable[Sequence[str | tuple[int, None, None] | Converter]],
        returning: str | None = None,
    ) -> Sequence[str | list[str]]:
        return [
            "INSERT INTO ",
            builder.quote_name(table_name),
            " (",
            join(", ", [builder.quote_name(column) for column in columns]),
            ") VALUES (",
            join(", ", [builder(value) for value in values]),
            ")",
        ]

    def DEFAULT(builder):
        return "DEFAULT"

    def UPDATE(
        builder,
        table_name: str,
        pairs: list[tuple[str, list[str | tuple[int, None, None] | Converter]]],
        where: list[str | list[str | list]] | None = None,
    ) -> list[str | list]:
        return [
            "UPDATE ",
            builder.quote_name(table_name),
            "\nSET ",
            join(
                ", ",
                [
                    (builder.quote_name(name), " = ", builder(param))
                    for name, param in pairs
                ],
            ),
            where and ["\n", builder(where)] or [],
        ]

    def DELETE(
        builder,
        alias: str | None,
        from_ast: list[str | list[str | None] | list[str]],
        where: list[str | list] | None = None,
    ) -> tuple:
        builder.indent += 1
        if alias is not None:
            assert isinstance(alias, str)
            if not where:
                return "DELETE ", builder.quote_name(alias), " ", builder(from_ast)
            return (
                "DELETE ",
                builder.quote_name(alias),
                " ",
                builder(from_ast),
                builder(where),
            )
        else:
            assert (
                from_ast[0] == "FROM"
                and len(from_ast) == 2
                and from_ast[1][1] == "TABLE"
            )
            alias = from_ast[1][0]
            if alias is not None:
                builder.suppress_aliases = True
            if not where:
                return "DELETE ", builder(from_ast)
            return "DELETE ", builder(from_ast), builder(where)

    def _subquery(
        builder, *sections: Sequence[str | list[str]]
    ) -> list[str | list[str]]:
        builder.indent += 1
        if not builder.inner_join_syntax:
            new_sections = move_conditions_from_inner_join_to_where(sections)
        result = [builder(s) for s in new_sections]
        builder.indent -= 1
        return result

    def SELECT(
        builder, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | list[str]]]:
        prev_suppress_aliases = builder.suppress_aliases
        builder.suppress_aliases = False
        try:
            result = builder._subquery(*sections)
            if builder.indent:
                indent = builder.indent_spaces * builder.indent
                return "(\n", result, indent + ")"
            return result
        finally:
            builder.suppress_aliases = prev_suppress_aliases

    def SELECT_FOR_UPDATE(
        builder, nowait: bool, skip_locked: bool, *sections: Sequence[str | list[str]]
    ) -> (
        Sequence[str | Sequence[str | list[str]]]
        | tuple[Sequence[str | Sequence[str | list[str]]], str, str, str, str]
    ):
        assert not builder.indent
        result = builder.SELECT(*sections)
        nowait_str = " NOWAIT" if nowait else ""
        skip_locked_str = " SKIP LOCKED" if skip_locked else ""
        return result, "FOR UPDATE", nowait_str, skip_locked_str, "\n"

    def EXISTS(
        builder, *sections: Sequence[str | list[str]]
    ) -> tuple[str, str, str, list, str, str]:
        result = builder._subquery(*sections)
        indent = builder.indent_spaces * builder.indent
        return "EXISTS (\n", indent, "SELECT 1\n", result, indent, ")"

    def NOT_EXISTS(
        builder, *sections: Sequence[str | list[str]]
    ) -> tuple[str, tuple[str, str, str, list, str, str]]:
        return "NOT ", builder.EXISTS(*sections)

    @indentable
    def ALL(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        exprs = [builder(e) for e in expr_list]
        return "SELECT ", join(", ", exprs), "\n"

    @indentable
    def DISTINCT(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        exprs = [builder(e) for e in expr_list]
        return "SELECT DISTINCT ", join(", ", exprs), "\n"

    @indentable
    def AGGREGATES(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        exprs = [builder(e) for e in expr_list]
        return "SELECT ", join(", ", exprs), "\n"

    def AS(builder, expr: list, alias: str) -> tuple[Sequence, str, str]:
        return builder(expr), " AS ", builder.quote_name(alias)

    def compound_name(builder, name_parts):
        return ".".join(p and builder.quote_name(p) or "" for p in name_parts)

    def sql_join(
        builder, join_type: str, sources: tuple[list[str | list], ...]
    ) -> list[str]:
        indent = builder.indent_spaces * (builder.indent - 1)
        indent2 = indent + builder.indent_spaces
        indent3 = indent2 + builder.indent_spaces
        result = [indent, "FROM "]
        for i, source in enumerate(sources):
            if len(source) == 3:
                alias, kind, x = source
                join_cond = None
            elif len(source) == 4:
                alias, kind, x, join_cond = source
            else:
                throw(AstError, "Invalid source in FROM section: %r" % source)
            if i > 0:
                if join_cond is None:
                    result.append(", ")
                else:
                    result += ["\n", indent, "  %s JOIN " % join_type]
            if builder.suppress_aliases:
                alias = None
            elif alias is not None:
                alias = builder.quote_name(alias)
            if kind == "TABLE":
                if isinstance(x, str):
                    result.append(builder.quote_name(x))
                else:
                    result.append(builder.compound_name(x))
                if alias is not None:
                    result += " ", alias  # Oracle does not support 'AS' here
            elif kind == "SELECT":
                if alias is None:
                    throw(AstError, "Subquery in FROM section must have an alias")
                result += [
                    builder.SELECT(*x),
                    " ",
                    alias,
                ]  # Oracle does not support 'AS' here
            else:
                throw(AstError, "Invalid source kind in FROM section: %r" % kind)
            if join_cond is not None:
                result += ["\n", indent2, "ON ", builder(join_cond)]
        result.append("\n")
        return result

    def FROM(builder, *sources) -> list[str]:
        return builder.sql_join("INNER", sources)

    def INNER_JOIN(builder, *sources) -> list[str]:
        builder.inner_join_syntax = True
        return builder.sql_join("INNER", sources)

    @indentable
    def LEFT_JOIN(builder, *sources) -> Sequence[str | Sequence[str | list[str]]]:
        return builder.sql_join("LEFT", sources)

    def WHERE(builder, *conditions) -> str | list[str]:
        if not conditions:
            return ""
        conditions = flat_conditions(conditions)
        indent = builder.indent_spaces * (builder.indent - 1)
        result = [indent, "WHERE "]
        extend = result.extend
        extend((builder(conditions[0]), "\n"))
        for condition in conditions[1:]:
            extend((indent, "  AND ", builder(condition), "\n"))
        return result

    def HAVING(builder, *conditions) -> str | list[str]:
        if not conditions:
            return ""
        conditions = flat_conditions(conditions)
        indent = builder.indent_spaces * (builder.indent - 1)
        result = [indent, "HAVING "]
        extend = result.extend
        extend((builder(conditions[0]), "\n"))
        for condition in conditions[1:]:
            extend((indent, "  AND ", builder(condition), "\n"))
        return result

    @indentable
    def GROUP_BY(
        builder, *expr_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        exprs = [builder(e) for e in expr_list]
        return "GROUP BY ", join(", ", exprs), "\n"

    @indentable
    def UNION(
        builder, kind, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        return "UNION ", kind, "\n", builder.SELECT(*sections)

    @indentable
    def INTERSECT(
        builder, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        return "INTERSECT\n", builder.SELECT(*sections)

    @indentable
    def EXCEPT(
        builder, *sections: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        return "EXCEPT\n", builder.SELECT(*sections)

    @indentable
    def ORDER_BY(
        builder, *order_list: Sequence[str | list[str]]
    ) -> Sequence[str | Sequence[str | Sequence[str | list[str]]]]:
        result = ["ORDER BY "]
        result.extend(join(", ", [builder(expr) for expr in order_list]))
        result.append("\n")
        return result

    def DESC(builder, expr: list[int | str]) -> tuple[Value | Sequence, str]:
        return builder(expr), " DESC"

    @indentable
    def LIMIT(
        builder, limit: int | None | Literal["null"], offset: int | None = None
    ) -> str | Sequence[str]:
        if limit is None:
            limit = "null"
        else:
            assert isinstance(limit, int_types)
        assert offset is None or isinstance(offset, int)
        if offset:
            return "LIMIT %s OFFSET %d\n" % (limit, offset)
        else:
            return "LIMIT %s\n" % limit

    def COLUMN(builder, table_alias: str | None, col_name: str) -> list[str]:
        if builder.suppress_aliases or not table_alias:
            return ["%s" % builder.quote_name(col_name)]
        return [
            "%s.%s" % (builder.quote_name(table_alias), builder.quote_name(col_name))
        ]

    def PARAM(
        builder,
        paramkey: str | ParamKey,
        converter: Converter | None = None,
        optimistic: bool = False,
    ) -> Param:
        return builder.make_param(builder.param_class, paramkey, converter, optimistic)

    def make_param(
        builder,
        param_class: type[_PT],
        paramkey: str | ParamKey | tuple[ParamKey | str, ...],
        *args,
    ) -> _PT:
        keys = builder.keys
        param = keys.get(paramkey)
        if param is None:
            param = param_class(builder.paramstyle, paramkey, *args)
            keys[paramkey] = param
        assert isinstance(param, param_class)
        return param

    def make_composite_param(
        builder,
        paramkey: tuple[ParamKey | str, ...],
        items: list[Param | Value],
        func: Callable,
    ) -> CompositeParam:
        return builder.make_param(builder.composite_param_class, paramkey, items, func)

    def STAR(builder, table_alias: str) -> tuple[str, str]:
        return builder.quote_name(table_alias), ".*"

    def ROW(builder, *items) -> tuple[str, list[Value | str | list[str]], str]:
        return "(", join(", ", map(builder, items)), ")"

    def VALUE(builder, value: OptAttrValue) -> Value:
        return builder.value_class(builder.paramstyle, value)

    def AND(builder, *cond_list) -> list[str | tuple[list[str], str]]:
        cond_list = [builder(condition) for condition in cond_list]
        return join(" AND ", cond_list)

    def OR(builder, *cond_list) -> tuple[str, list[str | tuple[list[str], str]], str]:
        cond_list = [builder(condition) for condition in cond_list]
        return "(", join(" OR ", cond_list), ")"

    def NOT(builder, condition: list[str | list]) -> tuple[str, tuple, str]:
        return "NOT (", builder(condition), ")"

    def POW(
        builder, expr1: list[int | str | list], expr2: list[int | str | list]
    ) -> tuple[str, Value | tuple, str, Value | tuple, str]:
        return "power(", builder(expr1), ", ", builder(expr2), ")"

    EQ = make_binary_op(" = ")
    NE = make_binary_op(" <> ")
    LT = make_binary_op(" < ")
    LE = make_binary_op(" <= ")
    GT = make_binary_op(" > ")
    GE = make_binary_op(" >= ")
    ADD = make_binary_op(" + ", True)
    SUB = make_binary_op(" - ", True)
    MUL = make_binary_op(" * ", True)
    DIV = make_binary_op(" / ", True)
    FLOORDIV = make_binary_op(" / ", True)

    def MOD(builder, a, b):
        symbol = " %% " if builder.paramstyle in ("format", "pyformat") else " % "
        return "(", builder(a), symbol, builder(b), ")"

    def FLOAT_EQ(builder, a, b):
        a, b = builder(a), builder(b)
        return (
            "abs(",
            a,
            " - ",
            b,
            ") / coalesce(nullif(greatest(abs(",
            a,
            "), abs(",
            b,
            ")), 0), 1) <= 1e-14",
        )

    def FLOAT_NE(builder, a, b):
        a, b = builder(a), builder(b)
        return (
            "abs(",
            a,
            " - ",
            b,
            ") / coalesce(nullif(greatest(abs(",
            a,
            "), abs(",
            b,
            ")), 0), 1) > 1e-14",
        )

    def CONCAT(builder, *args) -> tuple[str, list, str]:
        return "(", join(" || ", map(builder, args)), ")"

    def NEG(builder, expr: list[str]) -> tuple[str, list[str], str]:
        return "-(", builder(expr), ")"

    def IS_NULL(
        builder, expr: list[str | list[str | list] | type[None]]
    ) -> tuple[Sequence, str]:
        return builder(expr), " IS NULL"

    def IS_NOT_NULL(
        builder, expr: list[str | list | type[None]]
    ) -> tuple[Sequence, str]:
        return builder(expr), " IS NOT NULL"

    def LIKE(
        builder,
        expr: list[str | list[str | list]],
        template: list[str | list[str | list]],
        escape: list[str] | None = None,
    ) -> tuple[Unpack[tuple], str, Value]:
        result = builder(expr), " LIKE ", builder(template)
        if escape:
            result = result + (" ESCAPE ", builder(escape))
        return result

    def NOT_LIKE(
        builder,
        expr: list[str],
        template: list[str | list[str | list]],
        escape: list[str] | None = None,
    ) -> tuple[Unpack[tuple], str, Value]:
        result = builder(expr), " NOT LIKE ", builder(template)
        if escape:
            result = result + (" ESCAPE ", builder(escape))
        return result

    def BETWEEN(builder, expr1, expr2, expr3):
        return builder(expr1), " BETWEEN ", builder(expr2), " AND ", builder(expr3)

    def NOT_BETWEEN(builder, expr1, expr2, expr3):
        return builder(expr1), " NOT BETWEEN ", builder(expr2), " AND ", builder(expr3)

    def IN(builder, expr1: list, x: list) -> (
        str
        | tuple[
            list[str] | tuple[str, list, str],
            str,
            list[str | Param | Value | tuple[str, list, str]],
            str,
        ]
        | tuple[Value | Param | list[str], str, tuple[str, list, str]]
    ):
        if not x:
            return "0 = 1"
        if len(x) >= 1 and x[0] == "SELECT":
            return builder(expr1), " IN ", builder(x)
        expr_list = [builder(expr) for expr in x]
        return builder(expr1), " IN (", join(", ", expr_list), ")"

    def NOT_IN(builder, expr1: list, x: list) -> (
        str
        | tuple[
            list[str] | tuple[str, list, str],
            str,
            list[str | Param | Value | tuple[str, list, str]],
            str,
        ]
        | tuple[Value | Param | list[str], str, tuple[str, list, str]]
    ):
        if not x:
            return "1 = 1"
        if len(x) >= 1 and x[0] == "SELECT":
            return builder(expr1), " NOT IN ", builder(x)
        expr_list = [builder(expr) for expr in x]
        return builder(expr1), " NOT IN (", join(", ", expr_list), ")"

    def COUNT(builder, distinct: bool | None, *expr_list) -> Sequence:
        assert distinct in (None, True, False)
        if not distinct:
            if not expr_list:
                return ["COUNT(*)"]
            if builder.dialect == "PostgreSQL":
                return "COUNT(", builder.ROW(*expr_list), ")"
            else:
                return "COUNT(", join(", ", map(builder, expr_list)), ")"
        if not expr_list:
            throw(AstError, "COUNT(DISTINCT) without argument")
        if len(expr_list) == 1:
            return "COUNT(DISTINCT ", builder(expr_list[0]), ")"

        if builder.dialect == "PostgreSQL":
            return "COUNT(DISTINCT ", builder.ROW(*expr_list), ")"
        elif builder.dialect == "MySQL":
            return "COUNT(DISTINCT ", join(", ", map(builder, expr_list)), ")"
        # Oracle and SQLite queries translated to completely different subquery syntax
        else:
            throw(NotImplementedError)  # This line must not be executed

    def SUM(
        builder, distinct: bool | None, expr: list[str]
    ) -> tuple[str, list[str], str]:
        assert distinct in (None, True, False)
        return (
            distinct and "coalesce(SUM(DISTINCT " or "coalesce(SUM(",
            builder(expr),
            "), 0)",
        )

    def AVG(builder, distinct: bool | None, expr: list) -> tuple[str, Sequence, str]:
        assert distinct in (None, True, False)
        return distinct and "AVG(DISTINCT " or "AVG(", builder(expr), ")"

    def GROUP_CONCAT(
        builder, distinct: bool | None, expr: list[str], sep: list[str] | None = None
    ) -> tuple[tuple, str]:
        assert distinct in (None, True, False)
        result = distinct and "GROUP_CONCAT(DISTINCT " or "GROUP_CONCAT(", builder(expr)
        if sep is not None:
            if builder.provider.dialect == "MySQL":
                result = result, " SEPARATOR ", builder(sep)
            else:
                result = result, ", ", builder(sep)
        return result, ")"

    UPPER = make_unary_func("upper")
    LOWER = make_unary_func("lower")
    LENGTH = make_unary_func("length")
    ABS = make_unary_func("abs")

    def COALESCE(builder, *args) -> tuple[str, list, str]:
        if len(args) < 2:
            assert False  # pragma: no cover
        return "coalesce(", join(", ", map(builder, args)), ")"

    def MIN(builder, distinct: bool | None, *args) -> tuple[str, str, list, str]:
        assert not distinct, distinct
        if len(args) == 0:
            assert False  # pragma: no cover
        elif len(args) == 1:
            fname = "MIN"
        else:
            fname = builder.least_func_name
        return fname, "(", join(", ", map(builder, args)), ")"

    def MAX(builder, distinct: bool | None, *args) -> tuple[str, str, list, str]:
        assert not distinct, distinct
        if len(args) == 0:
            assert False  # pragma: no cover
        elif len(args) == 1:
            fname = "MAX"
        else:
            fname = builder.greatest_func_name
        return fname, "(", join(", ", map(builder, args)), ")"

    def SUBSTR(
        builder,
        expr: list[str | list[str]],
        start: list[str | int | list[str | int | list]],
        len: list[str | int] | None = None,
    ) -> tuple:
        if len is None:
            return "substr(", builder(expr), ", ", builder(start), ")"
        return "substr(", builder(expr), ", ", builder(start), ", ", builder(len), ")"

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
    ]:
        if start is None:
            start = ["VALUE", 0]

        if start[0] == "VALUE":
            start_value = start[1]
            assert isinstance(start_value, int)
            if builder.dialect == "PostgreSQL" and start_value < 0:
                index_sql = ["LENGTH", expr]
                if start_value < -1:
                    index_sql = ["SUB", index_sql, ["VALUE", -(start_value + 1)]]
            else:
                if start_value >= 0:
                    start_value += 1
                index_sql = ["VALUE", start_value]
        else:
            inner_sql = start
            then = ["ADD", inner_sql, ["VALUE", 1]]
            else_ = (
                ["ADD", ["LENGTH", expr], then]
                if builder.dialect == "PostgreSQL"
                else inner_sql
            )
            index_sql = ["IF", ["GE", inner_sql, ["VALUE", 0]], then, else_]

        if stop is None:
            len_sql = None
        elif stop[0] == "VALUE":
            stop_value = stop[1]
            assert isinstance(stop_value, int)
            if start[0] == "VALUE":
                start_value = start[1]
                assert isinstance(start_value, int)
                if start_value >= 0 and stop_value >= 0:
                    len_sql = ["VALUE", stop_value - start_value]
                elif start_value < 0 and stop_value < 0:
                    len_sql = ["VALUE", stop_value - start_value]
                elif start_value >= 0 and stop_value < 0:
                    len_sql = [
                        "SUB",
                        ["LENGTH", expr],
                        ["VALUE", start_value - stop_value],
                    ]
                    len_sql = ["MAX", False, len_sql, ["VALUE", 0]]
                elif start_value < 0 and stop_value >= 0:
                    len_sql = ["SUB", ["VALUE", stop_value + 1], index_sql]
                    len_sql = ["MAX", False, len_sql, ["VALUE", 0]]
                else:
                    assert False  # pragma: nocover1
            else:
                start_sql = ["COALESCE", start, ["VALUE", 0]]
                if stop_value >= 0:
                    start_positive = ["SUB", stop, start_sql]
                    start_negative = ["SUB", ["VALUE", stop_value + 1], index_sql]
                else:
                    start_positive = [
                        "SUB",
                        ["LENGTH", expr],
                        ["ADD", start_sql, ["VALUE", -stop_value]],
                    ]
                    start_negative = ["SUB", stop, start_sql]
                len_sql = [
                    "IF",
                    ["GE", start_sql, ["VALUE", 0]],
                    start_positive,
                    start_negative,
                ]
                len_sql = ["MAX", False, len_sql, ["VALUE", 0]]
        else:
            stop_sql = ["COALESCE", stop, ["VALUE", -1]]
            if start[0] == "VALUE":
                start_value = start[1]
                assert isinstance(start_value, int)
                start_sql = ["VALUE", start_value]
                if start_value >= 0:
                    stop_positive = ["SUB", stop_sql, start_sql]
                    stop_negative = [
                        "SUB",
                        ["LENGTH", expr],
                        ["SUB", start_sql, stop_sql],
                    ]
                else:
                    stop_positive = ["SUB", ["ADD", stop_sql, ["VALUE", 1]], index_sql]
                    stop_negative = ["SUB", stop_sql, start_sql]
                len_sql = [
                    "IF",
                    ["GE", stop_sql, ["VALUE", 0]],
                    stop_positive,
                    stop_negative,
                ]
                len_sql = ["MAX", False, len_sql, ["VALUE", 0]]
            else:
                start_sql = ["COALESCE", start, ["VALUE", 0]]
                both_positive = ["SUB", stop_sql, start_sql]
                both_negative = both_positive
                start_positive = ["SUB", ["LENGTH", expr], ["SUB", start_sql, stop_sql]]
                stop_positive = ["SUB", ["ADD", stop_sql, ["VALUE", 1]], index_sql]
                len_sql = [
                    "CASE",
                    None,
                    [
                        (
                            [
                                "AND",
                                ["GE", start_sql, ["VALUE", 0]],
                                ["GE", stop_sql, ["VALUE", 0]],
                            ],
                            both_positive,
                        ),
                        (
                            [
                                "AND",
                                ["LT", start_sql, ["VALUE", 0]],
                                ["LT", stop_sql, ["VALUE", 0]],
                            ],
                            both_negative,
                        ),
                        (
                            [
                                "AND",
                                ["GE", start_sql, ["VALUE", 0]],
                                ["LT", stop_sql, ["VALUE", 0]],
                            ],
                            start_positive,
                        ),
                        (
                            [
                                "AND",
                                ["LT", start_sql, ["VALUE", 0]],
                                ["GE", stop_sql, ["VALUE", 0]],
                            ],
                            stop_positive,
                        ),
                    ],
                ]
                len_sql = ["MAX", False, len_sql, ["VALUE", 0]]
        sql = ["SUBSTR", expr, index_sql, len_sql]
        return builder(sql)

    def CASE(builder, expr: None, cases: list, default: list | None = None) -> list:
        if (
            expr is None
            and default is not None
            and default[0] == "CASE"
            and default[1] is None
        ):
            cases2, default2 = default[2:]
            return builder.CASE(None, tuple(cases) + tuple(cases2), default2)
        result = ["case"]
        if expr is not None:
            result.append(" ")
            result.extend(builder(expr))
        for condition, expr in cases:
            result.extend((" when ", builder(condition), " then ", builder(expr)))
        if default is not None:
            result.extend((" else ", builder(default)))
        result.append(" end")
        return result

    def IF(
        builder, cond: list[str | list], then: list[str | list], else_: list[str | list]
    ) -> list[str | Param | list[str] | tuple]:
        return builder.CASE(None, [(cond, then)], else_)

    def TRIM(
        builder, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]:
        if chars is None:
            return "trim(", builder(expr), ")"
        return "trim(", builder(expr), ", ", builder(chars), ")"

    def LTRIM(
        builder, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]:
        if chars is None:
            return "ltrim(", builder(expr), ")"
        return "ltrim(", builder(expr), ", ", builder(chars), ")"

    def RTRIM(
        builder, expr: list[str], chars: list[str | tuple | StrConverter] | None = None
    ) -> tuple[str, list[str], str] | tuple[str, list[str], str, Value | Param, str]:
        if chars is None:
            return "rtrim(", builder(expr), ")"
        return "rtrim(", builder(expr), ", ", builder(chars), ")"

    def REPLACE(
        builder,
        str: list[str | StrConverter | Sequence],
        from_: list[str],
        to: list[str],
    ) -> tuple[str, Param | Sequence, str, Value, str, Value, str]:
        return "replace(", builder(str), ", ", builder(from_), ", ", builder(to), ")"

    def TO_INT(
        builder, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]:
        return "CAST(", builder(expr), " AS integer)"

    def TO_STR(
        builder, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]:
        return "CAST(", builder(expr), " AS text)"

    def TO_REAL(
        builder, expr: list[str | list[str] | list[str | int]]
    ) -> tuple[str, list[str] | tuple, str]:
        return "CAST(", builder(expr), " AS real)"

    def TODAY(builder):
        return "CURRENT_DATE"

    def NOW(builder):
        return "CURRENT_TIMESTAMP"

    def DATE(builder, expr: Sequence[str | list[str]]) -> tuple[str, Any, str]:
        return "DATE(", builder(expr), ")"

    def YEAR(builder, expr):
        return "EXTRACT(YEAR FROM ", builder(expr), ")"

    def MONTH(builder, expr):
        return "EXTRACT(MONTH FROM ", builder(expr), ")"

    def DAY(builder, expr):
        return "EXTRACT(DAY FROM ", builder(expr), ")"

    def HOUR(builder, expr):
        return "EXTRACT(HOUR FROM ", builder(expr), ")"

    def MINUTE(builder, expr):
        return "EXTRACT(MINUTE FROM ", builder(expr), ")"

    def SECOND(builder, expr):
        return "EXTRACT(SECOND FROM ", builder(expr), ")"

    def RANDOM(builder):
        return "RAND()"

    def RAWSQL(
        builder, sql: list[str | list[str | ParamKey | Converter]]
    ) -> str | list[str | Param]:
        if isinstance(sql, str):
            return sql
        return [x if isinstance(x, str) else builder(x) for x in sql]

    def build_json_path(
        builder, path: list[list[(str | int | ParamKey | Converter)]]
    ) -> tuple[Param | Value, bool, bool]:
        empty_slice = slice(None, None, None)
        has_params = False
        has_wildcards = False
        items = [builder(element) for element in path]
        for item in items:
            if isinstance(item, Param):
                has_params = True
            elif isinstance(item, Value):
                value = item.value
                if value is Ellipsis or value == empty_slice:
                    has_wildcards = True
                else:
                    assert isinstance(value, (int, str)), value
            else:
                assert False, item
        if has_params:
            paramkey = tuple(
                (
                    item.paramkey
                    if isinstance(item, Param)
                    else None if type(item.value) is slice else item.value
                )
                for item in items
            )
            path_sql = builder.make_composite_param(
                paramkey, items, builder.eval_json_path
            )
        else:
            result_value = builder.eval_json_path(item.value for item in items)
            path_sql = builder.value_class(builder.paramstyle, result_value)
        return path_sql, has_params, has_wildcards

    @classmethod
    def eval_json_path(cls, values: list[str | int]) -> str:
        result = ["$"]
        append = result.append
        empty_slice = slice(None, None, None)
        for value in values:
            if isinstance(value, int):
                append("[%d]" % value)
            elif isinstance(value, str):
                append(
                    "." + value
                    if is_ident(value)
                    else '."%s"' % value.replace('"', '\\"')
                )
            elif value is Ellipsis:
                append(".*")
            elif value == empty_slice:
                append("[*]")
            else:
                assert False, value
        return "".join(result)

    def JSON_QUERY(builder, expr: Sequence[str], path: Sequence[Sequence]) -> tuple:
        throw(NotImplementedError)

    def JSON_VALUE(
        builder,
        expr: Sequence[str],
        path: Sequence[Sequence],
        type: type[OptAttrValue] | _typeshed.MaybeNone,
    ) -> tuple:
        throw(NotImplementedError)

    def JSON_NONZERO(builder, expr: Sequence[str | Sequence]) -> tuple:
        throw(NotImplementedError)

    def JSON_CONCAT(builder, left, right):
        throw(NotImplementedError)

    def JSON_CONTAINS(
        builder, expr: Sequence[str], path: list[Sequence[str]], key: Sequence
    ) -> Sequence:
        throw(NotImplementedError)

    def JSON_ARRAY_LENGTH(builder, value: Sequence[str | Sequence]) -> tuple:
        throw(NotImplementedError)

    def JSON_PARAM(builder, expr: Sequence[str | Sequence | Converter]) -> tuple:
        return builder(expr)

    def ARRAY_INDEX(builder, col: Sequence[str], index: Sequence) -> tuple:
        throw(NotImplementedError)

    def ARRAY_CONTAINS(
        builder, key: Sequence[str | float], not_in: bool, col: Sequence[str]
    ) -> tuple:
        throw(NotImplementedError)

    def ARRAY_SUBSET(
        builder, array1: Sequence, not_in: bool, array2: Sequence
    ) -> tuple:
        throw(NotImplementedError)

    def ARRAY_LENGTH(builder, array: Sequence[str]) -> tuple:
        throw(NotImplementedError)

    def ARRAY_SLICE(
        builder,
        array: Sequence[str],
        start: Sequence[str | int | Sequence | None] | None,
        stop: Sequence[str | int | Sequence | None] | None,
    ) -> tuple:
        throw(NotImplementedError)

    def MAKE_ARRAY(builder, *items) -> tuple:
        throw(NotImplementedError)
