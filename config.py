from os import getenv


class Config:
    SECRET_KEY = getenv('SECRET_KEY')
    CLIENT_ID = getenv('CLIENT_ID')
    CLIENT_SECRET = getenv('CLIENT_SECRET')

    REDIRECT_URI = getenv('REDIRECT_URI')
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    USER_ID = getenv('USER_ID')
    API_URL = 'https://www.strava.com/api/v3'

    SPREADSHEET_KEY = getenv('SPREADSHEET_KEY')


class ProdConfig(Config):
    pass


class DevConfig(Config):
    pass
