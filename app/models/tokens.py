from datetime import datetime

from app import db


class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(16), nullable=False)  # ID do usuário
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)  # Timestamp de expiração
    created_at = db.Column(db.DateTime, default=datetime.now)  # Data de criação
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # Data de atualização

    def __init__(self, user_id, access_token, refresh_token, expires_at) -> None:
        super().__init__()
        self.user_id=user_id
        self.access_token=access_token
        self.refresh_token=refresh_token
        self.expires_at=expires_at

    def __repr__(self):
        return f"<Token user_id={self.user_id}, access_token={self.access_token}>"
