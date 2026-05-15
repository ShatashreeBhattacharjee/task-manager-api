from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required
from app import db
from app.models import Task

tasks_bp = Blueprint('tasks', __name__)

def validate_done_field(value):
    if not isinstance(value, bool):
        return False, "done must be a boolean (true or false)"
    return True, None

@tasks_bp.route('/')
def home():
    return jsonify({"Message": "API is running"})

@tasks_bp.route('/tasks', methods=['GET'])
def all_get_tasks():
    done_param=request.args.get('done')
    sort_by=request.args.get('sort_by','created_at')
    order=request.args.get('order','asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 1, type=int)

    allowed_sort_fields = {
        'created_at': Task.created_at,
        'updated_at': Task.updated_at,
        'task': Task.task,
        'done': Task.done
    }

    if sort_by not in allowed_sort_fields:
        return jsonify({"Error": "sort_by must be one of: created_at, updated_at, task, done"}), 400
    if order not in ['asc','desc']:
        return jsonify({"Error": "order must be 'asc' or 'desc'"}), 400
    if page < 1:
        return jsonify({"Error": "page must be greater than 0"}), 400
    if per_page < 1 or per_page > 100:
        return jsonify({"Error": "per_page must be between 1 and 100"}), 400
    sort_column=allowed_sort_fields[sort_by]
    if order=='desc':
        sort_column=sort_column.desc()
    if done_param is not None:
        if done_param.lower()=='true':
            query=Task.query.filter_by(done=True).all()
        elif done_param.lower()=='false':
            query=Task.query.filter_by(done=False).all()
        else:
            return jsonify({"Error": "done must be 'true' or 'false'"}),400
    else:
        query = Task.query
    paginated = query.order_by(sort_column).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "tasks": [t.to_dict() for t in paginated.items],
        "total": paginated.total,
        "page": paginated.page,
        "per_page": paginated.per_page,
        "total_pages": paginated.pages
    })

@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def add_task():
    data = request.get_json(silent=True)
    if not data or "task" not in data:
        return jsonify({"Error": "Task not provided"}), 400
    if not isinstance(data["task"], str) or not data["task"].strip():
        return jsonify({"Error": "Task must be a non-empty string"}), 400
    if "done" in data:
        valid, msg = validate_done_field(data["done"])
        if not valid:
            return jsonify({"Error": msg}), 400
    new_task = Task(task=data["task"].strip())
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@tasks_bp.route('/tasks/bulk', methods=['POST'])
@jwt_required()
def add_task_in_bulk():
    data = request.get_json(silent=True)
    if not data or "tasks" not in data:
        return jsonify({"Error": "Tasks list not provided"}), 400
    if not isinstance(data["tasks"], list):
        return jsonify({"Error": "Tasks must be a list"}), 400
    if len(data["tasks"]) == 0:
        return jsonify({"Error": "Task list is empty"}), 400
    added, skipped = [], []
    for t in data["tasks"]:
        if not isinstance(t, str) or not t.strip():
            skipped.append(t)
            continue
        new_task = Task(task=t.strip())
        db.session.add(new_task)
        added.append(new_task)
    db.session.commit()
    return jsonify({
        "Message": f"{len(added)} task(s) added",
        "added": [t.to_dict() for t in added],
        "skipped": skipped
    }), 201

@tasks_bp.route('/tasks/<int:id>', methods=['GET'])
def get_single_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"Error": "Task not found"}), 404
    return jsonify(task.to_dict()), 200

@tasks_bp.route('/tasks/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"Error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"Message": "Task deleted"}), 200

@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
@jwt_required()
def update_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"Error": "Task not found"}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"Error": "No data provided"}), 400
    if "task" in data:
        if not isinstance(data["task"], str) or not data["task"].strip():
            return jsonify({"Error": "Task must be a non-empty string"}), 400
        task.task = data["task"].strip()
    if "done" in data:
        valid, msg = validate_done_field(data["done"])
        if not valid:
            return jsonify({"Error": msg}), 400
        task.done = data["done"]
    db.session.commit()
    return jsonify({"Message": "Task updated successfully", "task": task.to_dict()}), 200