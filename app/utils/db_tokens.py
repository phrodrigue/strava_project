from flask import current_app

from app import db
from app.models import Token
from app.models.user import User


def get_tokens(user: User) -> Token | None:
    token = db.session.execute(
        db.select(Token).filter_by(user_id=user.strava_id)
    ).scalar_one_or_none()
    return token


def save_tokens(user: User, access_token: str, refresh_token: str, expires_at: int):
    """Salva ou atualiza os tokens no banco de dados."""
    token = get_tokens(user)

    if token:
        # Atualiza o token existente
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.expires_at = expires_at
    else:
        # Cria um novo token
        token = Token(
            user_id=user.strava_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            user = user
        )
        db.session.add(token)
    db.session.commit()
