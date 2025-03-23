import json
from time import sleep
from flask import current_app
from flask.cli import AppGroup
from gspread.utils import ValueInputOption
import requests

from app import db
from app.models import Activity, User
from app.utils.db_activity import get_activity_or_none, get_activity_state
from app.utils.decorators import cli_auth_user_required, cli_user_and_activities_required
from app.utils.spreadsheet import open_worksheet
from app.utils.spreadsheet.spreadsheet_row import SpreadsheetRow
from app.utils.strava.response import StravaResponse


update = AppGroup('update', help='Comandos para lidar com a atualização do banco de dados e da planilha.')


@update.command('json')
@cli_auth_user_required
def get_all_activities(user: User, access_token):
    """
    Pega todas as atividades do Strava e salva em um JSON
    """
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
                'start_date_local': activity['start_date_local'],
                'elevation': activity['total_elevation_gain'],
            }

            if activity['has_heartrate']:
                final[activity['id']]['fc_max'] = activity['max_heartrate']
                final[activity['id']]['fc_avg'] = activity['average_heartrate']

        params['page'] += 1

    with open(current_app.config['JSON_ACTIVITY_PATH'], 'w') as file:
        json.dump(final, file, indent=4)

    print('Procedimento finalizado.')


@update.command('db')
@cli_user_and_activities_required
def save_to_db(user: User, activities: dict):
    """
    Atualiza o banco de dados com as atividades salvas no arquivo JSON
    """
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
                user=user,
                fc_max = activity.get('fc_max'),
                fc_avg = activity.get('fc_avg'),
                elevation = activity['elevation']
            )

            to_add.append(a)
            print(f'Adicionando atividade {id}...')
        else:
            print(f'Atividade {id} já no banco de dados.')

    db.session.add_all(to_add)
    db.session.commit()
    print('Procedimento finalizado.')


@update.command('sheet')
@cli_user_and_activities_required
def save_to_spreadsheet(user: User, activities: dict):
    """
    Atualiza a planilha com as atividades salvas no arquivo JSON
    """
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


@update.command('temp')
@cli_user_and_activities_required
def temp(user: User, activities: dict):
    """
    Atualiza as entradas no DB e na planilha com os dados da FC e da elevação
     - comando temporário
    """
    ws = open_worksheet()
    sheet_lines = ws.get_all_values()

    criado_state = get_activity_state('Atualizado')
    to_add_in_db = []
    to_add_in_sheet = []

    tot_activities = len(activities)
    print(f'Atualizando <{tot_activities}> atividades.')

    i = 1
    for id, activity in activities.items():
        print(f'\n--\n\n[{i:0>3}/{tot_activities:0>3}] Atualizando atividade [{id}]')
        i += 1
        # atualiza no DB
        a = get_activity_or_none(id)
        if not a:
            a = Activity(
                strava_id = id,
                type = activity['type'],
                desc = 'Criada pela CLI - FC e elevacao',
                state = criado_state,
                user = user,
                fc_max = activity.get('fc_max'),
                fc_avg = activity.get('fc_avg'),
                elevation = activity['elevation']
            )

            to_add_in_db.append(a)
            print(f'Atividade adicionada no DB')
        else:
            a.last_update_desc = 'Atualizada pela CLI - FC e elevacao'
            a.fc_max = activity.get('fc_max')
            a.fc_avg = activity.get('fc_avg')
            a.elevation = activity['elevation']
            print(f'Atividade atualizada no DB.')
        
        # atualiza na planilha
        n_row = 0
        for i, line in enumerate(sheet_lines):
            if str(line[0]) == str(id):
                n_row = i + 1
                break

        if n_row:
            ws.update(
                [
                    [
                        activity.get('fc_max'),
                        activity.get('fc_avg'),
                        activity['elevation']
                    ]
                ],
                f'E{n_row}:G{n_row}',
                value_input_option=ValueInputOption.user_entered
            )
            print('Linha na planilha atualizada')
        else:
            resp = StravaResponse(json=activity)
            to_add_in_sheet.append(SpreadsheetRow(resp, id).new)
            print('Atividade fora da planilha. Será adicionada depois.')
        
        sleep(1)

    print('Todas as atividades verificadas')
    if to_add_in_sheet:
        ws.append_rows(
            values=to_add_in_sheet,
            value_input_option=ValueInputOption.user_entered
        )
        print(f'Linhas adicionadas na planilha:')
        for r in to_add_in_sheet:
            print(r)
    else:
        print('Nenhuma linha adicionada na planilha.')

    db.session.add_all(to_add_in_db)
    db.session.commit()
    print('Procedimento finalizado.')
