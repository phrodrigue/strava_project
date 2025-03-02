import os

from flask import current_app
import gspread
from gspread.utils import ValueInputOption

from app.utils.spreadsheet.spreadsheet_row import SpreadsheetRow
from app.utils.strava.response import StravaResponse


def open_worksheet():
    spredsheet_key = current_app.config['SPREADSHEET_KEY']

    root_path = str(os.path.abspath((os.path.dirname(__file__))))
    gc = gspread.service_account(filename=root_path + '/credentials.json') # type: ignore
    
    sh = gc.open_by_key(spredsheet_key)
    ws = sh.worksheet('NOVAS ATIVIDADES')
    return ws


def append_to_spreadsheet(data: StravaResponse, activity_id: int):
    """Adiciona na planilha uma linha com os dados recebidos da API do Strava"""
    spreadsheet_row = SpreadsheetRow(data, activity_id)

    ws = open_worksheet()
    ws.append_row(spreadsheet_row.new, value_input_option=ValueInputOption.user_entered)
    ws.format(
        'E',
        {
            'numberFormat': {
                "type": 'NUMBER',
                "pattern": '0.0,"km"'
                }
        }
    )
    return spreadsheet_row.new


def update_spreadsheet(data: StravaResponse, activity_id: int):
    if not data.OK:
        current_app.logger.error(f'erro ao atualizar atividade: {data.JSON}')
        return
    
    ws = open_worksheet()
    cell = ws.find(str(activity_id))

    if not cell:
        current_app.logger.error(f'erro ao atualizar atividade: atividade nao encontrada {activity_id}')
        return
    
    spreadsheet_row = SpreadsheetRow(data, activity_id)

    ws.update(
        [spreadsheet_row.new[1:]],
        f'B{cell.row}:G{cell.row}',
        value_input_option=ValueInputOption.user_entered
    )
    ws.format(
        f'E{cell.row}',
        {
            'numberFormat': {
                "type": 'NUMBER',
                "pattern": '0.0,"km"'
                }
        }
    )
