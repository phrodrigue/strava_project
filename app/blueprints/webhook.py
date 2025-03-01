from flask import Blueprint, current_app, request

from app.utils import create_response
from app.utils.decorators import time_it
from app.utils.exceptions import SportNotAllowedException
from app.utils.spreadsheet import update_spreadsheet, append_to_spreadsheet
from app.utils.strava.api import call

webhook_bp = Blueprint('webhook', __name__)


# Endpoint para validação do webhook
@webhook_bp.route('/', methods=['GET'])
def validate_webhook():
    challenge = request.args.get('hub.challenge')
    if challenge:
        current_app.logger.info('Teste de validacao de webhook realizado.')
    return create_response({'hub.challenge': challenge}, 200)


# Endpoint para receber eventos do webhook
@webhook_bp.route('', methods=['POST'])
@time_it
def webhook_event():
    ok_response = create_response('', 200)

    data = request.get_json()

    if data['object_type'] != 'activity':
        return ok_response

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

        return ok_response

    except SportNotAllowedException as e:
        # indica que foi processado mas o esporte não interessa. nao precisa de outra chamada
        current_app.logger.error(
            f'Tentativa de adicionar um esporte nao permitido.\n{e.message}')
        return ok_response

    except Exception as e:
        # indica um erro desconhecido. precisa de outra chamada
        current_app.logger.exception(
            f'Erro ao lidar com os dados enviados ao webhook.\n{data}')
        return create_response('', 400)


@webhook_bp.route('/new_activity/<id>')
@time_it
def append_activity(id):
    try:
        strava_response = call(f"/activities/{id}", id)
        row = append_to_spreadsheet(strava_response)
        return create_response(row, 200)

    except SportNotAllowedException as e:
        return create_response(e.message, 400)

    except Exception as e:
        current_app.logger.exception(
            f'Erro ao recuperar dados de uma atividade atraves de uma URL')
        return create_response('Nao foi possivel incluir atividade.', 400)
