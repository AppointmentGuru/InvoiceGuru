import os, raven

def get_secret(f):
    '''Returns a docker secret'''
    try:
        return open('/run/secrets/{}'.format(f)).read().rstrip()
    except IOError:
        return os.environ.get(f)


ALLOWED_HOSTS = [host.strip() for host in os.environ.get("ALLOWED_HOSTS", '').split(',')]
# aws storage
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_AUTO_CREATE_BUCKET = True
AWS_ACCESS_KEY_ID = get_secret('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_secret('AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = 'eu-central-1'
# AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)
STATIC_URL = "https://s3.amazonaws.com/{}/".format(AWS_STORAGE_BUCKET_NAME)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

MEDIA_URL = "https://s3.amazonaws.com/{}/media/".format(AWS_STORAGE_BUCKET_NAME)

TEMPLATE_REGISTRY = {
    'basic': {
        'filename': 'basic.html',
        'title': 'A simple invoice template',
        'description': 'A quick and easy template for simple invoices'
    },
    'basic_v2': {
        'filename': 'basic_v2.html',
        'title': 'Version 2 of the simple invoice template',
        'description': 'A quick and easy template for simple invoices'
    },
    # 'material': {
    #     'filename': 'material.html',
    #     'title': 'A meterial design themed invoice template',
    #     'description': 'An attractive simple invoice template'
    # }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DATABASE_NAME', 'postgres'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'HOST': os.environ.get('DATABASE_HOST', 'postgres'),
        'PORT': 5432,
    }
}
db_password = os.environ.get('DATABASE_PASSWORD', False)
if db_password:
    DATABASES.get('default').update({'PASSWORD': db_password})

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    # 'DEFAULT_PERMISSION_CLASSES': (
    #     'rest_framework.permissions.IsAuthenticated',
    # ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'kong_oauth.drf_authbackends.KongDownstreamAuthHeadersAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

FUNCTIONGURU_URL = 'https://functionguru.appointmentguru.co'
PUB_SUB_BACKEND = ('backends', 'PubNubBackend')
PUB_SUB_CHANNEL = get_secret('PUBNUB_SCHOOL_CHANNEL_PREFIX')

# service dependencies:
MEDICALAIDGURU_API = 'http://medicalaidguru'
APPOINTMENTGURU_API = 'http://appointmentguru'
COMMUNICATIONGURU_API = 'http://unibox'
# COMMUNICATIONGURU_API = 'https://unibox.appointmentguru.co'
# APPOINTMENTGURU_API = 'https://swarm.appointmentguru.co/v1'

INVOICEGURU_BASE_URL =  os.environ.get(
                            'INVOICEGURU_BASE_URL',
                            'https://invoiceguru.appointmentguru.co'
                        )
# INVOICEGURU_BASE_URL = 'http://host.docker.internal:8001'

GOOGLE_API_SHORTENER_TOKEN = os.environ.get('GOOGLE_API_SHORTENER_TOKEN')

KEEN_PROJECT_ID = os.environ.get('project_key')
KEEN_WRITE_KEY = os.environ.get('keen_write_key')

if os.environ.get('DEBUG', 'false') != 'true':
    DEBUG = False
else:
    DEBUG = True

class PUBLISHKEYS:
    '''A config of the events published by this service'''
    invoice_sent='invoice_sent'
    invoice_paid='invoice_paid'
    payment_received='payment_received'

sentry_url = 'https://{}:{}@sentry.io/{}'.format(
    os.environ.get('SENTRY_PUBLIC_KEY'),
    os.environ.get('SENTRY_SECRET_KEY'),
    os.environ.get('SENTRY_PROJECT_ID')
)
RAVEN_CONFIG = {
    'dsn': sentry_url,
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    # 'release': raven.fetch_git_sha(os.path.abspath(os.pardir)),
}

if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['sentry'],
        },
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s '
                        '%(process)d %(thread)d %(message)s'
            },
        },
        'handlers': {
            'sentry': {
                'level': 'ERROR', # To capture more than ERROR, change to WARNING, INFO, etc.
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
                'tags': {'custom-tag': 'x'},
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            }
        },
        'loggers': {
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            'raven': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
            'sentry.errors': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': False,
            },
        },
    }