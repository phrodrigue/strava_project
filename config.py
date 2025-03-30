from datetime import timedelta
from os import getenv


class Config:
    # app
    SECRET_KEY = getenv('SECRET_KEY')
    SERVER_NAME = getenv('SERVER_NAME')
    # banco de dados
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # API strava
    CLIENT_ID = getenv('CLIENT_ID')
    CLIENT_SECRET = getenv('CLIENT_SECRET')
    REDIRECT_URI = getenv('REDIRECT_URI')
    API_URL = 'https://www.strava.com/api/v3'
    # JWT config
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # planilha
    SPREADSHEET_KEY = getenv('SPREADSHEET_KEY')
    # outros
    ALLOWED_SPORTS = ['Ride', 'Run', 'Workout']
    JSON_ACTIVITY_PATH = getenv('JSON_ACTIVITY_PATH')


class ProdConfig(Config):
    pass


class DevConfig(Config):
    pass
