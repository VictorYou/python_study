'''Entry point for celery tasks.

See http://www.celeryproject.org/ for more information.
'''

try:
    from celery import Celery, exceptions

    app = Celery()
    app.config_from_object('celery_config')
except:
    # for pydoc support
    import celery_config
