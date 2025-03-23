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


def append_to_spreadsheet(data: StravaResponse, strava_id: int):
    """Adiciona na planilha uma linha com os dados recebidos da API do Strava"""
    spreadsheet_row = SpreadsheetRow(data, strava_id)

    ws = open_worksheet()
    ws.append_row(spreadsheet_row.new, value_input_option=ValueInputOption.user_entered)
    ws.format(
        'D',
        {
            'numberFormat': {
                "type": 'DATE',
                "pattern": 'ddd", "dd"/"mm"/"yy'
                }
        }
    )
    ws.format(
        'H',
        {
            'numberFormat': {
                "type": 'NUMBER',
                "pattern": '0.0,"km"'
                }
        }
    )


def update_in_spreadsheet(data: StravaResponse, strava_id: int):
    if not data.OK:
        current_app.logger.error(f'erro ao atualizar atividade: {data.JSON}')
        return

    ws = open_worksheet()
    cell = ws.find(str(strava_id))

    if not cell:
        current_app.logger.error(f'atividade nao encontrada na planilha [{strava_id}]')
        return

    spreadsheet_row = SpreadsheetRow(data, strava_id)

    ws.update(
        [spreadsheet_row.new[1:]],
        f'B{cell.row}:I{cell.row}',
        value_input_option=ValueInputOption.user_entered
    )
    ws.format(
        f'D{cell.row}',
        {
            'numberFormat': {
                "type": 'DATE',
                "pattern": 'ddd", "dd"/"mm"/"yy'
                }
        }
    )
    ws.format(
        f'H{cell.row}',
        {
            'numberFormat': {
                "type": 'NUMBER',
                "pattern": '0.0,"km"'
            }
        }
    )


def delete_in_spreadsheet(strava_id: int):
    ws = open_worksheet()
    cell = ws.find(str(strava_id))

    if not cell:
        current_app.logger.error(f'atividade nao encontrada na planilha [{strava_id}]')
        return

    ws.update(
        [[f'x-{strava_id}']],
        f'A{cell.row}',
        value_input_option=ValueInputOption.user_entered
    )
    ws.format(
        f'A{cell.row}:K{cell.row}',
        {
            'textFormat': {
                'foregroundColorStyle':  {
                    'rgbColor': {
                        "red": 183/255,
                        "green": 183/255,
                        "blue": 183/255
                    }
                },
            },
        }
    )

