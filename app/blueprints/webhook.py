from flask import Blueprint, current_app, jsonify, request

from app.utils.decorators import time_it
from app.utils.spreadsheet import append_to_spreadsheet_from_object_id

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

    try:
        if data['object_type'] == 'activity' and data['aspect_type'] in ['create', 'update']:
            append_to_spreadsheet_from_object_id(data['object_id'])

        response_status_code = 200

    except Exception as e:
        current_app.logger.exception(
            f'Erro ao lidar com os dados enviados ao webhook.\n{data}')
        response_status_code = 400

    return '', response_status_code


@webhook_bp.route('/new_activity/<id>')
def append_activity(id):
    try:
        row = append_to_spreadsheet_from_object_id(id)
        return row, 200
    except Exception as e:
        current_app.logger.exception(
            'Erro ao recuperar dados de uma atividade atraves de uma URL')
        return '', 400
