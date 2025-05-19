from collections.abc import Sequence
from typing import Any, ClassVar

from _typeshed import MaybeNone
from typing_extensions import Self

from pony.orm.core import Attribute, DbConnection
from pony.orm.core import DBSchemaError as DBSchemaError
from pony.orm.core import EntityMeta, TableName
from pony.orm.dbapiprovider import Converter, DBAPIProvider

class DBSchema:
    provider: DBAPIProvider
    tables: dict[TableName, Table]
    constraints: dict[str, Constraint]
    indent: str
    command_separator: str
    uppercase: bool
    names: dict[TableName, Table]

    dialect: ClassVar[str | MaybeNone]
    inline_fk_syntax: ClassVar[bool]
    named_foreign_keys: ClassVar[bool]
    table_class: ClassVar[type[Table]]
    column_class: ClassVar[type[Column]]
    index_class: ClassVar[type[DBIndex]]
    fk_class: ClassVar[type[ForeignKey]]

    def __init__(schema, provider: DBAPIProvider, uppercase: bool = True) -> None: ...
    def add_table(
        schema,
        table_name: TableName,
        entity: EntityMeta | None = None,
    ) -> Table: ...
    def case(schema, s: str) -> str: ...
    def check_tables(
        schema, provider: DBAPIProvider, connection: DbConnection
    ) -> None: ...
    def column_list(
        schema,
        columns: Sequence[Column],
    ) -> str: ...
    def create_tables(
        schema, provider: DBAPIProvider, connection: DbConnection
    ) -> None: ...
    def generate_create_script(schema) -> str: ...
    def order_tables_to_create(schema) -> list[Table | Any]: ...

class DBObject:
    def create(table, provider: DBAPIProvider, connection: DbConnection) -> None: ...

class Table(DBObject):
    schema: DBSchema
    name: TableName
    column_list: list[Column]
    column_dict: dict[str, Column]
    columns: Sequence[str]
    indexes: dict[Sequence[Column], DBIndex]
    pk_index: DBIndex | None
    foreign_keys: dict[tuple[Column, ...], ForeignKey]
    parent_tables: set[Self]
    child_tables: set[Self]
    entities: set[EntityMeta]
    options: dict[str, object]
    m2m: set[Attribute]

    typename: ClassVar[str]

    def __init__(
        table,
        name: TableName,
        schema: DBSchema,
        entity: EntityMeta | None = None,
    ) -> None: ...
    def add_column(
        table,
        column_name: str,
        sql_type: str,
        converter: Converter,
        is_not_null: bool | None = None,
        sql_default: str | bool | None = None,
    ) -> Column: ...
    def add_entity(
        table,
        entity: EntityMeta,
    ) -> None: ...
    def add_foreign_key(
        table,
        fk_name: str | None,
        child_columns: tuple[Column, ...],
        parent_table: Self,
        parent_columns: tuple[Column, ...],
        index_name: str | None = None,
        on_delete: str | None = None,
        interleave: bool | None = None,
    ) -> ForeignKey: ...
    def add_index(
        table,
        index_name: str | bool | None,
        columns: Sequence[Column],
        is_pk: str | bool = False,
        is_unique: bool | None = None,
        m2m: bool = False,
    ) -> DBIndex: ...
    def exists(
        table,
        provider: DBAPIProvider,
        connection: DbConnection,
        case_sensitive: bool = True,
    ) -> str | None: ...
    def get_create_command(table) -> str: ...
    def get_objects_to_create(
        table, created_tables: set[Self] | None = None
    ) -> Sequence[Table | DBIndex | ForeignKey]: ...

class Column:
    table: Table
    name: str
    sql_type: str
    converter: Converter
    is_not_null: bool | None
    sql_default: str | bool | None
    is_pk: bool
    is_pk_part: bool
    is_unique: bool

    auto_template: ClassVar[str | None]

    def __init__(
        column,
        name: str,
        table: Table,
        sql_type: str,
        converter: Converter,
        is_not_null: bool | None = None,
        sql_default: str | bool | None = None,
    ) -> None: ...
    def get_sql(column) -> str: ...

class Constraint(DBObject):
    schema: DBSchema
    name: str | None

    def __init__(constraint, name: str | None, schema: DBSchema) -> None: ...

class DBIndex(Constraint):
    table: Table
    columns: Sequence[Column]
    is_pk: bool
    is_unique: bool | None

    typename: ClassVar[str]

    def __init__(
        index,
        name: str | None,
        table: Table,
        columns: Sequence[Column],
        is_pk: bool = False,
        is_unique: bool | None = None,
    ) -> None: ...
    def _get_create_sql(index, inside_table: bool) -> str: ...
    def exists(
        index,
        provider: DBAPIProvider,
        connection: DbConnection,
        case_sensitive: bool = True,
    ) -> str | None: ...
    def get_create_command(index) -> str: ...
    def get_sql(index) -> str: ...

class ForeignKey(Constraint):
    parent_table: Table
    parent_columns: tuple[Column, ...]
    child_table: Table
    child_columns: tuple[Column, ...]
    on_delete: str | None
    interleave: bool | None

    typename: ClassVar[str]

    def __init__(
        foreign_key,
        name: str,
        child_table: Table,
        child_columns: tuple[Column, ...],
        parent_table: Table,
        parent_columns: tuple[Column, ...],
        index_name: bool | None,
        on_delete: str | None,
        interleave: bool | None = None,
    ) -> None: ...
    def _get_create_sql(foreign_key, inside_table: bool) -> str: ...
    def get_sql(foreign_key) -> str: ...
    def get_create_command(foreign_key) -> str: ...
