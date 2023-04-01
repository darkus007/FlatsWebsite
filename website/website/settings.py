"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
from os import getenv, path
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    "debug_toolbar",

    'flats.apps.FlatsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "debug_toolbar.middleware.DebugToolbarMiddleware",

    'flats.middlewares.MiddlewareAllException',
]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'flats.middlewares.projects',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('DB_NAME'),
        'USER': getenv('DB_USER'),
        'PASSWORD': getenv('DB_PASSWORD'),
        'HOST': getenv('DB_HOST'),
        'PORT': getenv('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

INTERNAL_IPS = [
    "127.0.0.1",
]


# настраиваем отправку писем
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # выводит в командной строке
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # отправляет на почтовый сервер
DEFAULT_FROM_EMAIL = 'flats@mail.ru'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
# EMAIL_HOST_USER = 'user'                                         # логин для SMTP-сервера, по умолчанию пустая строка
# EMAIL_HOST_PASSWORD = 'password'                                 # пароль для SMTP-сервера, по умолчанию пустая строка
ADMINS = [  # админы, которым будут отправлены письма методом mail_admins
    ('admin', 'admin@mail.ru'),
]
SERVER_EMAIL = 'flats_from@email.ru'  # адрес почты с которой будут отправлены письма


# настраиваем логирование
LOGGING = {
    'version': 1,
    'disable_existing_logger': True,    # отключаем все регистраторы, используемые по умолчанию

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },

    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',   # формат сообщения
            'datefmt': '%Y.%m.%d %H:%M:%S',                         # формат временной метки
        }
    },

    'handlers': {
        'console_dev': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        'console_prod': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_false'],
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/website.log',
            'maxBytes': 1048576,
            'backupCount': 10,
            'formatter': 'simple',
            'filters': ['require_debug_false'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false']
        }
    },

    'loggers': {
        'django': {                 # собирает сообщения от всех подсистем фреймворка
            'level': 'INFO',
            'handlers': ['console_dev', 'console_prod'],
        },
        'django.server': {          # собирает сообщения от подсистемы обработки запросов и формирования ответов
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': True,
        },
        # 'django.db.backends': {      # собирает сообщения обо всех операциях с базой данных сайта
        #     'handlers': ['console_dev'],
        #     'level': 'DEBUG',       # DEBUG - по умолчанию
        # }

        # добавлен регистратора, который объявлен в файле flats/middleware.py
        # logger = logging.getLogger(__name__), где __name__ = 'flats.middlewares'
        'flats.middlewares': {
            'level': 'WARNING',
            'handlers': ['file', 'console_dev', 'mail_admins'],
            'propagate': False,
        },
    }
}
