from flask import current_app, jsonify, url_for


def generate_auth_url(next):
    """Cria uma url para auenticacao no Strava"""
    return (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={current_app.config['CLIENT_ID']}&"
        f"response_type=code&scope=activity:read_all&"
        f"redirect_uri={current_app.config['REDIRECT_URI']}{next}"
    )


def generate_activity_url(strava_id):
    """Cria uma URL para recuperar dados de uma atividade no Strava"""
    return url_for('activity.get', _external=True, strava_id=strava_id)


def generate_new_activity_url(strava_id):
    """Cria uma URL para recuperar dados de uma nova atividade no Strava e salvar na planilha"""
    return url_for('index', next=f'/{strava_id}')


def create_response(msg: str | list | dict | None = None, status_code: int = 200):
    """Cria uma resposta json padronizada para toda aplicação"""
    return jsonify({'message': msg if msg else ''}), status_code
