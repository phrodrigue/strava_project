from flask import current_app, url_for


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


def generate_auth_url(next=None):
    """Cria uma url para auenticacao no Strava"""
    return (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={current_app.config['CLIENT_ID']}&"
        f"redirect_uri={current_app.config['REDIRECT_URI']}/{next if next else ''}&"
        f"response_type=code&scope=activity:read_all"
    )


def generate_activity_url(id):
    """Cria uma URL para recuperar dados de uma atividade no Strava"""
    return url_for('activity', _external=True, id=id)


def generate_new_activity_url(id):
    """Cria uma URL para recuperar dados de uma nova atividade no Strava e salvar na planilha"""
    return url_for('webhook.append_activity', _external=True, id=id)


def seconds_to_hours(seconds):
    """Converte o tempo em segundos para o formato H:MM:SS"""
    hours, rest = divmod(seconds, 3600)
    minutes, seconds = divmod(rest, 60)

    return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
