from envparse import env
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = BASE_DIR.joinpath('.env')
if ENV_FILE_PATH.is_file():
    env.read_envfile(path=ENV_FILE_PATH)

TG_TOKEN = env.str('TG_TOKEN')
API_URL = env.str('API_URL')
users = {}