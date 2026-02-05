from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {module} - {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "error.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "level": "ERROR",
        },
    },

    "loggers": {
        "profiles": {
            "handlers": ["console", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "authentication": {
            "handlers": ["console", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "payments": {
            "handlers": ["console", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "common": {
            "handlers": ["console", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django": {
            "handlers": ["console", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
    },

    "root": {
        "handlers": ["console", "error_file"],
        "level": "INFO",
    },
}
