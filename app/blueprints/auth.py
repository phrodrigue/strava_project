from flask import Blueprint, current_app, redirect, request, url_for

from app.utils import create_response, generate_auth_url
from app.utils.strava.tokens import get_new_token, refresh_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def login():
    return redirect(generate_auth_url())


@auth_bp.route('/success')
def login_success():
    current_app.logger.info('Novo login!')
    return create_response('Login realizado com sucesso!\nPode fechar essa janela.', 200)


@auth_bp.route('/callback/<path:next>')
def callback(next=None):
    code = request.args.get('code')
    if not code:
        msg = "Codigo de autorizacao nao recebido."
        current_app.logger.error(f'{msg}: {request.url}')
        return create_response(msg, 400)

    token_created = get_new_token(code)
    if not token_created:
        return create_response("Erro ao obter tokens.", 400)

    if next:
        return redirect(next)

    return redirect(url_for('auth.login_success'))


@auth_bp.route('/refresh_token')
def refresh_token_route():
    refreshed = refresh_token()

    if not refreshed:
        return create_response("Erro ao renovar o token.", 400)

    return redirect(url_for('auth.login_success'))
