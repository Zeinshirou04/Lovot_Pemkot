from flask import Flask
from Flask.blueprints.display import EyesBP

app = Flask(__name__)
app.register_blueprint(EyesBP)

def create_app():
    return app