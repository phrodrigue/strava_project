from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class Token(db.Model):
    __tablename__ = 'tokens'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(16), nullable=False)  # ID do usuário
    access_token: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[int] = mapped_column(nullable=False)  # Timestamp de expiração
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())  # Data de criação
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # Data de atualização
    _user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship('User', back_populates='tokens')

    def __init__(self, user_id, access_token, refresh_token, expires_at, user) -> None:
        super().__init__()
        self.user_id=user_id
        self.access_token=access_token
        self.refresh_token=refresh_token
        self.expires_at=expires_at
        self.user = user

    def __repr__(self):
        return f"<Token user_id={self.user.strava_id}, access_token={self.access_token}>"
