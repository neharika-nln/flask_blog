import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://blog_user:blog123@localhost:5432/blog_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)
    JWT_SECRET_KEY = os.urandom(24)
    JWT_ACCESS_TOKEN_EXPIRES = False
