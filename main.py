from dotenv import load_dotenv
import os

root_path = str(os.path.abspath((os.path.dirname(__file__))))
load_dotenv(root_path + "/.env")

from app import create_app, db
from app.models import *
app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'ActivityState': ActivityState,
        'Activity': Activity,
        'Token': Token
    }
