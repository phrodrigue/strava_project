from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, current_user, jwt_required

from app.utils import create_response, generate_auth_url
from app.utils.db_tokens import save_tokens
from app.utils.db_user import add_user_to_db
from app.utils.strava.tokens import get_new_token, refresh_token

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def login():
    next = request.args.get('next')
    return redirect(generate_auth_url(next=url_for('index', next=next)))


@auth_bp.route('/callback/')
def callback():
    code = request.args.get('code')
    if not code:
        msg = "Codigo de autorizacao nao recebido."
        current_app.logger.error(f'{msg}: {request.url}')
        return create_response(msg, 400)

    token_response = get_new_token(code)
    if not token_response:
        return create_response("Erro ao obter tokens.", 400)

    user = add_user_to_db(token_response['athlete'])
    save_tokens(
        user,
        token_response['access_token'],
        token_response['refresh_token'],
        token_response['expires_at']
    )
    jwt_access_token = create_access_token(identity=user)
    jwt_refresh_token = create_refresh_token(identity=user)

    next = request.args.get('next')

    return render_template(
        'login.html',
        jwt = jwt_access_token,
        refresh_token = jwt_refresh_token,
        next = next if next else '/'
    )


@auth_bp.route('/refresh_token')
@jwt_required()
def refresh_token_():
    '''View para dar o refresh token manualmente'''    
    new_tokens = refresh_token(current_user)

    if not new_tokens:
        return create_response("Erro ao renovar o token.", 400)

    save_tokens(
        user=current_user,
        access_token=new_tokens['access_token'],
        refresh_token=new_tokens['refresh_token'],
        expires_at=new_tokens['expires_at']
    )

    return create_response('Access Tokens do Strava renovado.')


@auth_bp.route("/refresh_jwt_token", methods=["POST"])
@jwt_required(refresh=True)
def refresh_jwt_token():
    access_token = create_access_token(identity=current_user)
    return create_response({'access_token': access_token})
