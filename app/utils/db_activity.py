from app import db
from app.models import Activity, ActivityState, User
from app.utils.strava.response import StravaResponse


def get_activity(strava_id: str) -> Activity:
    activity: Activity = db.session.execute(
        db.select(Activity).filter_by(strava_id=strava_id)
    ).scalar_one()
    return activity


def get_activity_or_none(strava_id: str) -> Activity | None:
    activity: Activity | None = db.session.execute(
        db.select(Activity).filter_by(strava_id=strava_id)
    ).scalar_one_or_none()
    return activity


def get_activity_state(desc: str) -> ActivityState:
    state = db.session.execute(
        db.select(ActivityState).filter_by(description=desc)
    ).scalar_one()
    return state


def add_to_db(strava_response: StravaResponse, desc: str, user: User):
    strava_id = strava_response.JSON['id']
    activity = get_activity_or_none(strava_id)

    if not activity:
        state_str = 'Criado' if strava_response.OK else 'Aguardando dados'
        state = get_activity_state(state_str)

        activity = Activity(
            strava_id = strava_id,
            type = strava_response.JSON.get('type'),
            desc = desc,
            state = state,
            user = user,
            fc_max = strava_response.JSON.get('max_heartrate'),
            fc_avg = strava_response.JSON.get('average_heartrate'),
            elevation = strava_response.JSON.get('total_elevation_gain')
        )
        db.session.add(activity)
    else:
        state = get_activity_state('Restaurado')
        activity.type = strava_response.JSON.get('type')
        activity.state = state
        activity.last_update_desc = desc
        if activity.user_id != user.strava_id:
            activity.user = user


def update_db(strava_response: StravaResponse, desc: str, user: User):
    state = get_activity_state('Atualizado')

    activity = get_activity(strava_response.JSON['id'])
    activity.type = strava_response.JSON.get('type')
    activity.last_update_desc = desc
    activity.state = state
    activity.user = user
    activity.fc_max = strava_response.JSON.get('max_heartrate')
    activity.fc_avg = strava_response.JSON.get('average_heartrate')
    activity.elevation = strava_response.JSON.get('total_elevation_gain')


def delete_db(strava_id: str, desc: str):
    state = get_activity_state('Excluido')

    activity = get_activity_or_none(strava_id)

    if activity:
        activity.last_update_desc = desc
        activity.state = state
