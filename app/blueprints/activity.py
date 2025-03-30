from flask import Blueprint, current_app
from flask_jwt_extended import current_user, jwt_required

from app import db
from app.utils import create_response
from app.utils.db_activity import add_to_db, delete_db, get_activity_or_none, update_db
from app.utils.exceptions import DeletedActivityException, SportNotAllowedException
from app.utils.spreadsheet import delete_in_spreadsheet, update_in_spreadsheet, append_to_spreadsheet
from app.utils.strava.api import call

activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/')
@activity_bp.route('/<strava_id>')
@jwt_required()
def get(strava_id=None):
    if not strava_id:
        return create_response('Atividade invalida.', 400)

    try:
        response = call(f'/activities/{strava_id}', strava_id, current_user, only_search=True)
        return create_response({'info': 'Atividade encontrada.', 'data': response.JSON})

    except Exception as e:
        msg = f'Erro ao solicitar dados da atividade: {e}'
        current_app.logger.exception(msg)
        return create_response(f'{e}', 400)


@activity_bp.route('/sync/')
@activity_bp.route('/sync/<strava_id>')
@jwt_required()
def sync(strava_id=None):
    if not strava_id:
        return create_response('Atividade invalida.', 400)

    try:
        strava_response = call(f"/activities/{strava_id}", strava_id, current_user)

        db_activity = get_activity_or_none(strava_id)

        if not db_activity:
            append_to_spreadsheet(strava_response, strava_id)
            add_to_db(strava_response, 'criada pela url', current_user)
            info = 'Atividade criada!'

        elif db_activity.state.description == 'Excluido':
            append_to_spreadsheet(strava_response, strava_id)
            add_to_db(strava_response, 'restaurada pela url', current_user)
            info = 'Atividade restaurada.'
    
        else:
            # state in ['Criado', 'Atualizado', 'Restaurado', 'Aguardando dados']
            update_in_spreadsheet(strava_response, strava_id)
            update_db(strava_response, 'atualizada pela url', current_user)
            info = 'Atividade atualizada.'

    except SportNotAllowedException as e:
        db.session.rollback()
        return create_response(e.message, 400)
    
    except DeletedActivityException as e:
        delete_in_spreadsheet(strava_id)
        delete_db(strava_id, 'excluida pela url')
        db.session.commit()
        return create_response(e.message, 400)

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception(
            f'Erro ao recuperar dados de uma atividade atraves de uma URL')
        return create_response('Nao foi possivel incluir atividade.', 400)
    
    else:
        db.session.commit()
        return create_response({'info': info, 'data': strava_response.JSON})
