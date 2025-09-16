import pytest
from api import models


@pytest.fixture(scope="module")
async def courier_partner(initialize_tests) -> models.Partner:
    return await models.Partner.create(**{
        "id": 1,
        "name_kk": "\"IT Solutions Center\" (АйТи Солюшинс Центр) ЖШС",
        "name_ru": "ТОО \"IT Solutions Center\" (АйТи Солюшинс Центр)",
        "name_en": "OCN \"IT Solutions Center\"",
        "activity_name_ru": "Деятельность сберегательных банков",
        "address": "город Алматы, Алмалинский район, Проспект АБЫЛАЙ ХАНА, дом: 91",
        "affiliated": True,
        "article": "ОB",
        "identifier": "030740001404",
        "is_commerce": True,
        "leader_data": {"iin": "721107450542", "last_name": "ИБРАГИМОВА",
                        "first_name": "ЛЯЗЗАТ", "middle_name": "ЕРКЕНОВНА"},
        "consent_confirmed": True,
        "is_government": True,
        "is_international": True,
        "email": "email@gmail.com",
        "registration_date": "2003-07-10 00:00:00.000000",
        "liq_date": "2003-07-10 00:00:00.000000",
        "liq_decision_date": "2003-07-10 00:00:00.000000",
        "courier_partner_id": None,
        "created_at": "2022-09-21 11:10:54.873492",
        "start_work_hour": "10:00",
        "end_work_hour": "19:00",
        "type": "too"
    })


@pytest.fixture(scope="module")
async def partner(initialize_tests, courier_partner: models.Partner) -> models.Partner:
    return await models.Partner.create(**{
        "id": 2,
        "name_kk": "\"Отбасы банк\" АҚ",
        "name_ru": "АО \"Отбасы банк\"",
        "name_en": None,
        "activity_name_ru": "Деятельность сберегательных банков",
        "address": "город Алматы, Алмалинский район, Проспект АБЫЛАЙ ХАНА, дом: 91",
        "affiliated": True,
        "article": "ОB",
        "identifier": "030740001404",
        "is_commerce": True,
        "leader_data": {"iin": "721107450542", "last_name": "ИБРАГИМОВА",
                        "first_name": "ЛЯЗЗАТ", "middle_name": "ЕРКЕНОВНА"},
        "consent_confirmed": True,
        "is_government": True,
        "is_international": True,
        "email": "email@gmail.com",
        "registration_date": "2003-07-10 00:00:00.000000",
        "liq_date": "2003-07-10 00:00:00.000000",
        "liq_decision_date": "2003-07-10 00:00:00.000000",
        "courier_partner_id": courier_partner.id,
        "created_at": "2022-09-21 11:10:54.873492",
        "start_work_hour": "10:00",
        "end_work_hour": "19:00",
        "type": "too"
    })
