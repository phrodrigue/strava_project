LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': [
                'debug_console_handler',
                'info_rotating_file_handler',
                'error_file_handler',
                # 'critical_mail_handler'
            ],
        },
        'my.package': {
            'level': 'WARNING',
            'propagate': False,
            'handlers': ['info_rotating_file_handler', 'error_file_handler'],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'DEBUG',
            'formatter': 'standart',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'standart',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'standart',
            'class': 'logging.FileHandler',
            'filename': 'logs/error.log',
            'mode': 'a',
        },
        # 'critical_mail_handler': {
        #     'level': 'CRITICAL',
        #     'formatter': 'standart',
        #     'class': 'logging.handlers.SMTPHandler',
        #     'mailhost': 'localhost',
        #     'fromaddr': 'monitoring@domain.com',
        #     'toaddrs': ['dev@domain.com', 'qa@domain.com'],
        #     'subject': 'Critical error with application name'
        # }
    },
    'formatters': {
        'standart': {
            'format': '%(asctime)s :: %(levelname)-8s- %(name)s::%(filename)s|%(lineno)s:: %(message)s'
        },
    },
}