from logging.config import dictConfig
from app.utils.logging import LOGGING_CONFIG
dictConfig(LOGGING_CONFIG)

from os import getenv

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

from app.utils import create_response

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(getenv('CONFIG'))

    # Inicializa o banco de dados
    db.init_app(app)
    migrate.init_app(app, db)

    # Importa e registra os blueprints
    from app.blueprints import activity_bp
    from app.blueprints import auth_bp
    from app.blueprints import webhook_bp

    app.register_blueprint(activity_bp, url_prefix='/activity')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')

    with app.app_context():
        db.create_all()
        from app.models.activities import inicialize_activity_state_db
        inicialize_activity_state_db()

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        response = e.get_response()
        if e.code < 400:
            return response

        data = {
            "error": e.name,
            "description": e.description,
        }
        return create_response(data, e.code)

    @app.route('/')
    def index():
        return create_response('Oi!', 200)

    return app
