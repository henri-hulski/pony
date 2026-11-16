"""Static typing checks for the public ORM API.

This module is never executed by the test runner (its name does not start with
``test``). It is checked statically by both type checkers::

    pyright
    mypy

How to declare entities
-----------------------
Entities derive from ``db.Entity``. Pyright understands this directly because
``Database.Entity`` is annotated as ``type[Entity]``. Mypy does not: it only
accepts a base class that it can resolve to a class definition, and an
attribute of an *instance* (``db.Entity``) never qualifies, however it is
annotated. For mypy, declare the base class once next to the database::

    db = Database()

    if TYPE_CHECKING:
        from pony.orm.core import Entity
    else:
        Entity = db.Entity

and derive the entities from ``Entity``. At runtime ``Entity`` *is*
``db.Entity``; for the type checkers it is the generic ``Entity`` root class.
If ``Entity`` is imported from another module, list it in ``__all__`` so that
``mypy --strict`` accepts the re-export. Code that is only checked with pyright
can keep writing ``db.Entity`` directly; the alias is only needed for mypy.

Caveats of this pattern
-----------------------
The alias has no effect at runtime, but the type checkers and the runtime see
slightly different things behind the name ``Entity``:

* ``isinstance`` checks and annotations. For the type checkers ``Entity`` is
  the generic root class that every entity derives from. At runtime it is the
  ``db.Entity`` of one specific database. With several databases
  ``isinstance(obj, Entity)`` is ``False`` for an entity of another database,
  although the type checkers consider it an ``Entity``. Do not use the alias
  for ``isinstance`` checks that must hold across databases.
* Several databases in one module. Only one of them can own the name
  ``Entity``; give the others distinct names (``Entity1``, ``Entity2``, ...).
* Two different objects share one name. The ``Entity`` in your module and
  ``pony.orm.core.Entity`` are the same class for the type checkers but
  different objects at runtime, and type checker messages simply say
  ``Entity``, which can be ambiguous. Choose another name (for example
  ``Base``) if that is a problem, the pattern works the same way, using
  ``from pony.orm.core import Entity as Base`` in the ``TYPE_CHECKING`` block.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from pony.orm import (
    Database,
    Optional,
    PrimaryKey,
    Required,
    Set,
    db_session,
    select,
)
from pony.orm.core import Query, SetInstance

if TYPE_CHECKING:
    from typing_extensions import assert_type
else:

    def assert_type(val, typ, /):
        return val


__all__ = ["Car", "Entity", "Person", "db"]

db = Database()

if TYPE_CHECKING:
    from pony.orm.core import Entity
else:
    Entity = db.Entity


class Person(Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    age = Required(int)
    birthday = Optional(date)
    cars = Set("Car")


class Car(Entity):
    make = Required(str)
    owner = Required(Person)


def check_attribute_types() -> None:
    """Descriptors are inferred from the attribute constructor argument."""
    assert_type(Required(str), Required[str])
    assert_type(Required(int), Required[int])
    assert_type(Optional(date), Optional[date])
    # ``str`` is also a callable returning ``str``; this must not confuse mypy.
    assert_type(Optional(str), Optional[str])
    assert_type(PrimaryKey(str), PrimaryKey[str])
    assert_type(PrimaryKey(int, auto=True), PrimaryKey[int])
    # Lazy references to an entity class.
    assert_type(Required(lambda: Person), Required[Person])
    assert_type(Set(lambda: Car), Set[Car])
    # An entity referenced by name cannot be resolved statically: ``Any``, not
    # ``Never`` (mypy) or ``Unknown`` (pyright), so no annotation is needed.
    assert_type(Required("Person"), Required[Any])
    assert_type(Required(lambda: "Person"), Required[Any])
    assert_type(Set("Car"), Set[Any])

    assert_type(Person.name, Required[str])

    with db_session:
        person = Person(name="Ann", age=30)
        assert_type(person.name, str)
        assert_type(person.age, int)
        assert_type(person.cars, SetInstance[Any])

        car = Car(make="VW", owner=person)
        assert_type(car.owner, Person)
        assert_type(car.make, str)


def check_queries() -> None:
    with db_session:
        query = select(p for p in Person if p.age > 20)
        assert_type(query, Query)
        assert_type(Person.get(name="Ann"), Person | None)
