import time

from flask import current_app
import requests

from app.models import User
from app.utils import generate_auth_url, generate_new_activity_url
from app.utils.db_tokens import get_tokens
from app.utils.exceptions import APIResponseException, DeletedActivityException, SportNotAllowedException
from app.utils.strava.response import StravaResponse
from app.utils.strava.tokens import refresh_token


def call(path: str, activity_id, user: User, only_search=False) -> StravaResponse:
    """Faz uma chamada para a API do Strava e retorna um objeto 'StravaResponse' com os dados recebidos"""
    token = get_tokens(user)
    if not token:
        json_message = {
            'message': 'tokens not found',
            'url': generate_auth_url(next=generate_new_activity_url(activity_id))
        }
        return StravaResponse(token_not_present=True, json=json_message)

    access_token = token.access_token

    # Verifica se o token expirou e renova se necessário
    if time.time() > token.expires_at:
        new_token = refresh_token(user)
        if not new_token:
            json_message = {
                'message': 'tokens expired',
                'url': generate_auth_url(next=generate_new_activity_url(activity_id))
            }
            return StravaResponse(token_expired=True, json=json_message)
        access_token = new_token['access_token']

    headers = {'Authorization': f"Bearer {access_token}"}
    response = requests.get(f"{current_app.config['API_URL']}{path}", headers=headers)
    response_json = response.json()

    if response.status_code != 200:
        if response_json['message'] == 'Record Not Found' and response_json['errors'][0]['code'] == 'invalid':
            raise DeletedActivityException(activity_id)
        raise APIResponseException(response_json)

    if not only_search and response_json['sport_type'] not in current_app.config['ALLOWED_SPORTS']:
        raise SportNotAllowedException(response_json['sport_type'])

    return StravaResponse(json=response.json())
