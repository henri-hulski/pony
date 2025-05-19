from types import ModuleType
from typing import ClassVar
from typing_extensions import LiteralString
from pony.orm import dbapiprovider
from pony.orm.core import DbConnection, PyType, SessionCache
from pony.orm.dbapiprovider import Converter, wrap_dbapi_exceptions
from pony.orm.dbproviders.postgres import (
    PGArrayConverter,
    PGBlobConverter,
    PGColumn,
    PGIntConverter,
    PGProvider,
    PGSchema,
    PGSQLBuilder,
    PGTimedeltaConverter,
    PGTranslator,
)
from pony.orm.dbschema import Column

NoneType: type[None]
provider_cls: type[CRProvider]

class CRArrayConverter(PGArrayConverter):
    array_types: ClassVar[dict[type[str | float], tuple[str, type[Converter]]]]

class CRBlobConverter(PGBlobConverter):
    def sql_type(converter) -> str: ...

class CRColumn(PGColumn):
    auto_template: ClassVar[str | None]

class CRIntConverter(PGIntConverter):
    signed_types: dict[None | int, str]
    unsigned_types: dict[None | int, str] | None

class CRProvider(PGProvider):
    array_converter_cls: type[PGArrayConverter]
    converter_classes: list[
        tuple[PyType | type[None] | tuple[type[int]], type[Converter]]  # noqa: Y090
    ]
    dbapi_module: ModuleType
    dbschema_cls: type[PGSchema]
    default_schema_name: str
    fk_types: dict[str, str]
    sqlbuilder_cls: type[PGSQLBuilder]
    translator_cls: type[PGTranslator]

    def normalize_name(provider, name: str): ...
    @wrap_dbapi_exceptions
    def set_transaction_mode(
        provider, connection: DbConnection, cache: SessionCache
    ): ...

class CRSchema(PGSchema):
    column_class: ClassVar[type[Column]]

class CRSQLBuilder(PGSQLBuilder): ...

class CRTimedeltaConverter(PGTimedeltaConverter):
    sql_type_name: LiteralString

class CRTranslator(PGTranslator): ...

class PGUuidConverter(dbapiprovider.UuidConverter):
    def py2sql(converter, val): ...
