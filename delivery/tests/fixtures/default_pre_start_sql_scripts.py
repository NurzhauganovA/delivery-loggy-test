import os

import pytest

from tests.utils import get_sql_script_from_fixtures


def default_permissions_insert_script() -> str:
    return """
        INSERT INTO public.permissions (slug, name) VALUES ('a:c', 'Создание зоны доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('a:d', 'Удаление зоны доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('a:g', 'Детальный просмотр зоны доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('a:l', 'Просмотр зон доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('a:u', 'Изменение зоны доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('c:c', 'Добавление города');
        INSERT INTO public.permissions (slug, name) VALUES ('c:d', 'Удаление города');
        INSERT INTO public.permissions (slug, name) VALUES ('c:g', 'Детальный просмотр города');
        INSERT INTO public.permissions (slug, name) VALUES ('c:l', 'Просмотр городов');
        INSERT INTO public.permissions (slug, name) VALUES ('c:u', 'Изменение города');
        INSERT INTO public.permissions (slug, name) VALUES ('cu:c', 'Добавление курьера');
        INSERT INTO public.permissions (slug, name) VALUES ('cu:d', 'Удаление курьера');
        INSERT INTO public.permissions (slug, name) VALUES ('cu:g', 'Детальный просмотр курьера');
        INSERT INTO public.permissions (slug, name) VALUES ('cu:l', 'Просмотр курьеров');
        INSERT INTO public.permissions (slug, name) VALUES ('cu:u', 'Изменение курьера');
        INSERT INTO public.permissions (slug, name) VALUES ('dg:c', 'Создание путь доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('dg:d', 'Удаление путь доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('dg:dl', 'Просмотр путь доставки поумолчанию');
        INSERT INTO public.permissions (slug, name) VALUES ('dg:g', 'Детальный просмотр путь доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('dg:l', 'Просмотр путей достовки');
        INSERT INTO public.permissions (slug, name) VALUES ('dg:u', 'Изменение путь доставки');
        INSERT INTO public.permissions (slug, name) VALUES ('g:c', 'Добавление группу');
        INSERT INTO public.permissions (slug, name) VALUES ('g:d', 'Удаление группы');
        INSERT INTO public.permissions (slug, name) VALUES ('g:g', 'Детальный просмотр группы');
        INSERT INTO public.permissions (slug, name) VALUES ('g:l', 'Просмотр групп');
        INSERT INTO public.permissions (slug, name) VALUES ('g:u', 'Изменение группы');
        INSERT INTO public.permissions (slug, name) VALUES ('g:ua', 'Добавить пользователя в группу');
        INSERT INTO public.permissions (slug, name) VALUES ('g:ur', 'Убрать пользователя из группы');
        INSERT INTO public.permissions (slug, name) VALUES ('i:c', 'Добавление продукта');
        INSERT INTO public.permissions (slug, name) VALUES ('i:d', 'Удаление продукта');
        INSERT INTO public.permissions (slug, name) VALUES ('i:g', 'Детальный просмотр продукта');
        INSERT INTO public.permissions (slug, name) VALUES ('i:l', 'Просмотр продуктов');
        INSERT INTO public.permissions (slug, name) VALUES ('i:md', 'Массовое удаление продукта');
        INSERT INTO public.permissions (slug, name) VALUES ('i:u', 'Изменение продукта');
        INSERT INTO public.permissions (slug, name) VALUES ('o:c', 'Добавление заявки');
        INSERT INTO public.permissions (slug, name) VALUES ('o:d', 'Удаление заявки');
        INSERT INTO public.permissions (slug, name) VALUES ('o:e', 'Импорт/Экспорт заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('o:g', 'Детальный просмотр заявки');
        INSERT INTO public.permissions (slug, name) VALUES ('o:l', 'Просмотр заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('o:mc', 'Массовое добавление заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('o:sa', 'Изменение статуса заявки');
        INSERT INTO public.permissions (slug, name) VALUES ('o:sms', 'SMS послед контроль');
        INSERT INTO public.permissions (slug, name) VALUES ('o:u', 'Изменение заявки');
        INSERT INTO public.permissions (slug, name) VALUES ('o:r', 'Получить отчет о заявках');
        INSERT INTO public.permissions (slug, name) VALUES ('o:dist', 'Распределение заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('oc:c', 'Создание комментария заявке');
        INSERT INTO public.permissions (slug, name) VALUES ('oci:c', 'Прикрепление фотографии к комментарии');
        INSERT INTO public.permissions (slug, name) VALUES ('p:c', 'Добавление партнера');
        INSERT INTO public.permissions (slug, name) VALUES ('pc:g', 'Детальный просмотр последконтроля');
        INSERT INTO public.permissions (slug, name) VALUES ('pc:u', 'Изменение последконтроля');
        INSERT INTO public.permissions (slug, name) VALUES ('p:d', 'Удаление партнера');
        INSERT INTO public.permissions (slug, name) VALUES ('pf:c', 'Создание профиля');
        INSERT INTO public.permissions (slug, name) VALUES ('pf:d', 'Удаление профиля');
        INSERT INTO public.permissions (slug, name) VALUES ('pf:l', 'Просмотр профилей');
        INSERT INTO public.permissions (slug, name) VALUES ('pf:u', 'Изменение профиля');
        INSERT INTO public.permissions (slug, name) VALUES ('p:g', 'Детальный просмотр партнера');
        INSERT INTO public.permissions (slug, name) VALUES ('p:l', 'Просмотр партнеров');
        INSERT INTO public.permissions (slug, name) VALUES ('pm:g', 'Детальный просмотр доступа');
        INSERT INTO public.permissions (slug, name) VALUES ('pm:ga', 'Присвоить доступ группе');
        INSERT INTO public.permissions (slug, name) VALUES ('pm:gr', 'Убрать доступ от группы');
        INSERT INTO public.permissions (slug, name) VALUES ('pm:l', 'Просмотр доступов');
        INSERT INTO public.permissions (slug, name) VALUES ('pm:ua', 'Присвоить доступ пользователю');
        INSERT INTO public.permissions (slug, name) VALUES ('pm:ur', 'Убрать доступ от пользователя');
        INSERT INTO public.permissions (slug, name) VALUES ('p:u', 'Изменение партнера');
        INSERT INTO public.permissions (slug, name) VALUES ('sp:c', 'Добавление точки вывоза');
        INSERT INTO public.permissions (slug, name) VALUES ('sp:d', 'Удаление точки вывоза');
        INSERT INTO public.permissions (slug, name) VALUES ('sp:g', 'Детальный просмотр точки вывоза');
        INSERT INTO public.permissions (slug, name) VALUES ('sp:l', 'Просмотр точек вывоза');
        INSERT INTO public.permissions (slug, name) VALUES ('sp:u', 'Изменение точки вывоза');
        INSERT INTO public.permissions (slug, name) VALUES ('fr:c', 'Создание причин обратной связи');
        INSERT INTO public.permissions (slug, name) VALUES ('fr:u', 'Изменение причин обратной связи');
        INSERT INTO public.permissions (slug, name) VALUES ('fr:d', 'Удаление причин обратной связи');
        INSERT INTO public.permissions (slug, name) VALUES ('f:cm', 'Создание обратной связи со стороны партнера');
        INSERT INTO public.permissions (slug, name) VALUES ('f:d', 'Удаление обратной связи');
        INSERT INTO public.permissions (slug, name) VALUES ('f:l', 'Просмотр обратной связи');
        INSERT INTO public.permissions (slug, name) VALUES ('f:g', 'Детальный просмотр обратной связи');
        INSERT INTO public.permissions (slug, name) VALUES ('f:u', 'Изменение обратной связи');
        INSERT INTO public.permissions (slug, name) VALUES ('ca:c', 'Создать категорию');
        INSERT INTO public.permissions (slug, name) VALUES ('ca:l', 'Просмотр категорий');
        INSERT INTO public.permissions (slug, name) VALUES ('ca:g', 'Детальный просмотр категорий');
        INSERT INTO public.permissions (slug, name) VALUES ('o:cc', 'Отмена заявки с выездом');
        INSERT INTO public.permissions (slug, name) VALUES ('pf:ew', 'Курьер: завершить работу');
        INSERT INTO public.permissions (slug, name) VALUES ('pf:sw', 'Курьер: начать работу');
        INSERT INTO public.permissions (slug, name) VALUES ('gp:p', 'Отправка текущей геопозиции');
        INSERT INTO public.permissions (slug, name) VALUES ('o:cs', 'Массовое смена статуса заявки');
        INSERT INTO public.permissions (slug, name) VALUES ('og:c', 'Создание группы заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('og:l', 'Просмотр групп заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('og:u', 'Изменение групп заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('og:d', 'Удаление групп заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('ogo:c', 'Добавление заявки к группе заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('ogo:d', 'Удаление заявки из группы заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('ogs:s', 'Изменение стауса группы заявок');
        INSERT INTO public.permissions (slug, name) VALUES ('s:g', 'Просмотр статистику');
        INSERT INTO public.permissions (slug, name) VALUES ('o:lc', 'Просмотр заявок курьером');
        INSERT INTO public.permissions (slug, name) VALUES ('o:p', 'Передача PAN заявки');
        INSERT INTO public.permissions (slug, name) VALUES ('op:g', 'Получение продукта у заявки');
    """


def default_groups_insert_script() -> str:
    return """
        INSERT INTO public.groups (slug, name) VALUES ('courier', 'Курьер');
        INSERT INTO public.groups (slug, name) VALUES ('manager', 'Менеджер партнера');
        INSERT INTO public.groups (slug, name) VALUES ('branch_manager', 'Менеджер филиала');
        INSERT INTO public.groups (slug, name) VALUES ('dispatcher', 'Диспетчер');
        INSERT INTO public.groups (slug, name) VALUES ('owner', 'Владелец');
        INSERT INTO public.groups (slug, name) VALUES ('service_manager', 'Менеджер');
        INSERT INTO public.groups (slug, name) VALUES ('partner_branch_manager', 'Менеджер филиала партнера');
        INSERT INTO public.groups (slug, name) VALUES ('sorter', 'Сортировщик');
        INSERT INTO public.groups (slug, name) VALUES ('supervisor', 'Супервайзер');
        INSERT INTO public.groups (slug, name) VALUES ('logist', 'Логист');
        INSERT INTO public.groups (slug, name) VALUES ('call_center_manager', 'Менеджер колл-центра');
        INSERT INTO public.groups (slug, name) VALUES ('general_call_center_manager', 'Менеджер колл-центра (расширенный)');
        INSERT INTO public.groups (slug, name) VALUES ('support', 'Поддержка');
    """

def default_groups_permissions_insert_script() -> str:
    return """
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'a:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'a:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'a:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'a:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'c:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'cu:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'cu:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'cu:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'cu:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'cu:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'dg:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'dg:dl');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'dg:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'dg:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'i:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'i:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'i:md');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'i:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:mc');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:sa');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:r');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:dist');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'oc:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'oci:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'p:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'p:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'pf:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'pf:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'pf:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'pf:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'p:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'sp:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'sp:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'sp:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'sp:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'sp:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'fr:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'fr:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'fr:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'f:cm');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'f:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'f:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'f:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'ca:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'ca:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'ca:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:cs');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'og:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'og:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'og:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'ogo:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'ogo:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'ogs:s');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 's:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('service_manager', 'o:p');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('partner_branch_manager', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('partner_branch_manager', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('partner_branch_manager', 'o:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('partner_branch_manager', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('partner_branch_manager', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('partner_branch_manager', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('partner_branch_manager', 'o:p');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:sa');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:sms');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:cc');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'oc:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'oci:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'pf:ew');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'pf:sw');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'gp:p');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'og:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'op:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'o:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'o:e');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'o:mc');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('dispatcher', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'dg:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'dg:dl');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'dg:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'dg:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'o:e');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'o:sa');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'f:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'f:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('owner', 'f:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'a:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'a:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'a:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'a:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'c:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'i:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'i:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'i:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'o:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'o:r');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'pf:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'pf:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'sp:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'sp:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'f:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('branch_manager', 'f:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:e');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:mc');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:r');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'f:cm');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('manager', 'o:p');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'ogs:s');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 's:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:lc');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('courier', 'o:p');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'o:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'o:r');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'o:cs');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'og:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'og:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'og:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'ogo:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'ogo:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('sorter', 'ogs:s');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'a:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'a:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'a:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'a:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'c:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'cu:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'cu:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'cu:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'cu:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'cu:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'dg:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'dg:dl');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'dg:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'dg:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'i:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'i:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'i:md');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'i:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:mc');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:sa');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:r');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:dist');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'oc:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'oci:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'p:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'p:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'pf:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'pf:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'pf:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'pf:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'p:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'sp:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'sp:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'sp:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'sp:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'sp:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'fr:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'fr:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'fr:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'f:cm');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'f:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'f:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'f:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'ca:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'ca:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'ca:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:cs');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'og:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'og:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'og:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'ogo:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'ogo:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'ogs:s');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 's:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('supervisor', 'o:p');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'a:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'c:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'cu:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'cu:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'cu:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'cu:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'cu:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'dg:dl');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'dg:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'dg:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:mc');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:sa');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:r');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'pc:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'pf:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'pf:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'pf:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'pf:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'p:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'sp:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'sp:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'sp:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'sp:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'sp:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'ca:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'ca:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:cs');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'og:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'og:u');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'og:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'ogo:c');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'ogo:d');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'ogs:s');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 's:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('logist', 'o:p');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'a:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'c:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'cu:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'cu:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'dg:dl');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'dg:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'dg:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'pf:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'sp:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'sp:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'ca:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'ca:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('call_center_manager', 's:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'a:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'c:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'cu:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'cu:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'dg:dl');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'dg:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'dg:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'pf:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'sp:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'sp:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'ca:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'ca:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('general_call_center_manager', 's:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'a:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'a:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'c:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'c:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'cu:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'cu:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'dg:dl');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'dg:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'dg:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'i:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'i:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'o:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'o:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'pf:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'p:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'p:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'sp:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'sp:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'ca:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'ca:g');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 'og:l');
        INSERT INTO public.groups_permissions (groups_id, permission_id) VALUES ('support', 's:g');
    """


def statuses_insert_script() -> str:
    return """
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (8, 'sent-for-preparation', true, '[{"id": 1, "name": "Новая заявка"}, {"id": 2, "name": "Курьер назначен"}]', null, 'otpravleno-na-podgotovku');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (9, 'prepare-to-send', true, '[{"id": 8, "name": "Отправлено на подготовку"}]', null, 'podogotovka-k-otpravku');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (11, 'at-the-call-point', true, '[{"id": 15, "name": "В пути к точке вывоза"}]', null, 'na-tochke-vyvoza');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (22, 'ready-to-send', true, '[{"id": 2, "name": "Курьер назначен"}]', null, 'gotovo-u-partnera');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (3, 'courier_accepted', false, '[{"id": 2, "name": "Курьер назначен"}, {"id": 9, "name": "Подготовка к отправке"}]', null, 'priniato-kurerom-v-rabotu');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (15, 'otw_delivery_point', true, '[{"id": 3, "name": "Принято курьером в работу"}]', null, 'v-puti-k-tochke-vyvoza');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (13, 'reassignment', true, '[{"id": 2, "name": "Курьер назначен"}, {"id": 3, "name": "Принято курьером в работу"}, {"id": 4, "name": "В пути к точке доставки"}, {"id": 5, "name": "На точке доставки"}]', null, 'perenaznachenie');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (18, 'post_control', true, '[{"id": 17, "name": "Видеоидентификация"}]', null, 'videoidentifikatsiia-proidena');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (4, 'otw_delivery_point', false, '[{"id": 3, "name": "Принято курьером в работу"}, {"id": 11, "name": "На точке вывоза"}]', null, 'v-puti-k-tochke-dostavki');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (1, 'order_new', false, '[]', null, 'novaia-zaiavka');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (2, 'courier_appointed', false, '[{"id": 1, "name": "Новая заявка"}]', null, 'kurer-naznachen');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (5, 'on_delivery_point', false, '[{"id": 4, "name": "В пути к точке доставки"}]', null, 'na-tochke-dostavki');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (6, 'at_client', false, '[{"id": 5, "name": "На точке доставки"}]', null, 'kontakt-s-poluchatelem');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (10, 'ready-to-send', true, '[{"id": 9, "name": "Подготовка к отправке"}]', null, 'gotovo-k-otpravke');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (24, 'post_control', true, '[{"id": 20, "name": "Код отправлен"}]', null, 'skanirovanie-karty');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (25, 'at_client', true, '[{"id": 3, "name": "Принято курьером в работу"}]', null, 'u-klienta');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (20, 'post_control', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 25, "name": "У клиента"}]', null, 'kod-otpravlen');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (7, 'order_delivevred', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 12, "name": "Последконтроль"}, {"id": 17, "name": "Видеоидентификация"}, {"id": 18, "name": "Видеоидентификация пройдена"}, {"id": 20, "name": "Отправка SMS"}]', null, 'dostavleno');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (17, 'post_control', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 20, "name": "Отправка SMS"}]', null, 'videoidentifikatsiia');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (23, 'ready-to-send', false, '[]', null, 'gotovo-k-vyvozu');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (16, 'post_control', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 24, "name": "Сканирование карты"}]', null, 'fotografirovanie');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (12, 'post_control', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 16, "name": "Фотографирование"}]', null, 'posledkontrol');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (26, 'post_control', true, '[{"id": 20, "name": "Отправка SMS"}]', null, 'priviazka-karty-k-klientu');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (27, 'vydano', true, '[{"id": 16, "name": "Фотографирование"}]', null, 'order_delivevred');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (28, 'courier_accepted', true, '[]', null, 'vyvezeno-kurerom');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (29, 'at-the-call-point', true, '[]', null, 'priniato-kurerskoi-sluzhboi');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (31, 'ready-to-send', true, '[]', null, 'vkliucheno-v-gruppu');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (32, 'at_client', true, '[]', null, 'na-sverke');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug) VALUES (30, 'packed', true, '[]', null, 'upakovano');
    """


def statuses_insert_script_v2() -> str:
    return """
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (32, 'at_client', true, '[]', null, 'na-sverke', 'On reconciliation', null, 'На сверке', 'На сверке', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (2, 'courier_appointed', false, '[{"id": 1, "name": "Новая заявка"}]', null, 'kurer-naznachen', 'Courier assigned', null, 'Курьер назначен', 'Курьер назначен', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (4, 'otw_delivery_point', false, '[{"id": 3, "name": "Принято курьером в работу"}, {"id": 11, "name": "На точке вывоза"}]', null, 'v-puti-k-tochke-dostavki', 'On the way to the delivery point', null, 'В пути к точке доставки', 'В пути к точке доставки', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (5, 'on_delivery_point', false, '[{"id": 4, "name": "В пути к точке доставки"}]', null, 'na-tochke-dostavki', 'At the delivery point', null, 'На точке доставки', 'На точке доставки', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (6, 'at_client', false, '[{"id": 5, "name": "На точке доставки"}]', null, 'kontakt-s-poluchatelem', 'Contact with the recipient', null, 'Контакт с получателем', 'Контакт с получателем', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (10, 'ready-to-send', true, '[{"id": 9, "name": "Подготовка к отправке"}]', null, 'gotovo-k-otpravke', 'Ready for shipment', null, 'Готово к отправке', 'Готово к отправке', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (7, 'order_delivevred', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 12, "name": "Последконтроль"}, {"id": 17, "name": "Видеоидентификация"}, {"id": 18, "name": "Видеоидентификация пройдена"}, {"id": 20, "name": "Отправка SMS"}]', null, 'dostavleno', 'Delivered', null, 'Доставлено', 'Доставлено', 'delivered');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (12, 'post_control', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 16, "name": "Фотографирование"}]', null, 'posledkontrol', 'Post-control', null, 'Последконтроль', 'Последконтроль', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (13, 'reassignment', true, '[{"id": 2, "name": "Курьер назначен"}, {"id": 3, "name": "Принято курьером в работу"}, {"id": 4, "name": "В пути к точке доставки"}, {"id": 5, "name": "На точке доставки"}]', null, 'perenaznachenie', 'Rescheduling', null, 'Переназначение', 'Переназначение', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (16, 'post_control', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 24, "name": "Сканирование карты"}]', null, 'fotografirovanie', 'Photographing', null, 'Фотографирование', 'Фотографирование', 'photo_capturing');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (17, 'post_control', true, '[{"id": 6, "name": "Контакт с получателем"}, {"id": 20, "name": "Отправка SMS"}]', null, 'videoidentifikatsiia', 'Video identification', null, 'Видеоидентификация', 'Видеоидентификация', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (18, 'post_control', true, '[{"id": 17, "name": "Видеоидентификация"}]', null, 'videoidentifikatsiia-proidena', 'Video identification passed', null, 'Видеоидентификация пройдена', 'Видеоидентификация пройдена', 'verify_otp');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (23, 'ready-to-send', true, '[]', null, 'gotovo-k-vyvozu', 'Ready for pickup', null, 'Готово к вывозу', 'Готово к вывозу', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (24, 'post_control', true, '[{"id": 20, "name": "Код отправлен"}]', null, 'skanirovanie-karty', 'Card scanning', null, 'Сканирование карты', 'Сканирование карты', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (25, 'at_client', true, '[{"id": 3, "name": "Принято курьером в работу"}]', null, 'u-klienta', 'At client', null, 'У клиента', 'У клиента', 'send_otp');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (26, 'post_control', true, '[{"id": 20, "name": "Отправка SMS"}]', null, 'priviazka-karty-k-klientu', 'Card linked to client', null, 'Привязка карты к клиенту', 'Привязка карты к клиенту', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (28, 'courier_accepted', true, '[]', null, 'vyvezeno-kurerom', 'Taken by courier', null, 'Вывезено курьером', 'Вывезено курьером', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (29, 'at-the-call-point', true, '[]', null, 'priniato-kurerskoi-sluzhboi', 'Accepted by courier service', null, 'Принято курьерской службой', 'Принято курьерской службой', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (30, 'packed', true, '[]', null, 'upakovano', 'Packed', null, 'Упаковано', 'Упаковано', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (31, 'ready-to-send', true, '[]', null, 'vkliucheno-v-gruppu', 'Included in group', null, 'Включено в группу', 'Включено в группу', null);
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (3, 'courier_accepted', true, '[]', null, 'vyvezeno-kurerom', 'Taken by courier', null, 'Вывезено курьером', 'Вывезено курьером', 'courier_accepted');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (36, 'pos_terminal_registration', false, null, null, 'vvod-seriynogo-nomera-i-modeli', 'Enter serial number and model', null, 'Ввод серийного номера и модели', 'Ввод серийного номера и модели', 'pos_terminal_registration');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (1, 'order_new', false, '[]', null, 'novaia-zaiavka', 'New order', null, 'Новая заявка', 'Новая заявка', 'new');
        INSERT INTO public.status (id, icon, is_optional, after, partner_id, slug, name_en, name_zh, name_ru, name_kk, code) VALUES (35, 'card_returned_to_bank', false, null, null, 'card-returned-to-bank', 'Card was returned to bank', null, 'Карта возвращена в банк', 'Карта возвращена в банк', 'card_returned_to_bank');
    """


def default_countries_insert_script() -> str:
    return """ 
        INSERT INTO public.country (id, name_ru, name_en, name_zh, name_kk) VALUES (2, 'Россия', 'Russia', null, 'Ресей');
        INSERT INTO public.country (id, name_ru, name_en, name_zh, name_kk) VALUES (1, 'Казахстан', 'Kazakhstan', null, 'Казахстан');

    """


def default_cities_insert_script() -> str:
    return """
        INSERT INTO public.city (id, longitude, latitude, timezone, country_id, name_en, name_zh, name_ru, name_kk) VALUES (1, null, null, 'Asia/Aqtau', 1, 'Almaty', null, 'Алматы', 'Алматы');
        INSERT INTO public.city (id, longitude, latitude, timezone, country_id, name_en, name_zh, name_ru, name_kk) VALUES (2, null, null, 'Asia/Aqtau', 1, 'Astana', null, 'Астана', 'Астана');
        INSERT INTO public.city (id, longitude, latitude, timezone, country_id, name_en, name_zh, name_ru, name_kk) VALUES (3, null, null, 'Asia/Aqtau', 1, 'Qaraganda', null, 'Караганда', 'Караганда');
        INSERT INTO public.city (id, longitude, latitude, timezone, country_id, name_en, name_zh, name_ru, name_kk) VALUES (4, null, null, 'Europe/Moscow', 2, 'Moscow', null, 'Москва', 'Москва');
    """


@pytest.fixture
def default_pre_start_sql_script(request) -> str:
    """
        Returns:
            INSERT SQL скрипт с созданием записей в таблицах, находящихся в tables_and_fixtures
    """
    tables_and_fixtures = {
        'public."country"': 'country',
        'public."city"': 'city',
        'public."permissions"': 'permissions',
        'public."groups"': 'groups',
        'public."groups_permissions"': 'groups_permissions',
        'public."status"': 'status',
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))

    scripts = get_sql_script_from_fixtures(
        current_dir=script_dir,
        fixtures=tables_and_fixtures,
    )

    return scripts
