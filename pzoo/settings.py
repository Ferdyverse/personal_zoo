import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure required data directories exist at startup
for _dir in [
    BASE_DIR / 'data',
    BASE_DIR / 'data' / 'logs',
    BASE_DIR / 'data' / 'uploads',
    BASE_DIR / 'data' / 'uploads' / 'animals',
    BASE_DIR / 'data' / 'uploads' / 'terrariums',
    BASE_DIR / 'data' / 'uploads' / 'documents',
]:
    _dir.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv('PZOO_SECRET_KEY', '4a591941b7f9ce05833eeae0aca040e830072bbb067db5d3f3712b93babbba13')

DEBUG = os.getenv('PZOO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('PZOO_ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'accounts',
    'animals',
    'feeding',
    'history',
    'terrariums',
    'documents',
    'app_settings',
    'api',
    'maintenance',
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

ROOT_URLCONF = 'pzoo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': False,
        'OPTIONS': {
            'environment': 'pzoo.jinja2.environment',
        },
    },
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

WSGI_APPLICATION = 'pzoo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'database_django.db',
    }
}

AUTH_USER_MODEL = 'accounts.User'

# Support old Flask-Bcrypt hashes from migration
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # default for new passwords
    'django.contrib.auth.hashers.BCryptPasswordHasher',   # for migrated Flask passwords
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'de'
LANGUAGES = [('de', 'Deutsch'), ('en', 'English')]
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_DIR / 'data' / 'uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/account/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/account/login'

UNFOLD = {
    'SITE_TITLE': 'Personal Zoo',
    'SITE_HEADER': 'Personal Zoo',
    'SITE_SYMBOL': 'pets',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'THEME': 'dark',
    'COLORS': {
        'primary': {
            '50': '240 253 244',
            '100': '220 252 231',
            '200': '187 247 208',
            '300': '134 239 172',
            '400': '74 222 128',
            '500': '34 197 94',
            '600': '22 163 74',
            '700': '21 128 61',
            '800': '20 83 45',
            '900': '14 64 33',
            '950': '5 46 22',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': True,
        'navigation': [
            {
                'title': 'Animals',
                'icon': 'pets',
                'items': [
                    {'title': 'Animals', 'icon': 'cruelty_free', 'link': '/admin/animals/animal/'},
                    {'title': 'Animal Types', 'icon': 'category', 'link': '/admin/animals/animaltype/'},
                ],
            },
            {
                'title': 'Feeding',
                'icon': 'restaurant',
                'items': [
                    {'title': 'Feedings', 'icon': 'lunch_dining', 'link': '/admin/feeding/feeding/'},
                    {'title': 'Feeding Types', 'icon': 'category', 'link': '/admin/feeding/feedingtype/'},
                ],
            },
            {
                'title': 'History',
                'icon': 'history',
                'items': [
                    {'title': 'History', 'icon': 'event_note', 'link': '/admin/history/history/'},
                    {'title': 'History Types', 'icon': 'category', 'link': '/admin/history/historytype/'},
                ],
            },
            {
                'title': 'Terrariums',
                'icon': 'home',
                'items': [
                    {'title': 'Terrariums', 'icon': 'domain', 'link': '/admin/terrariums/terrarium/'},
                    {'title': 'Terrarium Types', 'icon': 'category', 'link': '/admin/terrariums/terrariumtype/'},
                    {'title': 'Equipment', 'icon': 'build', 'link': '/admin/terrariums/terrariumequipment/'},
                    {'title': 'Lamps', 'icon': 'light', 'link': '/admin/terrariums/terrariumlamps/'},
                    {'title': 'History', 'icon': 'event_note', 'link': '/admin/terrariums/terrariumhistory/'},
                    {'title': 'History Types', 'icon': 'category', 'link': '/admin/terrariums/terrariumhistorytype/'},
                ],
            },
            {
                'title': 'Settings',
                'icon': 'settings',
                'items': [
                    {'title': 'App Settings', 'icon': 'tune', 'link': '/admin/app_settings/appsetting/'},
                    {'title': 'Notifications', 'icon': 'notifications', 'link': '/admin/app_settings/notification/'},
                ],
            },
            {
                'title': 'Users',
                'icon': 'group',
                'items': [
                    {'title': 'Users', 'icon': 'person', 'link': '/admin/accounts/user/'},
                ],
            },
        ],
    },
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s | %(module)s >>> %(message)s',
            'datefmt': '%B %d, %Y %H:%M:%S %Z',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': str(BASE_DIR / 'data' / 'logs' / 'error.log'),
            'maxBytes': 10000,
            'backupCount': 10,
            'delay': True,
            'level': 'ERROR',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'error_file'],
    },
}
