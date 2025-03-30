from flask import current_app
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db


class ActivityState(db.Model):
    __tablename__ = 'activity_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(50))

    activities = relationship('Activity', back_populates='state')
    
    def __init__(self, description) -> None:
        super().__init__()
        self.description = description

    def __repr__(self):
        return f'<ActivityState {self.description}>'
