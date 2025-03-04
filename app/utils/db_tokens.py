from flask import current_app

from app import db
from app.models import Token


def get_tokens(user_id: str) -> Token | None:
    token = db.session.execute(
        db.select(Token).filter_by(user_id=user_id)
    ).scalar_one_or_none()
    return token


def save_tokens(access_token, refresh_token, expires_at):
    """Salva ou atualiza os tokens no banco de dados."""
    user_id = current_app.config['USER_ID']

    token = get_tokens(user_id)

    if token:
        # Atualiza o token existente
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.expires_at = expires_at
    else:
        # Cria um novo token
        token = Token(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        db.session.add(token)
    db.session.commit()
