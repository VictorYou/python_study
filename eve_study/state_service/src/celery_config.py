'''Celery configuration for labrequest_tasks and snapshot_tasks.

See http://www.celeryproject.org/ for more information.
'''
from logging.config import dictConfig
import os

BROKER_URL = 'amqp://rabbit'
CELERY_IMPORTS = ('snapshot_tasks','labrequest_tasks')
CELERY_RESULT_BACKEND = 'rpc://rabbit'
CELERY_ROUTES = ([
    ('snapshot_tasks.*', {'queue': 'snapshot_tasks'}),
    ('labrequest_tasks.*', {'queue': 'labrequest_tasks'}),
],)

if os.getenv('STATE_SERVICE_ENABLE_CELERY_LOGGING'):
    CELERYD_HIJACK_ROOT_LOGGER = False
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'snapshot_tasks', 'labrequest_tasks'],
        },
        'formatters': {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'snapshot_tasks': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'snapshot_tasks.log',
                'formatter': 'simple',
                'maxBytes': 100000,
                'backupCount': 3
            },
            'labrequest_tasks': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'labrequest_tasks.log',
                'formatter': 'simple',
                'maxBytes': 100000,
                'backupCount': 3
            },
            'celery': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'celery.log',
                'formatter': 'simple',
                'maxBytes': 100000,
                'backupCount': 3
            },
        },
        'loggers': {
            'snapshot_tasks': {
                'handlers': ['snapshot_tasks', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
            'labrequest_tasks': {
                'handlers': ['labrequest_tasks', 'console'],
                'level': 'INFO',
                'propagate': True,
            },
            'celery': {
                'handlers': ['celery', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
    dictConfig(LOGGING)
else:
    print "Celery logging is disabled. Enable by setting STATE_SERVICE_ENABLE_CELERY_LOGGING"
