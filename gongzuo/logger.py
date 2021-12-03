
import sys
import logging
from logging.config import dictConfig
from pathlib import Path
from datetime import date

LOGGING_PATH = Path(r"logs")
LOGGING_PATH.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {
            'level': 'NOTSET',
            'handlers': ['console_handler', 'debug_handlers'],
        },
    },
    'handlers': {
        'console_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
        'debug_handlers': {
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.FileHandler',
            'filename': LOGGING_PATH / f'{date.today()}.log',
        }
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s [%(name)s.%(module)s] %(levelname)s: %(message)s'
        },
        'error': {
            'format': '%(asctime)s [%(process)d.%(module)s:%(lineno)s] %(levelname)s: %(message)s'
        },
        'debug': {
            'format': '%(asctime)s [%(process)d.%(module)s:%(lineno)s] %(levelname)s: %(message)s'
        },
    },
}

dictConfig(LOGGING_CONFIG)