import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import dj_database_url
import dj_email_url
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(os.getenv('ENV_FILE', 'env')))

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = os.getenv('DEBUG') in ['true', 'y', 't']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

"""
SOCKS5 Configuration
  - used by the screenshot worker, generally to get around the error code 451
    GDPR bullshit
"""
SOCKS5_PROXY_ENABLED = os.getenv('SOCKS5_PROXY_ENABLED') in ['true', 'y', 't']

if SOCKS5_PROXY_ENABLED:
    SOCKS5_PROXY_HOSTNAME = os.getenv('SOCKS5_PROXY_HOSTNAME')
    SOCKS5_PROXY_PORT = int(os.getenv('SOCKS5_PROXY_PORT'))

if os.environ['DEV_ENV'] in ['production', 'staging']:

    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=False
    )
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sorl.thumbnail',
    'shots',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'csp.middleware.CSPMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""

if os.getenv('DEV_ENV') not in 'build':
    DATABASES = {
        'default': dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=600)
    }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache',
    },
    'page': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}



# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

"""
EMAIL SETTINGS
"""
DEFAULT_FROM_EMAIL = "no-reply@screenshot.m3b.net"

if os.environ['DEV_ENV'] in ['test', 'build']:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
else:
    email_config = dj_email_url.parse(os.environ["SMTP_URL"])

    EMAIL_HOST = email_config['EMAIL_HOST']
    EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
    EMAIL_PORT = email_config['EMAIL_PORT']
    EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']

"""
STATIC ASSET HANDLING
  - WhiteNoise configuration for forever-cacheable files and compression support
"""
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

"""
COOKIES & CSRF COOKIE POLICIES

TODO: These are only enabled in production because people the admin/ won't
work without HTTPS enabled. And I'm too lazy to futz with HTTPS on localhost
right now.
"""
if not DEBUG:
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_NAME = '__Host-csrftoken'
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SECURE = True

"""
S3 Settings
"""
S3_BUCKET_PREFIX = os.getenv('S3_BUCKET_PREFIX')
S3_REGION_NAME = os.getenv('S3_REGION_NAME')
S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

"""
sorl thumbnails
"""
THUMBNAIL_DUMMY = True

"""
CONTENT-SECURITY-POLICY
  - Refer to Mozilla Observatory when crafting your CSP: https://observatory.mozilla.org
"""
CSP_DEFAULT_SRC = ("'none'",)
CSP_SCRIPT_SRC = ("'self'",'https://www.googletagmanager.com','https://www.google-analytics.com',)
CSP_STYLE_SRC = ("'self'",)
CSP_INCLUDE_NONCE_IN = ['script-src', 'style-src']
CSP_IMG_SRC = ("'self'","data:",'https://www.google-analytics.com', S3_ENDPOINT_URL, "http://dummyimage.com")
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'none'",)
CSP_FORM_ACTION = ("'self'",)

AWS_STORAGE_BUCKET_NAME = S3_BUCKET_PREFIX
AWS_DEFAULT_ACL = 'public-read'
# AWS_S3_OBJECT_PARAMETERS = {}
# AWS_LOCATION = ''
AWS_S3_REGION_NAME = S3_REGION_NAME
AWS_S3_ENDPOINT_URL = S3_ENDPOINT_URL
