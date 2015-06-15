import os

# Add the current directory to the python path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Specify here the database settings. We support MySQL, PostgreSQL and SQLite
DATABASE = {
    'ENGINE': 'postgres',       # 'postgres', 'sqlite' or 'mysql'. Any other defaults to sqlite
    'NAME': 'shortlrdb',        # Filename for SQLite or DB name for PostgreSQL/MySQL
    'HOST': 'localhost',        # Not needed for SQLite. Server IP. Default: localhost
    'PORT': '5432',             # Not needed for SQLite. PostgreSQL default: 5432
    'USER': 'postgres',         # Not needed for SQLite. User that has access to the DB
    'PASSWORD': 'postgres',     # Not needed for SQLite. Password for the user
}

# Select the default version of the API, this will load specific parts of your
# logic in the app.
DEFAULT_API = 'v1'

# Logging settings. This is a standard python logging configuration. The levels
# are supposed to change depending on the settings file, to avoid clogging the
# logs with useless information.
LOGFILE = 'baratheon.app.log'
LOG_CONFIG = {
    "version": 1,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(filename)s->%(funcName)s:%(lineno)s] %(message)s",
            'datefmt': "%Y/%m/%d %H:%M:%S"
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
    },
    'loggers': {
        'baratheon.app': {
            'handlers': ["logfile", ],
            'level': 'DEBUG',
        },
    }
}
