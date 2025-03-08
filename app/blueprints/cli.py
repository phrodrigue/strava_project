from flask import Blueprint

from app import db
from app.models import User
from app.models import ActivityState

cli_bp = Blueprint('cli', __name__, cli_group=None)


@cli_bp.cli.command('populate')
def populate():
    """
    Cria os estados das atividades e o usuário padrão no banco de dados
    """
    print('Verificando estados...')
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
            print(f'Estado [{state.upper()}] adicionado ao banco de dados')

    print('Verificando usuário padrão...')
    user = db.session.execute(
        db.select(User).filter_by(strava_id='0')
    ).scalar_one_or_none()

    if not user:
        user = User('0', 'default', 'user')
        db.session.add(user)
        print(f'User [{user.name.upper()}] adicionado ao banco de dados')
    
    db.session.commit()
    print('Todas as entidades salvas no DB.')
