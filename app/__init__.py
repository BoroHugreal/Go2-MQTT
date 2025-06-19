# app/__init__.py
from flask import Flask
from .main import bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.register_blueprint(bp)
    return app
