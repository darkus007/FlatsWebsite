# FlatsWebsite v.1.1
Сайт по подбору квартир. Часть проекта Flats, в который также входят [FlatsScrapper](https://github.com/darkus007/FlatsScrapper) - сервис по сбору информации с сайтов застройщиков и наполнению базы данных.
FlatsTelegramBot - позволяет получать информацию о квартирах в мессенджере Telegram.

Данный проект написан на Django. Реализован просмотр квартир в виде таблиц, с сортировкой по жилым комплексам. \
На сайте можно зарегистрироваться и после подтверждения e-mail получать на почту уведомления об изменении цены или статуса 
по выбранным квартирам. \
Настроено логирование и кэширование, отправка писем администратору об ошибках на сайте, оптимизированы ORM запросы, 
написан фильтр и middlewares для пополнения контекста шаблона и обработки исключений. \
Письма отправляются с использованием [Celery](https://docs.celeryq.dev/en/stable/). \
Весь функционал сайта также доступен через REST API, которое разработано с применением [Django REST framework](https://www.django-rest-framework.org).

Написан `docker-compose.yml` который упаковывает и запускает приложение в контейнере используя [Nginx](https://nginx.org/ru/) + [Gunicorn](https://gunicorn.org/).

При разработке приложения использованы следующие основные пакеты, фреймворки и технологии: \
[Django](https://pypi.org/project/Django/); \
[Django REST framework](https://www.django-rest-framework.org); \
[Celery](https://docs.celeryq.dev/en/stable/); \
[Django Simple Captcha](https://pypi.org/project/django-simple-captcha/); \
[Django Debug Toolbar](https://pypi.org/project/django-debug-toolbar/); \
[Bootstrap](https://bootstrap-4.ru/); \
[Docker](https://www.docker.com/).

Полный список в фале `requirements.txt`.

Базы данных [PostgreSQL](https://www.postgresql.org/) и [Redis](https://redis.io/) в качестве брокера сообщений для Celery.

### Описание Models приложения flats
> Projects - таблица с информацией о жилых комплексах.
>> project_id - уникальный идентификатор, совпадает с id застройщика.\
>> city - город.\
>> name - название ЖК.\
>> url - URL адрес ЖК на сайте застройщика.\
>> metro - ближайшее метро.\
>> time_to_metro - расстояние пешком до метро.\
>> latitude - координаты ЖК, широта.\
>> longitude - координаты ЖК, долгота.\
>> address - адрес ЖК.\
>> data_created - дата добавления ЖК в базу данных.\
>> data_closed - дата снятия ЖК с продажи.

> Flats - таблица с информацией о Квартирах.
>> flat_id - уникальный идентификатор, совпадает с id застройщика.\
>> address - адрес квартиры.\
>> floor - этаж.\
>> rooms - количество комнат.\
>> area - площадь.\
>> finishing - с отделкой?.\
>> settlement_date - дата заселения.\
>> url_suffix - продолжение URL к адресу ЖК.\
>> data_created - дата добавления квартиры в базу данных.\
>> data_closed - дата снятия квартиры с продажи.
>> project - проект к которому принадлежит квартира, связь один со многими.

> Prices - таблица с информацией о ценах на Квартиру.
>> price_id - уникальный идентификатор, \
>> benefit_name - ценовое предложение.\
>> benefit_description - описание ценового предложения.\
>> price - цена.\
>> meter_price - цена за метр.\
>> booking_status - статус бронирования.\
>> data_created - дата добавления записи в базу данных.\
>> flat - проект к которому принадлежит квартира, связь один со многими.

На уровне базы данных таблица AllFlatsLastPrice реализована в виде представления (VIEW).
Возвращает последнюю запись по квартире (последнее изменение по цене или статусу квартиры).
> AllFlatsLastPrice - таблица с информацией о ценах на Квартиру.
>> flat_id - уникальный идентификатор, совпадает с id застройщика.\
>> address - адрес квартиры.\
>> floor - этаж.\
>> rooms - количество комнат.\
>> area - площадь.\
>> finishing - с отделкой?.\
>> settlement_date - дата заселения.\
>> url_suffix - продолжение URL к адресу ЖК.\
>> project_id - уникальный идентификатор, совпадает с id застройщика.\
>> city - город.\
>> name - название ЖК.\
>> url - URL адрес ЖК на сайте застройщика.\
>> price - цена.\
>> booking_status - статус бронирования.

SQL для создания таблицы AllFlatsLastPrice:
```
CREATE VIEW all_flats_last_price AS
SELECT flats.flat_id, flats.address, flats.floor, flats.rooms, flats.area, flats.finishing, flats.settlement_date, flats.url_suffix,
	projects.project_id, projects.name, projects.city, projects.url,
	prices.price, prices.booking_status
FROM flats
INNER JOIN projects ON flats.project_id = projects.project_id
INNER JOIN prices ON prices.flat_id = flats.flat_id
INNER JOIN (
	SELECT flat_id, max(data_created) AS max_data
	FROM prices
	GROUP BY flat_id
) AS last_price ON last_price.flat_id = prices.flat_id
WHERE prices.data_created = last_price.max_data;
```


## Установка и запуск
Приложение написано на [Python v.3.11](https://www.python.org). \
Скачайте FlatsWebsite на Ваше устройство любым удобным способом (например Code -> Download ZIP, распакуйте архив 
или выполните `git clone https://github.com/darkus007/FlatsWebsite.git`). \
Установите [Docker](https://www.docker.com/), если он у Вас еще не установлен.

### Настройка приложения

Откройте файл `.env` и измените значения переменных окружения на свои: \
`SECRET_KEY` - секретный ключ Django; \
`DJANGO_SUPERUSER_PASSWORD` - пароль супер пользователя; \
`DJANGO_SUPERUSER_EMAIL` - email супер пользователя; \
`DJANGO_SUPERUSER_USERNAME` - login супер пользователя; \
`POSTGRES_DB` - название базы данных (совпадает с `POSTGRES_DB` файла `docker-compose.yml`); \
`POSTGRES_USER` - пользователь базы данных (совпадает с `POSTGRES_USER` файла `docker-compose.yml`); \
`POSTGRES_PASSWORD` - пароль пользователя базы данных (совпадает с `POSTGRES_PASSWORD` файла `docker-compose.yml`); \
`DEFAULT_FROM_EMAIL` - адрес отправителя по умолчанию (от кого придет письмо пользователю). \
Настройки почты, зависят от Вашего провайдера, эти настройки Вы можете получить у него: \
`EMAIL_HOST` - хост; \
`EMAIL_PORT` - порт; \
`EMAIL_HOST_USER` - пользователь; \
`EMAIL_HOST_PASSWORD` - пароль.

!!! Приложение запустится без корректировки и изменения указанных в данном разделе настроек, для теста можно их оставить без изменений !!!

#### Запуск в контейнере Docker
Откройте терминал, перейдите в каталог с приложением (`cd <путь к приложению>/FlatsWebsite`). \
Выполните команду `docker-compose up -d --build`. Дождитесь сборки и запуска контейнеров. \
Выполните скрипт `. ./create_sql_view.bash` он создаст представление `all_flats_last_price` в контейнере, необходимое для работы приложения.
(При необходимости дайте скрипту права на запуск выполнив `sudo chmod +x create_sql_view.bash`).
Откройте любимый Веб-браузер и перейдите по адресу http://127.0.0.1/
