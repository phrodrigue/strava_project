from datetime import datetime
import threading

from flask import current_app
import gspread
from gspread.utils import ValueInputOption

from app.utils import generate_activity_url, seconds_to_hours
from app.utils.strava.api import call


def append_to_spreadsheet_from_object_id(id):
    """Adiciona na planilha uma linha com os dados recebidos da API do Strava"""
    data = call(f"/activities/{id}", id)

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

    spredsheet_key = current_app.config['SPREADSHEET_KEY']
    threading.Thread(
        target=append_spreadsheet,
        args=(row, spredsheet_key)
    ).start()

    return row


def append_spreadsheet(row_data, key):
    """Funcao para possibilitar a utilizacao da API do Google de forma assincrona"""
    gc = gspread.service_account(filename='credentials.json') # type: ignore
    sh = gc.open_by_key(key)
    ws = sh.worksheet('NOVAS ATIVIDADES')
    ws.append_row(row_data, value_input_option=ValueInputOption.user_entered)
