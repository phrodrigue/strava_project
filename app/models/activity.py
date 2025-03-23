from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Double
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app import db
from app.models import ActivityState
from app.models import User


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    strava_id: Mapped[str] = mapped_column(String(16), unique=True)
    type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fc_max: Mapped[float | None] = mapped_column(Double, nullable=True)
    fc_avg: Mapped[float | None] = mapped_column(Double, nullable=True)
    elevation: Mapped[float | None] = mapped_column(Double, nullable=True)
    last_update_desc: Mapped[str] = mapped_column(String(32))
    creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    state_id: Mapped[int] = mapped_column(ForeignKey('activity_states.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    state = relationship('ActivityState', back_populates='activities')
    user = relationship('User', back_populates='activities')

    def __init__(
            self, 
            strava_id: str,
            type: str | None,
            desc: str, 
            state: ActivityState, 
            user: User,
            fc_max: float | None = None,
            fc_avg: float | None = None,
            elevation: float | None = None

        ) -> None:
        super().__init__()
        self.strava_id = strava_id
        self.type = type
        self.last_update_desc = desc
        self.state = state
        self.user = user
        self.fc_max = fc_max
        self.fc_avg = fc_avg
        self.elevation = elevation

    def __repr__(self):
        return f'<Activity {self.strava_id}>'
