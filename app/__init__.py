from logging.config import dictConfig
from app.utils.logging import LOGGING_CONFIG
dictConfig(LOGGING_CONFIG)

from os import getenv

from flask import Flask, redirect, render_template, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from werkzeug.exceptions import HTTPException

from app.utils import create_response

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=convention))
migrate = Migrate(render_as_batch=True)
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(getenv('CONFIG'))

    from app.utils.db_user import get_user_or_none
    
    # cria a identidade a partir de um User model
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.strava_id
    
    # retorna um User model a partir de uma identidade
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return get_user_or_none(identity)

    # Inicializa o banco de dados
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Importa e registra os blueprints
    from app.blueprints import activity_bp
    from app.blueprints import auth_bp
    from app.blueprints import webhook_bp
    from app.blueprints import cli

    app.register_blueprint(activity_bp, url_prefix='/activity')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    app.cli.add_command(cli)

    @app.shell_context_processor
    def make_shell_context():
        return {
            'execute': db.session.execute,
            'select': db.select
        }

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
    @app.route('/<int:strava_id>')
    def index(strava_id=None):
        next = request.args.get('next')
        if next:
            return redirect(next)

        id = strava_id if strava_id else ''
        return render_template('index.html', strava_id=id)

    return app
