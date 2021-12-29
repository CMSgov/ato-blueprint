import logging.config
import os
from django.utils.log import DEFAULT_LOGGING
from .settings import LOGLEVEL

# Disable Django's logging setup
LOGGING_CONFIG = None

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        # Our application code
        'siteapp': {
            'level': LOGLEVEL,
            'handlers': ['console'],
            # Avoid double logging because of root logger
            'propagate': False,
        },
        'mozilla_django_oidc': {
            'handlers': ['console'],
            'level': LOGLEVEL,
        },
        'nplusone': {
            'handlers': ['console'],
            'level': 'WARN',
        },
        ## Add if necessary
        ##        # Prevent noisy modules from logging to non-console loggers (if any)
        ##        'noisy_module': {
        ##            'level': 'ERROR',
        ##            'handlers': ['console'],
        ##            'propagate': False,
        ##        },
        # Default runserver request logging
        # 'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

