from flask import Blueprint, current_app, request

from app import db
from app.utils import create_response
from app.utils.db_activity import add_to_db, delete_db, get_activity_or_none, update_db
from app.utils.decorators import time_it
from app.utils.exceptions import SportNotAllowedException
from app.utils.spreadsheet import delete_in_spreadsheet, update_in_spreadsheet, append_to_spreadsheet
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
@webhook_bp.route('/', methods=['POST'])
@time_it
def webhook_event():
    ok_response = create_response('', 200)

    data = request.get_json()

    if data['object_type'] != 'activity':
        return ok_response

    try:
        strava_id = data['object_id']

        activity = get_activity_or_none(strava_id)
        if data['aspect_type'] == 'create' and activity and activity.state.description in ['Criado', 'Atualizado', 'Restaurado']:
            return ok_response

        if data['aspect_type'] == 'delete':
            delete_in_spreadsheet(strava_id)

            if activity:
                delete_db(strava_id, 'deletada pelo webhook')
                db.session.commit()

            return ok_response

        strava_response = call(f"/activities/{strava_id}", strava_id)

        if data['aspect_type'] == 'create':
            action = 'criada' if not activity else 'restaurada'
            append_to_spreadsheet(strava_response, strava_id)
            add_to_db(strava_response.OK, strava_id, f'{action} pelo webhook')

        elif data['aspect_type'] == 'update' and 'title' in data['updates'].keys():
            update_in_spreadsheet(strava_response, strava_id)
            update_db(strava_id, 'atualizada pelo webhook')

    except SportNotAllowedException as e:
        # indica que foi processado mas o esporte não interessa. nao precisa de outra chamada
        db.session.rollback()
        current_app.logger.error(
            f'Tentativa de adicionar um esporte nao permitido.\n{e.message}')
        return ok_response

    except Exception as e:
        # indica um erro desconhecido. precisa de outra chamada
        db.session.rollback()
        current_app.logger.exception(
            f'Erro ao lidar com os dados enviados ao webhook.\n{data}')
        return create_response('', 400)
    
    else:
        db.session.commit()
        return ok_response
