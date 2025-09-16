from pathlib import Path
from typing import Any, Dict, Sequence

custom_types = [
    'predicate_failed', 'ip_any_interface', 'pattern_str_type', 'ip_v4_interface',
    'color_error', 'ip_v6_interface', 'ip_any_address', 'enum', 'ip_any_network',
    'pattern_bytes_type', 'pattern_type', 'import_error', 'ip_v6_network',
    'pattern_regex', 'ip_v4_address', 'ip_v6_address', 'path_type', 'sequence_str',
    'ip_v4_network'
]

special_msg = ['JSON decode error']


async def __msg_to_template(msg: str, context: Dict[str, Any] | None = None) -> str:
    if not context:
        return msg

    if msg in special_msg:
        return msg

    for ctx_key in context.keys():
        placeholder = "{" + ctx_key + "}"
        msg = msg.replace(str(context[ctx_key]), placeholder)

    return msg


async def __translate_msg(
    t: 'Translator',  # type: ignore # noqa: F821
    msg: str,
    context: Dict[str, Any]) -> str:
    return await t.t(
        await __msg_to_template(msg, context),
        **context,
    ) if msg not in special_msg else msg


async def translate_error(
    t: 'Translator',  # type: ignore # noqa: F821
    msg: str,
    **context,
) -> str:
    return await t.t(
        await __msg_to_template(msg, context),
        **context,
    ) if msg not in special_msg else msg


async def translate_errors(
    t: 'Translator',  # type: ignore # noqa: F821
    errors: Sequence[Any]
) -> list[Dict[str, Any], None, None]:
    return [
        {
            **error,
            'msg': await __translate_msg(t, error['msg'], error.get('ctx', {}))
        } for error in errors
    ]


async def get_package_root() -> Path:
    return Path(__file__).parent
