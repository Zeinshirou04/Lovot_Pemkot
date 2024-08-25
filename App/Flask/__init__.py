from flask import Flask
from Flask.blueprints.display import EyesBP

app = Flask(__name__)
app.register_blueprint(EyesBP)

if __name__ == '__main__':
    app.run(debug=True)