from os import getenv


class Config:
    # app
    SECRET_KEY = getenv('SECRET_KEY')
    # banco de dados
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # API strava
    CLIENT_ID = getenv('CLIENT_ID')
    CLIENT_SECRET = getenv('CLIENT_SECRET')
    REDIRECT_URI = getenv('REDIRECT_URI')
    API_URL = 'https://www.strava.com/api/v3'
    # planilha
    SPREADSHEET_KEY = getenv('SPREADSHEET_KEY')
    # outros
    USER_ID = getenv('USER_ID')
    ALLOWED_SPORTS = ['Ride', 'Run', 'Workout']


class ProdConfig(Config):
    pass


class DevConfig(Config):
    pass
