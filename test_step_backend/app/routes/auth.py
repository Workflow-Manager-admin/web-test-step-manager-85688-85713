from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, jsonify
from ..models import db, User
from ..auth import generate_token

blp = Blueprint("Auth", "auth", url_prefix="/auth", description="User authentication")


@blp.route("/signup")
class Signup(MethodView):
    # PUBLIC_INTERFACE
    def post(self):
        """Register a new user account."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"message": "Username and password required"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 409
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created"}), 201


@blp.route("/login")
class Login(MethodView):
    # PUBLIC_INTERFACE
    def post(self):
        """User login, returns JWT on success."""
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"message": "Username and password required"}), 400
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            token = generate_token(user)
            return jsonify({"token": token}), 200
        return jsonify({"message": "Invalid credentials"}), 401
