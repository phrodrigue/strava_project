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
