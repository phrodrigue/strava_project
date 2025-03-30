from app import db
from app.models import User


def get_user_or_none(strava_id: str) -> User | None:
    user = db.session.execute(
        db.select(User).filter_by(strava_id=strava_id)
    ).scalar_one_or_none()
    return user


def get_user(strava_id: str) -> User:
    user = db.session.execute(
        db.select(User).filter_by(strava_id=strava_id)
    ).scalar_one()
    return user


def add_user_to_db(user_data: dict):
    user = get_user_or_none(user_data['id'])

    if not user:
        user = User(
            strava_id=user_data['id'],
            name=user_data['firstname'],
            lastname=user_data['lastname']
        )

        db.session.add(user)
        db.session.commit()
    
    return user
