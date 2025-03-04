from datetime import datetime
from typing import List

from flask import current_app
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app import db


class ActivityState(db.Model):
    __tablename__ = 'activity_states'

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(50))

    activities: Mapped[List['Activity']] = relationship(back_populates='state')
    
    def __init__(self, description) -> None:
        super().__init__()
        self.description = description

    def __repr__(self):
        return f'<ActivityState {self.description}>'


class Activity(db.Model):
    __tablename__ = 'activities'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    strava_id: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    last_update_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    creation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_update_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    state_id: Mapped['int'] = mapped_column(ForeignKey('activity_states.id'), nullable=False)

    state: Mapped['ActivityState'] = relationship(back_populates='activities')

    def __init__(self, strava_id: str, desc: str, state: ActivityState) -> None:
        super().__init__()
        self.strava_id = strava_id
        self.last_update_desc = desc
        self.state = state

    def __repr__(self):
        return f'<Activity {self.strava_id}>'


def inicialize_activity_state_db():
    states = [
        'Criado',           # nova entrada
        'Atualizado',       # atualizado
        'Excluido',         # excluido
        'Aguardando dados', # houve um erro na inclusao, aguardando novos dados
        'Restaurado',       # foi excluido e restaurado
    ]
    for state in states:
        db_state = db.session.execute(
            db.select(ActivityState).filter_by(description=state)
        ).scalar_one_or_none()
        if not db_state:
            activity_state = ActivityState(description=state)
            db.session.add(activity_state)
            current_app.logger.info(f'Estado [{state}] adicionado ao banco de dados')
    db.session.commit()
