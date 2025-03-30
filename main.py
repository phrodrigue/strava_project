from dotenv import load_dotenv # type: ignore
import os

root_path = str(os.path.abspath((os.path.dirname(__file__))))
load_dotenv(root_path + "/.env")

from app import create_app

app = create_app()
