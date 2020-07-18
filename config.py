import os
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

IMAGE_UPLOADS = os.path.join(basedir, "static", "img")
ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF"]
POSTGRES_URL = "127.0.0.1:5432"
POSTGRES_USER = "postgres"
POSTGRES_PW = "monem0006"
POSTGRES_DB = "fyyur"
SQLALCHEMY_DATABASE_URI   = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
SECRET_KEY = 'samman'
SQLALCHEMY_TRACK_MODIFICATIONS = False

