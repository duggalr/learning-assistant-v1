"""
Django settings for gpt_learning_assistant project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv


if 'PRODUCTION' not in os.environ:
    dot_env_file = find_dotenv()
    load_dotenv(dot_env_file)


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/


if 'PRODUCTION' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']
else:
    SECRET_KEY = 'django-insecure-r8d(r2)5kr!sjx5$8yv0mmgz)7w&@$99*=k*3if@8io^$uf)+w'

# SECURITY WARNING: don't run with debug turned on in production!
if 'PRODUCTION' in os.environ:
    DEBUG = False
else:
    DEBUG = True

if 'PRODUCTION' in os.environ:
    ALLOWED_HOSTS = ['codecompanion.app', 'www.codecompanion.app']
else:
    ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'learning_assistant',
    'storages'
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

ROOT_URLCONF = 'gpt_learning_assistant.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'gpt_learning_assistant.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if 'PRODUCTION' in os.environ:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_DB_USERNAME'],
            'PASSWORD': os.environ['RDS_DB_PASSWORD'],
            'HOST': os.environ['RDS_DB_HOST'],
            'PORT': '5432',
        }
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['LOCAL_DB_NAME'],
            'USER': os.environ['LOCAL_DB_HOST_USER'],
            'PASSWORD': os.environ['LOCAL_DB_PASSWORD'],
            'HOST': os.environ['LOCAL_DB_HOST'],
            'PORT': '5432',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_USE_TLS = True  
EMAIL_HOST = 'smtp.gmail.com'  
EMAIL_HOST_USER = os.environ['SMTP_EMAIL']
EMAIL_HOST_PASSWORD = os.environ['SMTP_PASSWORD']
EMAIL_PORT = 587  

## Celery
if 'PRODUCTION' in os.environ:
    CELERY_BROKER_URL = "redis://default:W69a6gEdTMH6AKxDnx4lRtZMXbepBjcU@redis-18616.c80.us-east-1-2.ec2.cloud.redislabs.com:18616"
    CELERY_RESULT_BACKEND = "redis://default:W69a6gEdTMH6AKxDnx4lRtZMXbepBjcU@redis-18616.c80.us-east-1-2.ec2.cloud.redislabs.com:18616"
else:
    CELERY_BROKER_URL = "redis://localhost:6379"
    CELERY_RESULT_BACKEND = "redis://localhost:6379"


# PROJECT_ROOT = os.path.abspath(os.path.dirname(__name__))
# STATIC_URL = 'static/'

PROJECT_ROOT = os.path.abspath(os.path.dirname(__name__))
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/'),
)
## Files
if 'PRODUCTION' in os.environ:
    ## AWS Static Files
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

    # Tell django-storages the domain to use to refer to static files.
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

    # Tell the staticfiles app to use S3Boto3 storage when writing the collected static files (when you run `collectstatic`).
    STATICFILES_LOCATION = 'static'
    MEDIAFILES_LOCATION = 'media'

    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
    STATICFILES_STORAGE = 'custom_storages.StaticStorage'

else:
    # User Uploaded Media Files
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')
    MEDIA_URL = '/media/'


if 'PRODUCTION' in os.environ:
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    # X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 604800  # set low, but when site is ready for deployment, set to at least 15768000 (6 months)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


## File Upload Settings
X_FRAME_OPTIONS = 'SAMEORIGIN'
MAX_FILE_SIZE = 5000000


