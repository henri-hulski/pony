from collections import defaultdict
from collections.abc import Sequence

from pony.orm.core import Database, Entity

class Bag:
    def __init__(self, database: Database) -> None: ...
    def to_dict(
        self,
    ) -> defaultdict[str, dict[int, dict[str, int | str | list | None]]]: ...

def to_dict(
    objects: Entity | Sequence[Entity],
) -> dict[str, dict[int, dict[str, int | str | list | None]]]: ...
