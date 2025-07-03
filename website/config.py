import os

SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
