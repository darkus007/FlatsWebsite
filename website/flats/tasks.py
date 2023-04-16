from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db import connection
from django.template.loader import render_to_string

from website.celery import app
from website.settings import DEFAULT_FROM_EMAIL


def dict_fetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@app.task
def task_send_flat_changes() -> None:
    """
    Проверяет изменения по отслеживаемым пользователями квартирам,
    и запускает задачи на отправку писем.
    """
    # внутренний запрос, не имеет влияние извне,
    # поэтому с целью оптимизации написан сырой SQL
    with connection.cursor() as cursor:
        sql = """
            SELECT flat.flat_id, flat.address, flat.floor, flat.rooms, flat.area, flat.finishing,
            flat.settlement_date, flat.url_suffix,
                project.project_id, project.name, project.city, project.url,
                price.price, price.booking_status,
                members_selectedflat.flats_user_id
            FROM flat
            INNER JOIN members_selectedflat ON flat.flat_id = members_selectedflat.flat_id_id
            INNER JOIN project ON flat.project_id = project.project_id
            INNER JOIN price ON price.flat_id = flat.flat_id
            INNER JOIN (
                SELECT flat_id, max(data_created) AS max_data
                FROM price
                GROUP BY flat_id
            ) AS last_price ON last_price.flat_id = price.flat_id
            WHERE price.data_created = last_price.max_data 
            AND last_price.max_data <> members_selectedflat.data_created
            ORDER BY members_selectedflat.flats_user_id;
        """
        cursor.execute(sql)
        user_selected_flats_changed = dict_fetchall(cursor)
        produce_send_emails(group_user_flats(user_selected_flats_changed))


def group_user_flats(changed_flats: list[dict]) -> dict[list[dict]]:
    """
    Группирует квартиры по пользователям.
    :param changed_flats: Список словарей, который содержит квартиры и пользователей.
    :return: Словарь, где ключ - id пользователя, а значение - список квартир.
    """
    users = {}
    first_flat = changed_flats.pop()
    users[first_flat["flats_user_id"]] = [first_flat]
    for flat in changed_flats:
        if users[first_flat["flats_user_id"]][0]["flats_user_id"] == flat["flats_user_id"]:
            users[first_flat["flats_user_id"]].append(flat)
        else:
            if users.get(flat["flats_user_id"]):
                users[flat["flats_user_id"]].append(flat)
            else:
                users[flat["flats_user_id"]] = [flat]
    return users


def produce_send_emails(users: dict[list[dict]]) -> None:
    """
    Проходит по сгруппированным пользователям и ставит задачи на отправку писем.
    :param users: словарь, где ключ - id пользователя, а значение - список квартир.
    :return: None
    """
    for key, value in users.items():
        user = get_user_model().objects.values('username', 'email').get(pk=key)
        context = {'user': user, 'flats': value}
        subject = render_to_string('flats/flats_changed_letter_subject.txt', context)
        body_text = render_to_string('flats/flats_changed_letter_body.txt', context)
        task_send_mail.delay(subject, body_text,
                             from_email=DEFAULT_FROM_EMAIL,
                             recipient_list=[user['email']],
                             fail_silently=True)


@app.task
def task_send_mail(subject: str, message: str, from_email: str = None, **kwargs) -> int:
    """ Отправляет письма пользователям. """
    return send_mail(subject, message, from_email, **kwargs)
