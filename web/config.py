import os

basedir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(basedir)  # Поднимаемся на уровень выше
db_path = os.path.join(base_dir, 'bot', 'climate_poll.db')

SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'your-secret-key-here'