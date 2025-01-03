import os
import environ
import sentry_sdk

from pathlib import Path
# from firebase_admin import initialize_app, credentials

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))

ALLOWED_HOSTS = ["*"]

SECRET_KEY = env.str("SECRET_KEY", default="Oppa_pro")

DEBUG = env.bool("DEBUG", default=False)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'HOST': env.str('DB_HOST'),
#         'NAME': env.str('POSTGRES_DB'),
#         'USER': env.str('POSTGRES_USER'),
#         'PASSWORD': env.str('POSTGRES_PASSWORD'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS = [
    'jazzmin',
    # 'jet',
    'django_filters',
    'multiselectfield',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',

    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'djoser',
    'adminsortable2',
    'solo',
    "django_celery_beat",
    'fcm_django',

    'user',
    'car',
    'business',
    'info',
    'purchase_request',
    'chat',
    'notification',
    'product',
    'telegram',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'src.wsgi.application'

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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'staticfiles'),
)

BUSINESS_START_BALANCE = 200

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'user.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 30,
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

DJOSER = {
    'SEND_ACTIVATION_EMAIL': False,
    'USER_CREATE_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_RETYPE': True,
    'SERIALIZERS': {
        "token": "user.serializers.UserSignInSerializer",
    },
}

PURCHASE_REQUEST_LIFE_HOURS = 24

FIREBASE_APPLICATION_CREDENTIALS = os.environ.get(
    'FIREBASE_APPLICATION_CREDENTIALS'
)

# firebase_cred = credentials.Certificate(FIREBASE_APPLICATION_CREDENTIALS)
# firebase_app = initialize_app(firebase_cred)
# To learn more, visit the docs here:
# https://cloud.google.com/docs/authentication/getting-started>

FCM_DJANGO_SETTINGS = {
    # an instance of firebase_admin.App to be used as default for all fcm-django requests
    # default: None (the default Firebase app)
    "DEFAULT_FIREBASE_APP": None,
    # default: _('FCM Django')
    "APP_VERBOSE_NAME": "Default",
    # true if you want to have only one active device per registered user at a time
    # default: False
    "ONE_DEVICE_PER_USER": True,
    # devices to which notifications cannot be sent,
    # are deleted upon receiving error response from FCM
    # default: False
    "DELETE_INACTIVE_DEVICES": False,
}



NIKITA_LOGIN = env.str('NIKITA_LOGIN', default='')
NIKITA_PASSWORD = env.str('NIKITA_PASSWORD', default='')
NIKITA_SENDER = env.str('NIKITA_SENDER', default='')
NIKITA_TEST = env.str('NIKITA_TEST', default='1')
NIKITA_URL = env.str('NIKITA_URL', default='')

# Redis and Celery settings
REDIS_HOST = env.str('REDIS_HOST', default='0.0.0.0')
REDIS_PORT = env.str('REDIS_PORT', default='6379')
CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

JAZZMIN_SETTINGS = {
    "site_title": "OPPA",
    "site_header": "OPPA",
    "site_brand": "OPPA",
    "site_logo": "/jazzmin/img/oppa_logo.svg",
    "welcome_sign": "Админпанель OPPA",
    "user_avatar": 'profile_photo',
    "hide_apps": ['django_celery_beat', 'auth'],
}

PAYBOX_SECRET_KEY = env.str("PAYBOX_SECRET_KEY")
PAYBOX_MERCHANT_ID = env.str("PAYBOX_MERCHANT_ID")
PAYBOX_RESULT_URL = env.str("PAYBOX_RESULT_URL")
PAYBOX_TEST_MODE = env.bool("PAYBOX_TEST_MODE", default=True)
PAYBOX_CURRENCY = "KGS"
PAYBOX_PAYMENT_LIFETIME_SEC = env.int("PAYBOX_PAYMENT_LIFETIME_SEC", default=300)
PAYBOX_LANGUAGE = "ru"
SENTRY_DSN = env.url("SENTRY_DSN", default=None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN.geturl(),
        enable_tracing=True,
    )
JET_SIDE_MENU_COMPACT = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
