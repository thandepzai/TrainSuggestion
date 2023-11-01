from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_pyfile('config.py')

    from app.routes import bp
    app.register_blueprint(bp)

    return app