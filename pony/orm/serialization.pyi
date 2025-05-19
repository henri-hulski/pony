from collections import defaultdict
from collections.abc import Sequence

from pony.orm.core import Database, Entity

class Bag:
    def __init__(bag, database: Database) -> None: ...
    def to_dict(
        bag,
    ) -> defaultdict[str, dict[int, dict[str, int | str | list | None]]]: ...

def to_dict(
    objects: Entity | Sequence[Entity],
) -> dict[str, dict[int, dict[str, int | str | list | None]]]: ...
