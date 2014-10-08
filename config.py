import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = '_flasktaskr.db'
USERNAME = 'admin'
PASSWORD = 'admin'
WTF_CSRF_ENABLED = True
SECRET_KEY = '4afc3bea-4efe-11e4-9c23-1c3e84e3d31b'

DATABASE_PATH = os.path.join(BASE_DIR, DATABASE)

#database URI - for SQLAlchemy
SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_PATH
