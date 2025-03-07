import os
import sys
from django.core.management.utils import get_random_secret_key
import dj_database_url
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent

print('BASE_DIR', BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', False) == 'True'

ALLOWED_HOSTS = [
    '127.0.0.0',
    'localhost',
    '137.184.111.7',
    'pavliati.pythonanywhere.com',
    'fractalportfolios.com',
    'www.fractalportfolios.com'
]

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Email backend configuration based on the environment
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# SMTP settings for production
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = bool(os.getenv('EMAIL_USE_TLS', True))
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Your email address
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Your email password or API key
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'your-email@example.com')

# Other Django settings
DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')



# MainApplication definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'django_celery_beat',
    "rest_framework",
    "rest_framework_simplejwt",
    'risk',
    'reports',
    'signals',
    'mysite.apps.MySiteConfig',
    'portfolio.apps.PortfolioConfig',
    'accounts',
    'trade_app',
    'instrument',
    'calculations',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configure REST Framework to use JWT
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # Short-lived access token
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # Longer-lived refresh token
    "ROTATE_REFRESH_TOKENS": True,  # Issues new refresh token on refresh
    "BLACKLIST_AFTER_ROTATION": True,  # Blacklist old refresh tokens
    "AUTH_HEADER_TYPES": ("Bearer",),  # Token sent in Authorization header
}

# Celery settings
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"


CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.0:8001',
    'https://137.184.111.7:443',
    'https://137.184.111.7',
    "http://localhost:3000",
    'https://pavliati.pythonanywhere.com',
    'https://fractalportfolios.com',
    'http://www.fractalportfolios.com',
    'https://www.fractalportfolios.com',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': str(BASE_DIR) + '/cache',
    }
}

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['front_end/build'],
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

# WSGI_APPLICATION = 'mysite.wsgi.application'

ASGI_APPLICATION = 'mysite.asgi.application'

# Database
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', False) == 'True'

if DEVELOPMENT_MODE:
    # Local development settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'ffm_web',
            'USER': 'root',
            'PASSWORD': 'test88',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    }
else:
    # Production settings - Use DATABASE_URL environment variable
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL)
        }
    else:
        raise Exception('DATABASE_URL environment variable not defined')

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'mysite.validators.CustomPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Budapest'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    os.path.join(BASE_DIR, 'front_end/build/static'), # This is the path for the React fornt end static files
]

# default static files settings for PythonAnywhere.
MEDIA_ROOT = os.path.join(BASE_DIR, '/media')
MEDIA_URL = '/media/'
STATIC_ROOT = '/var/www/ffm_static/' #os.path.join(BASE_DIR, 'staticfiles') #'/var/www/ffm_static/'
LOGIN_URL = "/home/"

