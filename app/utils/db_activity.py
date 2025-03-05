from app import db
from app.models import Activity, ActivityState


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


def add_to_db(ok: bool, strava_id: str, desc: str):
    activity = get_activity_or_none(strava_id)

    if not activity:
        state_str = 'Criado' if ok else 'Aguardando dados'
        state = get_activity_state(state_str)

        activity = Activity(strava_id, desc, state)
        db.session.add(activity)
    else:
        state = get_activity_state('Restaurado')
        activity.state = state
        activity.last_update_desc = desc


def update_db(strava_id: str, desc: str):
    state = get_activity_state('Atualizado')

    activity = get_activity(strava_id)
    activity.last_update_desc = desc
    activity.state = state


def delete_db(strava_id: str, desc: str):
    state = get_activity_state('Excluido')

    activity = get_activity_or_none(strava_id)

    if activity:
        activity.last_update_desc = desc
        activity.state = state
