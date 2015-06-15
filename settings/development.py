import os

# Add the current directory to the python path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Specify here the database settings.
DATABASE = {
    'NAME': 'shortlrdb',        # DB name in PostgreSQL
    'HOST': 'localhost',        # Server IP. Default: localhost
    'PORT': '5432',             # PostgreSQL default: 5432
    'USER': 'postgres',         # User that has access to the DB
    'PASSWORD': 'postgres',     # Password for the user
}

# Default version of the API
DEFAULT_API = 'v1'

# Logging settings. This is a standard python logging configuration. The levels
# are supposed to change depending on the settings file, to avoid clogging the
# logs with useless information.
LOGFILE = 'baratheon.app.log'
LOG_CONFIG = {
    "version": 1,
    'formatters': {
        'standard': {
            '()': 'colorlog.ColoredFormatter',
            'format': "[%(asctime)s] [%(process)s] [%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S %z"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, LOGFILE),
            'maxBytes': 2097152,  # 2MB per file
            'backupCount': 2,  # Store up to three files
            'formatter': 'standard',
        },
        'stream': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        'baratheon.app': {
            'handlers': ["logfile", 'stream'],
            'level': 'DEBUG',
        },
    }
}
