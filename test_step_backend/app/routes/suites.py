from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, jsonify
from ..models import db, StepSuite
from ..auth import login_required

blp = Blueprint("Suites", "suites", url_prefix="/suites", description="Manage test step suites (grouping)")


@blp.route("/")
class SuitesList(MethodView):
    decorators = [login_required]
    # PUBLIC_INTERFACE
    def get(self):
        """
        List all suites for a user.
        """
        user = request.user
        suites = StepSuite.query.filter_by(user_id=user.id).all()
        result = []
        for s in suites:
            result.append({
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "created_at": s.created_at.isoformat(),
                "step_count": len(s.steps)
            })
        return {"suites": result}

    # PUBLIC_INTERFACE
    def post(self):
        """
        Create a new suite.
        JSON: name, description
        """
        user = request.user
        data = request.get_json()
        name = data.get("name")
        description = data.get("description", "")
        if not name:
            return jsonify({"message": "Name required"}), 400
        suite = StepSuite(name=name, description=description, user_id=user.id)
        db.session.add(suite)
        db.session.commit()
        return jsonify({
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "created_at": suite.created_at.isoformat()
        }), 201


@blp.route("/<int:suite_id>")
class SuiteItem(MethodView):
    decorators = [login_required]

    # PUBLIC_INTERFACE
    def get(self, suite_id):
        """
        Get suite details and its steps.
        """
        user = request.user
        suite = StepSuite.query.filter_by(id=suite_id, user_id=user.id).first()
        if not suite:
            return jsonify({"message": "Suite not found"}), 404
        steps = [{
            "id": s.id,
            "title": s.title,
            "order": s.order,
            "created_at": s.created_at.isoformat()
        } for s in suite.steps]
        return {
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "created_at": suite.created_at.isoformat(),
            "steps": steps
        }

    # PUBLIC_INTERFACE
    def put(self, suite_id):
        """
        Update suite name or description.
        JSON: name, description
        """
        user = request.user
        suite = StepSuite.query.filter_by(id=suite_id, user_id=user.id).first()
        if not suite:
            return jsonify({"message": "Suite not found"}), 404
        data = request.get_json()
        if "name" in data:
            suite.name = data["name"]
        if "description" in data:
            suite.description = data["description"]
        db.session.commit()
        return jsonify({"message": "Suite updated"})

    # PUBLIC_INTERFACE
    def delete(self, suite_id):
        """
        Delete a suite (and cascade delete steps).
        """
        user = request.user
        suite = StepSuite.query.filter_by(id=suite_id, user_id=user.id).first()
        if not suite:
            return jsonify({"message": "Suite not found"}), 404
        db.session.delete(suite)
        db.session.commit()
        return jsonify({"message": "Suite deleted"})
