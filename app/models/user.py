from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class User(db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    strava_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(16))
    lastname: Mapped[str] = mapped_column(String(32))

    activities = relationship('Activity', back_populates='user')
    tokens = relationship('Token', back_populates='user')

    def __init__(self, strava_id: str, name: str, lastname: str) -> None:
        super().__init__()
        self.strava_id = strava_id
        self.name = name
        self.lastname = lastname

    def __repr__(self):
        return f'<User {self.name} ({self.strava_id})>'
