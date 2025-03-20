import os.path
import json
import time

import click
from flask import current_app
from flask.cli import AppGroup
from gspread.utils import ValueInputOption
import requests

from app import db
from app.models.activity import Activity
from app.utils import generate_auth_url
from app.utils.db_activity import get_activity_or_none, get_activity_state
from app.utils.db_tokens import get_tokens
from app.utils.db_user import get_user_or_none
from app.utils.spreadsheet import open_worksheet
from app.utils.spreadsheet.spreadsheet_row import SpreadsheetRow
from app.utils.strava.response import StravaResponse
from app.utils.strava.tokens import refresh_token


update = AppGroup('update', help='Comandos para lidar com a atualização do banco de dados e da planilha.')


@update.command('json')
@click.option('--user', prompt='ID do usuário', help='ID do usuário da atividade.', type=int)
def get_all_activities(user):
    """
    Pega todas as atividades do Strava e salva em um JSON
    """
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

    access_token = token.access_token

    # Verifica se o token expirou e renova se necessário
    if time.time() > token.expires_at:
        new_token = refresh_token(user)
        if not new_token:
            print(f'Não foi possível renovar o token do usuário {user.name}')
            print(f'Refaça o login acessando:\n{generate_auth_url("/")}')
            return
        print('Token renovado.')
        access_token = new_token['access_token']

    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'after': 1704078000,    # a partir de 01-01-2024
        'page': 1,
        'per_page': 30
    }

    final: dict[str, dict] = {}

    print(f'Por página: {params["per_page"]}')
    while True:
        print(f'Buscando página {params["page"]}...')
        response = requests.get(
            f'{current_app.config["API_URL"]}/athlete/activities',
            headers = headers,
            params = params
        )
        activities = response.json()

        if not activities:
            print('Nenhuma atividade encontrada.')
            break

        for activity in activities:
            print(f'Adicionando atividade {activity["id"]}...')
            final[activity['id']] = {
                'id': activity['id'],
                'user_id': activity['athlete']['id'],
                'name': activity['name'],
                'distance': activity['distance'],
                'moving_time': activity['moving_time'],
                'type': activity['type'],
                'sport_type': activity['sport_type'],
                'start_date': activity['start_date'],
                'start_date_local': activity['start_date_local']
            }

        params['page'] += 1

    with open('instance/all_activities.json', 'w') as file:
        json.dump(final, file, indent=4)

    print('Procedimento finalizado.')


@update.command('db')
@click.option('--user', prompt='ID do usuário', help='ID do usuário das atividades.', type=int)
def save_to_db(user):
    """
    Atualiza o banco de dados com as atividades salvas no arquivo JSON
    """
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

    criado_state = get_activity_state('Criado')
    to_add = []

    for id, activity in activities.items():
        a = get_activity_or_none(id)
        if not a:
            a = Activity(
                strava_id=id,
                type=activity['type'],
                desc='Criada pela CLI',
                state=criado_state,
                user=user
            )

            to_add.append(a)
            print(f'Adicionando atividade {id}...')
        else:
            print(f'Atividade {id} já no banco de dados.')

    db.session.add_all(to_add)
    db.session.commit()
    print('Procedimento finalizado.')


@update.command('sheet')
def save_to_spreadsheet():
    """
    Atualiza a planilha com as atividades salvas no arquivo JSON
    """
    file_path = current_app.config['JSON_ACTIVITY_PATH']

    if not os.path.isfile(file_path):
        print('Arquivo com atividades não encontrado.')
        return

    with open(file_path, 'r') as file:
        activities: dict = json.load(file)

    to_add = []
    ws = open_worksheet()
    all_rows = ws.get_all_values()

    for id, activity in activities.items():
        added = False
        for row in all_rows:
            if row[0] == id:
                added = True
                break
        if added: continue

        resp = StravaResponse(json=activity)
        to_add.append(SpreadsheetRow(resp, id).new)

    if to_add:
        ws.append_rows(
            values=to_add,
            value_input_option=ValueInputOption.user_entered
        )
        print(f'Linhas adicionadas:')
        for r in to_add:
            print(r)
    else:
        print('Nenhuma linha adicionada.')
