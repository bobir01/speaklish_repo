import dataclasses
import os
from pathlib import Path
from dataclasses import dataclass

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# only development

# load_dotenv(BASE_DIR.parent / 'dev.env')
load_dotenv(BASE_DIR.parent / '.env')

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY', get_random_secret_key())

# IN_TEST = os.environ.get('IN_TEST', True)
IN_TEST = False

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.environ.get('DEBUG', False)
DEBUG = False
ALLOWED_HOSTS = ['localhost','api.speaklish.uz',
                 ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'school_api.apps.SchoolApiConfig',
    'questions.apps.QuestionsConfig',
    'writing_checker.apps.WritingCheckerConfig',
    'paycomuz',

    'payments.apps.PaymentsConfig',

    # 'corsheaders',
    'rest_framework',
    'django_filters',
    'drf_yasg',
    # 'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

# APPEND_SLASH = False

CSRF_TRUSTED_ORIGINS = [
    'https://api.speaklish.uz',
    'http://api.speaklish.uz',
    'http://localhost:8000',
]

CORS_ALLOWED_ORIGINS = [
    'https://api.speaklish.uz',
    'http://api.speaklish.uz',
    'http://localhost:8000',

]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates/']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.csrf',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        "NAME": os.environ.get('POSTGRES_DB', None),
        "USER": os.environ.get('POSTGRES_USER', ),
        "PASSWORD": os.environ.get('POSTGRES_PASSWORD', ),
        "HOST": os.environ.get('POSTGRES_HOST', 'localhost'),
        "PORT": "5432",
    }

}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{os.environ.get('REDIS_URL', 'redis://redis:6379/0')}",
        "KEY_PREFIX": "spklsh_",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

ADMIN_CREDS = {
    'username': os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
    'password': os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin'),
    'email': os.environ.get('DJANGO_ADMIN_EMAIL', '')}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = 'media/'

# openai conf
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

open_ai_config = {
    'open_ai_temp': 0,
    'system_text': ''''''}

OPENAI_TEMP = open_ai_config['open_ai_temp']
SYSTEM_TEXT = open_ai_config['system_text']
OPENAI_MODEL = 'gpt-4o'
TELEGRAM_BOT_TOKEN = os.environ.get('BOT_TOKEN')

groq_parser_conf = {
    'model': 'mixtral-8x7b-32768',
    'system_text': """pass"""
}

GROQ_PARSER_MODEL = groq_parser_conf['model']
GROQ_PARSER_SYSTEM_TEXT = groq_parser_conf['system_text']
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

AZURE_REDIS_HOST = os.environ.get('AZURE_REDIS_HOST')
AZURE_REDIS_PORT = os.environ.get('AZURE_REDIS_PORT')
AZURE_REDIS_PASSWORD = os.environ.get('AZURE_REDIS_PASSWORD')

# celery conf
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "verbose": {
            "format": "[{levelname} {asctime}] modelu:{module}  | {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

PAYCOM_SETTINGS = {
    "KASSA_ID": os.getenv("PAYME_KASSA"),  # token
    "SECRET_KEY": os.getenv("PAYME_SEC"),  # password
    "ACCOUNTS": {
        "KEY": "order_id"
    }
}

AZURE_VOICE_KEY = os.getenv('AZURE_VOICE_KEY')
AZURE_VOICE_REGION = os.getenv('AZURE_VOICE_REGION')

PAYZE_KEY = os.getenv('PAYZE_AUTH_KEY')
PAYZE_SECRET = os.getenv('PAYZE_AUTH_SECRET')
