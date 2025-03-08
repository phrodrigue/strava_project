from flask import current_app
import requests

from app.models.user import User
from app.utils.db_tokens import get_tokens


def get_new_token(code):
    """Busca um novo token junto ao Strava"""
    token_data = {
        'client_id': current_app.config['CLIENT_ID'],
        'client_secret': current_app.config['CLIENT_SECRET'],
        'code': code,
        'grant_type': 'authorization_code'
    }

    response = requests.post(
        'https://www.strava.com/oauth/token', data=token_data)
    if response.status_code != 200:
        current_app.logger.error(response.json())
        return

    return response.json()


def refresh_token(user: User):
    """Solicita um novo token"""
    tokens = get_tokens(user)

    if not tokens:
        return

    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': current_app.config['CLIENT_ID'],
            'client_secret': current_app.config['CLIENT_SECRET'],
            'grant_type': 'refresh_token',
            'refresh_token': tokens.refresh_token
        }
    )

    if response.status_code != 200:
        current_app.logger.error(response.json())
        return

    return response.json()
