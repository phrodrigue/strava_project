from functools import wraps
import json
import os
from time import time
from typing import Callable

import click
from flask import current_app

from app.utils import generate_auth_url
from app.utils.db_tokens import get_tokens
from app.utils.db_user import get_user_or_none
from app.utils.strava.tokens import refresh_token


def time_it(f: Callable):
    @wraps(f)
    def wrapper(*args, **kargs):
        start = time()
        result = f(*args, **kargs)
        elapsed = time() - start
        current_app.logger.info(f'WEBHOOK executado em {elapsed:.5f}s')
        return result
    return wrapper


def cli_auth_user_required(f: Callable):
    @wraps(f)
    @click.option('--user', prompt='ID do usuário', help='ID do usuário das atividades.', type=int)
    def wrapper(user, *args, **kargs):
        user = get_user_or_none(user)
        if not user:
            print('Usuário não encontrado')
            print(f'Para fazer o login, acesse:\n{generate_auth_url("/")}')
            return

        token = get_tokens(user)
        if not token:
            print(f'Nenhum token encontrado para o usuário {user.name}')
            print(f'Para fazer o login, acesse:\n{generate_auth_url("/")}')
            return

        # Verifica se o token expirou e renova se necessário
        if time() > token.expires_at:
            new_token = refresh_token(user)
            if not new_token:
                print(f'Não foi possível renovar o token do usuário {user.name}')
                print(f'Refaça o login acessando:\n{generate_auth_url("/")}')
                return
            print('Token renovado.')
            access_token = new_token['access_token']
        else:
            access_token = token.access_token

        return f(user, access_token, *args, **kargs)
    return wrapper


def cli_user_and_activities_required(f: Callable):
    @wraps(f)
    @click.option('--user', prompt='ID do usuário', help='ID do usuário das atividades.', type=int)
    def wrapper(user, *args, **kargs):
        user = get_user_or_none(user)
        if not user:
            print('Usuário não encontrado')
            return

        file_path = current_app.config['JSON_ACTIVITY_PATH']

        if not os.path.isfile(file_path):
            print('Arquivo com atividades não encontrado.')
            return

        with open(file_path, 'r') as file:
            activities: dict = json.load(file)
        return f(user, activities, *args, **kargs)
    return wrapper