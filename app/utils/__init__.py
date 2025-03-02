from flask import current_app, jsonify, url_for


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


def create_response(msg: str | list | dict, status_code: int):
    """Cria uma resposta json padronizada para todo a aplicação"""
    return jsonify({'message': msg}), status_code
