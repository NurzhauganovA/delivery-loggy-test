import types

from . import biometry  # noqa: F401
from . import common  # noqa: F401
from . import dataloader  # noqa: F401
from . import excel_loader  # noqa: F401
from . import firebase  # noqa: F401
from . import geocoder  # noqa: F401
from . import sms  # noqa: F401
from . import router  # noqa: F401
from . import ws_monitoring  # noqa: F401


async def terminate_services() -> None:
    namespace = globals().copy()
    for name, module in namespace.items():
        if not isinstance(module, types.ModuleType):
            continue
        module_object = namespace[name]
        if not hasattr(module_object, 'service'):
            continue
        if hasattr(module_object.service, 'close'):
            await module_object.service.close()
