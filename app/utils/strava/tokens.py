from flask import current_app
import requests

from app.utils.tokens_db import get_tokens, save_tokens


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

    tokens = response.json()
    save_tokens(
        tokens['access_token'],
        tokens['refresh_token'],
        tokens['expires_at']
    )

    return True


def refresh_token():
    """Solicita um novo token"""
    tokens = get_tokens(current_app.config['USER_ID'])
    if not tokens or 'refresh_token' not in tokens:
        return

    response = requests.post(
        'https://www.strava.com/oauth/token',
        data={
            'client_id': current_app.config['CLIENT_ID'],
            'client_secret': current_app.config['CLIENT_SECRET'],
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']
        }
    )

    if response.status_code != 200:
        current_app.logger.error(response.json())
        return

    new_tokens = response.json()
    save_tokens(
        new_tokens['access_token'],
        new_tokens['refresh_token'],
        new_tokens['expires_at']
    )

    return new_tokens['access_token']
