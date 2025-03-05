from datetime import datetime

from flask import current_app
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app import db
from app.models import ActivityState


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    strava_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    last_update_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    state_id: Mapped['int'] = mapped_column(ForeignKey('activity_states.id'), nullable=False)

    state = relationship('ActivityState', back_populates='activities')

    def __init__(self, strava_id: str, desc: str, state: ActivityState) -> None:
        super().__init__()
        self.strava_id = strava_id
        self.last_update_desc = desc
        self.state = state

    def __repr__(self):
        return f'<Activity {self.strava_id}>'
