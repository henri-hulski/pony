from builtins import dict as builtins_dict
from collections.abc import Callable

def decorator(caller: Callable, func: Callable | None = None) -> Callable: ...

class FunctionMaker:
    annotations: builtins_dict[str, object] | None
    defaults: tuple | None
    dict: builtins_dict[str, object] | None
    doc: str | None
    module: str | None
    name: str | None
    signature: str | None

    def __init__(
        self,
        func: Callable | None = None,
        name: str | None = None,
        signature: str | None = None,
        defaults: tuple | None = None,
        doc: str | None = None,
        module: str | None = None,
        funcdict: builtins_dict[str, object] | None = None,
    ) -> None: ...
    def update(self, func: Callable, **kw) -> None: ...
