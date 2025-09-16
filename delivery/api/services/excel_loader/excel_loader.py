import time
from datetime import datetime
from datetime import timedelta
from io import BytesIO

import loguru
import pandas as pd
import tortoise
from fastapi import UploadFile
from loguru import logger
from starlette.concurrency import run_in_threadpool
from tortoise.expressions import Q

import api
from ..geocoder import GeocoderRemoteServiceRequestError, GeocoderRemoteServiceResponseError
from ..router.router import TIMEZONE

from ... import schemas
from ... import models
from ... import enums
from ...common import validators
from ...domain.pan import Pan
from ...enums import ProfileType
from ...modules.city.infrastructure.db_table import City
from ...modules.delivery_point import DeliveryPointRepository
from ...modules.delivery_point.schemas import DeliveryPointCreate
from ...modules.shipment_point import ShipmentPointRepository
from ...reports.queries import get_time_with_timezone, order_report_query_builder
from ...schemas import DeliveryStatus
from ...services.geocoder import service


class ExcelLoaderFieldsError(Exception):
    """Raises when the model fields are not correct."""


class ExportError(Exception):
    """Raises when the export fails."""


# TODO: make a file movement to the folder with excels
class ExcelLoader:
    @staticmethod
    def calculate_column_width(series) -> int:
        return max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
        )) + 1  # adding a little extra space

    def set_columns(self, dataframe: pd.DataFrame, worksheet) -> None:
        for idx, col in enumerate(dataframe):  # loop through all columns
            series = dataframe[col]

            max_len = self.calculate_column_width(series)  # Calculate max length of the column
            worksheet.set_column(idx, idx, max_len)  # set column width

    @staticmethod
    def drop_timezone_from_dt_fields(dt_fields: list, dataframe: pd.DataFrame) -> None:
        """need for drop datetime fields with timezone cuz excel can't handle it"""

        if dt_fields:
            date_columns = dataframe.select_dtypes(include=['datetime64[ns, UTC]']).columns
            for date_column in date_columns:
                dataframe[date_column] = dataframe[date_column].dt.tz_localize(None).dt.strftime(
                    '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def is_profile(field: str) -> bool:
        return field in ['courier', 'manager', 'service_manager']

    @staticmethod
    async def _get_json_fields(
        json_fields: list,
        data: list
    ):
        for record in data:
            for json_field in json_fields:
                json_field_value = record[json_field]

                if json_field_value:
                    record[json_field] = [item if isinstance(item, dict) else item.dict() for item
                                          in json_field_value]

    async def _get_related_fields(
        self,
        rel_fields: list,
        data: list
    ) -> list:
        """need for get related fields from model and add them to dataframe"""
        result = data.copy()
        if rel_fields:
            for idx, item in enumerate(data):
                for rel_field in rel_fields:
                    is_profile = self.is_profile(rel_field)
                    item_field = item.get(rel_field + '_id')

                    if item_field is not None:
                        if is_profile:
                            rel_field = f'Profile{rel_field.capitalize()}'

                        rel_model = getattr(api.models,
                                            rel_field.capitalize() if not is_profile else rel_field)
                        rel_object_query = rel_model.get(id=item_field)

                        if is_profile:
                            rel_object_query = rel_object_query.prefetch_related('user')
                            rel_field = rel_field.lstrip('Profile').lower()

                        rel_object = await rel_object_query
                        new_record = {}

                        for k, v in result[idx].items():
                            if k == rel_field + '_id':
                                new_record[rel_field] = rel_object.__str__()
                            else:
                                new_record[k] = v

                        result[idx] = new_record

        return result

    @staticmethod
    def translate_fields(cols: list, description_cols: dict) -> list:
        for idx, field in enumerate(cols):
            for k, v in description_cols.items():
                if field in v:
                    cols[idx] = k

        return cols

    @staticmethod
    def _prepare_filtering(filtering_dict: dict) -> dict:
        """need for prepare filtering dict"""
        result = {}
        for key, value in filtering_dict.items():
            if value is not None:
                result[key] = value

        return result

    @staticmethod
    def _prepare_periodic_filtering(periodic_filtering_dict: dict) -> dict:
        """need for prepare filtering dict"""
        range_: list = [
            periodic_filtering_dict.get('from'),
            periodic_filtering_dict.get('to')
        ]

        if not all(range_):
            return {}

        for idx, item in enumerate(range_):
            try:
                if item is not None:
                    range_[idx] = datetime.strptime(item, '%Y-%m-%d')
                else:
                    range_[idx] = datetime.now()
            except ValueError:
                raise ExportError(f'Incorrect date format. Use YYYY-MM-DD')

        range_[-1] = range_[-1] + timedelta(days=1)
        return {'created_at__range': range_}

    @staticmethod
    def _translate_cols_to_eng(cols: list, description_cols: dict):
        for idx, field in enumerate(cols):
            for k, v in description_cols.items():
                if field in v:
                    cols[idx] = k

    @staticmethod
    def _hide_hidden_fields(
        data: list,
        hidden_fields: list
    ):
        """need for hide fields from model"""
        if hidden_fields:
            for idx, item in enumerate(data):
                for hidden_field in hidden_fields:
                    data[idx].pop(hidden_field)

    @staticmethod
    async def _get_address(
        address_type: enums.AddressType,
        address
    ):
        try:
            cords = await service.to_coordinates(address)
        except (
            GeocoderRemoteServiceRequestError,
            GeocoderRemoteServiceResponseError,
        ) as e:
            logger.debug(e)
            logger.debug(f'address: {address}')
            logger.debug(f'address-type: {address_type}')
            raise e
        if address_type == enums.AddressType.SHIPMENT_POINT:
            sp_repo = ShipmentPointRepository()
            sp_id = await sp_repo.get_id_by_geolocations(**cords.dict())
            return {
                'place_id': sp_id,
                'position': 0,
                'type': address_type
            }
        dp_repo = DeliveryPointRepository()
        create_schema = DeliveryPointCreate(
            **cords.dict(),
            address=address,
        )
        dp = await dp_repo.create(create_schema)
        return {
            'place_id': dp.id,
            'position': 1,
            'type': address_type,
        }

    async def _parse_points(self, shipment_point: str, delivery_point: str):

        result_addresses = []
        if shipment_point is not None:
            result_addresses.append(
                await self._get_address(
                    address_type=enums.AddressType.SHIPMENT_POINT,
                    address=shipment_point
                )
            )
        result_addresses.append(
            await self._get_address(
                address_type=enums.AddressType.DELIVERY_POINT,
                address=delivery_point
            )
        )

        return result_addresses

    async def get_models_from_excel(
        self,
        model_name: str,
        file: UploadFile,
        current_user: schemas.UserCurrent = None
    ) -> tuple[BytesIO, str]:
        wrong_address = 0
        description_cols, *_ = enums.order_descriptions.values()

        content = await file.read()
        df = await run_in_threadpool(pd.read_excel, content)
        df = await run_in_threadpool(df.replace, {float('nan'): None})
        _, cols, values = (await run_in_threadpool(df.to_dict, orient='split')).values()

        self._translate_cols_to_eng(cols, description_cols)
        item_counter = 0
        error_rows = []
        for item in values:
            item_counter += 1
            data_to_create = dict(zip(cols, item))

            if model_name == 'Order':
                errors = await self.order_from_excel(data_to_create, item_counter, current_user)
                data_to_create['created_by'] = enums.CreatedType.IMPORT
                if errors:
                    item.append(errors)
                    error_rows.append(item)
                else:
                    order = schemas.OrderCreate(**data_to_create)
                    created_order = await models.order_create(
                        create=order,
                        user=current_user,
                        courier_service_id=current_user.partners[0],
                    )
                    address_long = created_order.addresses[0].place.longitude
                    address_lat = created_order.addresses[0].place.latitude
                    order_time = await created_order.localtime
                    created_order.initial_delivery_datetime = order_time + timedelta(hours=2)
                    created_order.delivery_datetime = order_time + timedelta(hours=2)
                    await created_order.save()
                    if address_long is None and address_lat is None:
                        wrong_address += 1

        _, cols, values = df.to_dict(orient='split').values()
        cols.append('Ошибки')

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df = await run_in_threadpool(pd.DataFrame, error_rows, index=None, columns=cols, dtype=None, copy=None)
            await run_in_threadpool(df.to_excel, writer, sheet_name='sheet1', index=False)
            worksheet = writer.sheets['sheet1']
            workbook = writer.book
            cell_format_red = workbook.add_format({'font_color': 'red'})
            start_row, end_row = 1, len(df.axes[0])
            start_col, end_col = len(df.axes[1]) - 1, len(df.axes[1]) - 1

            worksheet.conditional_format(start_row, start_col, end_row, end_col,
                                         {'type': 'text', 'criteria': 'containsText', 'value': ' ',
                                          'format': cell_format_red})

        saved_objects = len(values) - len(error_rows)
        data = {'success': saved_objects, 'fail': len(error_rows), 'total': len(values),
                'wrong_address': wrong_address, 'date': datetime.now(), 'name_file': file.filename}
        history_schema = schemas.HistoryCreate(
            initiator_type=enums.InitiatorType.IMPORT,
            initiator_id=current_user.id,
            initiator_role=current_user.profile['profile_type'],
            request_method=enums.RequestMethods.POST,
            model_type=enums.HistoryModelName.IMPORT_ORDER,
            model_id=current_user.partners[0],
            action_data=data
        )
        await models.history_create(history_schema)
        del data['date'], data['name_file']
        buffer.seek(0)
        return buffer, str(data)

    @staticmethod
    def _get_item_cols(item: dict, cols: list) -> dict:
        result = {}
        if not cols:
            return item

        for col in cols:
            if col in item:
                result.update({col: item[col]})

        return result

    @staticmethod
    def _hide_hidden_cols(
        cols: list,
        hidden_cols: list,
        description_cols: dict
    ) -> list:
        """need for hide cols from model"""
        result = list(cols).copy()

        if hidden_cols:
            for col in hidden_cols:
                col = description_cols.get(col)
                result.remove(col)

        return result

    async def _prepare_cols(
        self,
        cols: list,
        hidden_cols: list,
        description_cols: dict
    ):
        result = self.translate_fields(cols, description_cols)
        result = self._hide_hidden_cols(result, hidden_cols, description_cols)
        return result

    async def order_from_excel(self, data_to_create, item_counter, current_user) -> str | None:
        error_order = None
        shipment_point = data_to_create.pop('shipment_point', None)
        delivery_point = data_to_create.pop('delivery_point', None)

        if not shipment_point:
            shipment_point = None

        receiver_phone_number = data_to_create.get('receiver_phone_number')
        city_name = data_to_create.pop('city')
        country_name = data_to_create.pop('country', None)

        if not city_name:
            return 'Не указан город'
        city_name = city_name.strip()
        try:
            if current_user.profile['profile_type'] == ProfileType.BANK_MANAGER:
                if not country_name:
                    return 'Не указана страна'
                else:
                    country_name = country_name.strip()
                    city_obj = await City.filter(
                        Q(
                            name_en=city_name,
                            name_kk=city_name,
                            name_ru=city_name,
                            name_zh=city_name,
                            join_type=Q.OR,
                        ),
                        Q(
                            country__name_en=country_name,
                            country__name_kk=country_name,
                            country__name_ru=country_name,
                            country__name_zh=country_name,
                            join_type=Q.OR,
                        ),
                    ).first()
            else:
                city_obj = await City.filter(Q(
                            name_en=city_name,
                            name_kk=city_name,
                            name_ru=city_name,
                            name_zh=city_name,
                            join_type=Q.OR,
                        )).first()
            data_to_create['city_id'] = city_obj.id
        except AttributeError as e:
            return 'Город с таким названием не найден'

        data_to_create['distribute_now'] = False
        data_to_create['type'] = enums.OrderType.PLANNED
        if not delivery_point:
            return 'Не указан адрес доставки'

        delivery_datetime = data_to_create.pop('delivery_datetime', None)
        if delivery_datetime:
            try:
                delivery_datetime_str = str(delivery_datetime)[:10] + ' ' + '17:59'
                data_to_create['delivery_datetime'] = datetime.strptime(
                    delivery_datetime_str,
                    '%Y-%m-%d %H:%M').astimezone(TIMEZONE)
                if data_to_create['delivery_datetime'] < datetime.now().astimezone(TIMEZONE):
                    return 'Дата доставки не актуальная'
            except (ValueError, TypeError) as e:
                return 'Неверный формат Дата доставки {}'.format(e)
        if data_to_create['receiver_iin']:
            data_to_create['receiver_iin'] = str(data_to_create['receiver_iin']).strip()
            try:
                if len(str(data_to_create['receiver_iin'])) < 12:
                    data_to_create['receiver_iin'] = str(data_to_create['receiver_iin']).zfill(12)
                elif len(str(data_to_create['receiver_iin'])) > 12:
                    return f'Field number {item_counter}, receiver_iin wrong format'
            except ValueError:
                return 'Неверный формат ИИН получателя'
        else:
            data_to_create['receiver_iin'] = None

        try:
            if not receiver_phone_number:
                return 'Не указан номер телефона получателя'
            data_to_create['receiver_phone_number'] = '+' + str(receiver_phone_number).strip()
            validators.validate_phone(data_to_create['receiver_phone_number'])
            receiver_phone_number = data_to_create['receiver_phone_number']
            if len(receiver_phone_number) > 12:
                return 'Неверный формат номера телефона получателя'
        except ValueError as e:
            return f'Field number {item_counter}, {e}'

        if current_user.profile['profile_type'] == enums.ProfileType.MANAGER:
            data_to_create['partner_id'] = current_user.profile['profile_content']['partner_id']

        try:
            partner_name = data_to_create.pop('partner', '').strip()
            if not partner_name:
                return 'Не указан партнер'
            partner = await models.Partner.filter(name_ru=partner_name).first()
            data_to_create['partner_id'] = partner.id

        except AttributeError:
            return 'Партнер с таким названием не найден'

        if data_to_create.get('partner_id') not in current_user.partners:
            return 'Партнер недоступен'
        try:
            item_name = data_to_create.pop('item', '').strip()
            if not item_name:
                return 'Не указан продукт'
            item_obj = await models.Item.filter(
                name=item_name,
                partner_id=data_to_create['partner_id'],
            ).first()
            data_to_create['item_id'] = item_obj.id
            if item_obj.partner_id not in current_user.partners:
                return 'Продукт с таким названием не найден'
        except AttributeError:
            return 'Продукт с таким названием не найден'
        except KeyError:
            return 'Партнер с таким названием не найден'

        if current_user.profile['profile_type'] == ProfileType.BANK_MANAGER:
            if data_to_create.get('idn') is None:
                return 'Не указан IDN'
            if data_to_create.get('manager') is None:
                return 'Не указан менеджер'
            if not data_to_create.get('receiver_iin'):
                return 'Не указан ИИН получателя'
            if not data_to_create.get('receiver_iin'):
                return 'Не указан ИИН получателя'

        # noinspection PyBroadException
        try:
            if shipment_point:
                shipment_point = shipment_point.replace(';', ',')
                if city_obj.name not in shipment_point:
                    shipment_point += ', ' + city_obj.name
            delivery_point = delivery_point.replace(';', ',')
            if city_obj.name not in delivery_point:
                delivery_point += ', ' + city_obj.name
            data_to_create['addresses'] = await self._parse_points(
                shipment_point,
                delivery_point,
            )
        except Exception as e:
            logger.debug(e)
            return 'Адрес вывоза или Адрес доставки не найден'

        return error_order


async def prepare_orders_for_report(columns: list[str], **kwargs) -> list[list[str]]:
    description_cols, *_ = enums.order_descriptions.values()
    original_columns = ExcelLoader.translate_fields(columns, description_cols)
    start = time.time()
    async with tortoise.transactions.in_transaction('default') as conn:
        count, orders = await conn.execute_query(
            order_report_query_builder(**kwargs)
        )
    fact_delivery_time = kwargs.get('fact_delivery_time__range', None)
    current_status_range = kwargs.get('current_status__created_at__range', None)
    created_at_range = kwargs.get('created_at__range', None)
    timezone_offset = timedelta(seconds=0)
    if fact_delivery_time:
        timezone_offset = fact_delivery_time[0].utcoffset()
    if created_at_range:
        timezone_offset = created_at_range[0].utcoffset()
    if current_status_range:
        timezone_offset = current_status_range[0].utcoffset()
    end = time.time() - start
    loguru.logger.debug("Query: ", end)
    start = time.time()
    result = []
    for order in orders:
        order_data = []
        for column in original_columns:
            if isinstance(order.get(column), datetime):
                order_data.append(get_time_with_timezone(order[column], timezone_offset))
                continue

            if column == 'pan' and order.get(column):
                pan = Pan(value=order[column])
                order_data.append(pan.get_masked())
                continue

            order_data.append(order.get(column, ''))
        result.append(order_data)

    end = time.time() - start
    loguru.logger.debug("Deserialization: ", end)
    return result
