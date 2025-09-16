import typing

import pydantic

from .. import enums


class TransportBase(pydantic.BaseModel):
    name: str
    type: enums.TransportType
    courier_id: pydantic.StrictInt
    plate_number: pydantic.StrictStr
    average_speed: pydantic.StrictInt
    fuel_consumption: pydantic.StrictFloat
    payload: typing.Optional[pydantic.StrictFloat]
    width: typing.Optional[pydantic.StrictFloat] = None
    height: typing.Optional[pydantic.StrictFloat] = None
    depth: typing.Optional[pydantic.StrictFloat] = None

    # noinspection PyMethodParameters
    @pydantic.root_validator(skip_on_failure=True)
    def computing_capacity_and_checking_payload(cls, values) -> dict:
        values['capacity'] = None
        has_capacity_dimensions = False

        width, height, depth = values['width'], values['height'], values['depth']
        if width is not None and height is not None and depth is not None:
            has_capacity_dimensions = True

        transport_type = values['type']
        if transport_type == enums.TransportType.FOOT:
            if has_capacity_dimensions:
                raise ValueError(
                    f'Transport: {transport_type} cannot be provided '
                    'with width, height and depth dimensions',
                )

            foot_capacity_low_limit = 0
            foot_capacity_high_limit = 10

            payload = values.get('payload')
            if payload is None or any(
                [
                    payload <= foot_capacity_low_limit,
                    payload > foot_capacity_high_limit,
                ],
            ):
                raise ValueError(
                    f'Payload for transport: {transport_type} '
                    f'must be greater than {foot_capacity_low_limit} '
                    f'and less than or equal to {foot_capacity_high_limit}',
                )
        else:
            if not has_capacity_dimensions:
                raise ValueError(
                    f'Transport: {transport_type} must be provided '
                    'with width, height and depth dimensions',
                )

            values['capacity'] = width * height * depth
        return values


class Transport(TransportBase):
    pass


class TransportCreate(Transport):
    pass


class TransportUpdate(Transport):
    pass


class TransportGet(Transport):
    id: pydantic.StrictInt
    courier_id: pydantic.StrictInt


class TransportInternal(Transport):
    courier_id: pydantic.StrictInt
