import os

DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_SECRET_KEY = os.environ[
    "JWT_SECRET_KEY"
]  # We want the app to fail if the JWT SECRET_KEY is not valid
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
APP_SECRET_KEY = os.environ["APP_SECRET_KEY"]
UPLOADED_IMAGES_DEST = os.path.join("static", "images")
