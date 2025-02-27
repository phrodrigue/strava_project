from datetime import datetime
import os

from flask import current_app
import gspread
from gspread.utils import ValueInputOption

from app.utils import generate_activity_url, seconds_to_hours
from app.utils.strava.response import StravaResponse


def open_worksheet():
    spredsheet_key = current_app.config['SPREADSHEET_KEY']

    root_path = str(os.path.abspath((os.path.dirname(__file__))))
    gc = gspread.service_account(filename=root_path + '/credentials.json') # type: ignore
    
    sh = gc.open_by_key(spredsheet_key)
    ws = sh.worksheet('NOVAS ATIVIDADES')
    return ws


def append_to_spreadsheet(data: StravaResponse):
    """Adiciona na planilha uma linha com os dados recebidos da API do Strava"""
    if not data.OK:
        row = [
            id,
            'ERRO NA API',
            data.JSON['message'],
            '',
            'LOGIN:',
            data.JSON['url'],
        ]

    else:
        activity_date = data.JSON['start_date_local']
        date_obj = datetime.strptime(activity_date, "%Y-%m-%dT%H:%M:%SZ")

        row = [
            data.JSON['id'],
            data.JSON['name'],
            date_obj.strftime("%d/%m/%Y"),
            data.JSON['distance'],
            seconds_to_hours(data.JSON['elapsed_time']),
            generate_activity_url(data.JSON['id'])
        ]

    ws = open_worksheet()
    ws.append_row(row, value_input_option=ValueInputOption.user_entered)

    ws.format(
        'D:D',
        {
            'numberFormat': {
                "type": 'NUMBER',
                "pattern": '0.0,"km"'
                }
        }
    )
    return row


def update_spreadsheet(data: StravaResponse, activity_id):
    if not data.OK:
        current_app.logger.error(f'erro ao atualizar atividade: {data.JSON}')
        return
    
    ws = open_worksheet()
    cell = ws.find(activity_id)

    if not cell:
        current_app.logger.error(f'erro ao atualizar atividade: atividade nao encontrada {activity_id}')
        return

    activity_date = data.JSON['start_date_local']
    date_obj = datetime.strptime(activity_date, "%Y-%m-%dT%H:%M:%SZ")

    row = [
        data.JSON['name'],
        date_obj.strftime("%d/%m/%Y"),
        data.JSON['distance'],
        seconds_to_hours(data.JSON['elapsed_time']),
        generate_activity_url(data.JSON['id'])
    ]

    ws.update(
        [row],
        f'B{cell.row}:F{cell.row}',
        value_input_option=ValueInputOption.user_entered
    )

    ws.format(
        f'D{cell.row}',
        {
            'numberFormat': {
                "type": 'NUMBER',
                "pattern": '0.0,"km"'
                }
        }
    )
