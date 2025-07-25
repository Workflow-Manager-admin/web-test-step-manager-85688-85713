from flask import Flask
from flask_cors import CORS
from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.steps import blp as steps_blp
from .routes.suites import blp as suites_blp
from flask_smorest import Api
from .models import db

import os

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["API_TITLE"] = "My Flask API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# --- Persistence and Security config ---
# Example envs: DATABASE_URL, SECRET_KEY. Provide development defaults.
db_url = os.environ.get("DATABASE_URL") or "sqlite:///test_step_backend.db"
secret = os.environ.get("SECRET_KEY") or "dev_secret"
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret

db.init_app(app)


api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(steps_blp)
api.register_blueprint(suites_blp)
