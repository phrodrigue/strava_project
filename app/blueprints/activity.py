from flask import Blueprint, current_app

from app import db
from app.utils import create_response
from app.utils.db_activity import add_to_db, delete_db, get_activity_or_none, update_db
from app.utils.exceptions import DeletedActivityException, SportNotAllowedException
from app.utils.spreadsheet import delete_in_spreadsheet, update_in_spreadsheet, append_to_spreadsheet
from app.utils.strava.api import call

activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/<strava_id>')
def get(strava_id):
    try:
        response = call(f'/activities/{strava_id}', strava_id, only_search=True)
        return create_response(response.JSON, 200)

    except Exception as e:
        msg = f'Erro ao solicitar dados da atividade: {e}'
        current_app.logger.exception(msg)
        return create_response(msg, 400)


@activity_bp.route('/sync/<strava_id>')
def sync(strava_id):
    try:
        strava_response = call(f"/activities/{strava_id}", strava_id)

        db_activity = get_activity_or_none(strava_id)

        if not db_activity:
            row = append_to_spreadsheet(strava_response, strava_id)
            add_to_db(strava_response.OK, strava_id, 'criada pela url')
            info = 'Atividade criada!'

        elif db_activity.state.description == 'Excluido':
            row = append_to_spreadsheet(strava_response, strava_id)
            add_to_db(strava_response.OK, strava_id, 'restaurada pela url')
            info = 'Atividade restaurada.'
    
        else:
            # state in ['Criado', 'Atualizado', 'Restaurado', 'Aguardando dados']
            row = update_in_spreadsheet(strava_response, strava_id)
            update_db(strava_id, 'atualizada pela url')
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
        return create_response({'info': info, 'row': row}, 200)
