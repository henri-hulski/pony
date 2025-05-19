from __future__ import annotations

from typing import cast

from typing_extensions import TypeAlias


class EntityMeta(type):
    _database_: Database


class Entity(metaclass=EntityMeta):
    pass


class Database:
    _Entity: TypeAlias = "Entity"
    Entity: type[_Entity]

    def __init__(self, *args, **kwargs) -> None:
        self.Entity = cast(
            type[Entity], type.__new__(EntityMeta, "Entity", (Entity,), {})
        )
        self.Entity._database_ = self


db = Database()


class User(db.Entity):
    pass
