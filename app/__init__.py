from logging.config import dictConfig
from app.utils import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)

from os import getenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(getenv('CONFIG'))
    app.debug = False
    app.secret_key = app.config['SECRET_KEY']

    # Inicializa o banco de dados
    db.init_app(app)

    # Importa e registra os blueprints
    from app.blueprints import auth_bp, webhook_bp
    from app.utils.strava.api import call

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return 'Oi!'

    @app.route('/success')
    def login_success():
        app.logger.info('Novo login!')
        return 'Login realizado com sucesso!\nPode fechar essa janela.'

    @app.route('/activity/<id>')
    def activity(id):
        try:
            response = call(f'/activities/{id}', id)
            return response.JSON
        except Exception as e:
            msg = f'Erro ao solicitar dados da atividade: {repr(e)}'
            app.logger.exception(msg)
            resp = {'message': msg}
            return resp, 400

    return app
