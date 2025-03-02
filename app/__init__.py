from logging.config import dictConfig
from app.utils.logging import LOGGING_CONFIG
dictConfig(LOGGING_CONFIG)

from app.utils import create_response
from os import getenv

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(getenv('CONFIG'))

    # Inicializa o banco de dados
    db.init_app(app)
    migrate.init_app(app, db)

    # Importa e registra os blueprints
    from app.blueprints import auth_bp, webhook_bp
    from app.utils.strava.api import call

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')

    with app.app_context():
        db.create_all()
        from app.models.atividades import inicialize_activity_state_db
        inicialize_activity_state_db()

    @app.route('/')
    def index():
        return create_response('Oi!', 200)


    @app.route('/activity/<id>')
    def activity(id):
        try:
            response = call(f'/activities/{id}', id, only_search=True)
            return create_response(response.JSON, 200)

        except Exception as e:
            msg = f'Erro ao solicitar dados da atividade: {repr(e)}'
            app.logger.exception(msg)
            return create_response(msg, 400)

    return app
