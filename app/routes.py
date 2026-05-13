from flask import Blueprint, jsonify, request
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
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks])

@tasks_bp.route('/tasks', methods=['POST'])
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
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({"Error": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"Message": "Task deleted"}), 200

@tasks_bp.route('/tasks/<int:id>', methods=['PUT'])
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