from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, jsonify
from sqlalchemy import or_
from ..models import db, TestStep
from ..auth import login_required

blp = Blueprint("TestSteps", "test_steps", url_prefix="/steps", description="CRUD, search/filter, and suite grouping for Test Steps")


@blp.route("/")
class StepsList(MethodView):
    decorators = [login_required]

    # PUBLIC_INTERFACE
    def get(self):
        """
        List and filter test steps.
        Query params: suite_id, q (search), order, page, per_page
        """
        user = request.user
        suite_id = request.args.get("suite_id", type=int)
        search = request.args.get("q", type=str)
        order = request.args.get("order", type=str)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        query = TestStep.query.filter_by(user_id=user.id)
        if suite_id:
            query = query.filter_by(suite_id=suite_id)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    TestStep.title.ilike(search_pattern),
                    TestStep.description.ilike(search_pattern),
                )
            )
        if order == "desc":
            query = query.order_by(TestStep.created_at.desc())
        else:
            query = query.order_by(TestStep.created_at.asc())

        steps = query.paginate(page=page, per_page=per_page, error_out=False)
        result = [{
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "order": s.order,
            "suite_id": s.suite_id,
            "created_at": s.created_at.isoformat()
        } for s in steps.items]
        return {
            "steps": result,
            "total": steps.total,
            "page": steps.page,
            "pages": steps.pages
        }

    # PUBLIC_INTERFACE
    def post(self):
        """
        Create a new test step.
        JSON: title, description, order, suite_id
        """
        user = request.user
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        order = data.get("order", 0)
        suite_id = data.get("suite_id")
        if not title or suite_id is None:
            return jsonify({"message": "Title and suite_id required"}), 400
        step = TestStep(
            title=title,
            description=description,
            order=order,
            suite_id=suite_id,
            user_id=user.id
        )
        db.session.add(step)
        db.session.commit()
        return jsonify({
            "id": step.id,
            "title": step.title,
            "description": step.description,
            "order": step.order,
            "suite_id": step.suite_id,
            "created_at": step.created_at.isoformat()
        }), 201


@blp.route("/<int:step_id>")
class StepItem(MethodView):
    decorators = [login_required]

    # PUBLIC_INTERFACE
    def get(self, step_id):
        """
        Retrieve details of a test step.
        """
        user = request.user
        step = TestStep.query.filter_by(id=step_id, user_id=user.id).first()
        if not step:
            return jsonify({"message": "Test step not found"}), 404
        return {
            "id": step.id,
            "title": step.title,
            "description": step.description,
            "order": step.order,
            "suite_id": step.suite_id,
            "created_at": step.created_at.isoformat()
        }

    # PUBLIC_INTERFACE
    def put(self, step_id):
        """
        Update a test step.
        JSON: title, description, order
        """
        user = request.user
        step = TestStep.query.filter_by(id=step_id, user_id=user.id).first()
        if not step:
            return jsonify({"message": "Test step not found"}), 404
        data = request.get_json()
        for field in ["title", "description", "order"]:
            if field in data:
                setattr(step, field, data[field])
        db.session.commit()
        return jsonify({"message": "Test step updated"})

    # PUBLIC_INTERFACE
    def delete(self, step_id):
        """
        Delete a test step.
        """
        user = request.user
        step = TestStep.query.filter_by(id=step_id, user_id=user.id).first()
        if not step:
            return jsonify({"message": "Test step not found"}), 404
        db.session.delete(step)
        db.session.commit()
        return jsonify({"message": "Test step deleted"})

