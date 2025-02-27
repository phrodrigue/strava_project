from flask import Blueprint, current_app, jsonify, request

from app.utils.decorators import time_it
from app.utils.spreadsheet import update_spreadsheet, append_to_spreadsheet
from app.utils.strava.api import call

webhook_bp = Blueprint('webhook', __name__)


# Endpoint para validação do webhook
@webhook_bp.route('/', methods=['GET'])
def validate_webhook():
    challenge = request.args.get('hub.challenge')
    if challenge:
        current_app.logger.info('Teste de validacao de webhook realizado.')
    return jsonify({'hub.challenge': challenge}), 200


# Endpoint para receber eventos do webhook
@webhook_bp.route('', methods=['POST'])
@time_it
def webhook_event():
    data = request.get_json()

    if data['object_type'] != 'activity':
        return '', 200

    try:
        activity_id = data['object_id']
        strava_response = call(f"/activities/{activity_id}", activity_id)

        if data['aspect_type'] == 'create':
            append_to_spreadsheet(strava_response)

        elif data['aspect_type'] == 'update' and 'title' in data['updates'].keys():
            update_spreadsheet(strava_response, str(activity_id))
            
        else:
            # exclusão. registra os dados da atividade
            pass

        response_status_code = 200

    except Exception as e:
        current_app.logger.exception(
            f'Erro ao lidar com os dados enviados ao webhook.\n{data}')
        response_status_code = 400

    return '', response_status_code


@webhook_bp.route('/new_activity/<id>')
def append_activity(id):
    try:
        strava_response = call(f"/activities/{id}", id)
        row = append_to_spreadsheet(strava_response)
        return row, 200
    except Exception as e:
        current_app.logger.exception(
            f'Erro ao recuperar dados de uma atividade atraves de uma URL')
        return '', 400
