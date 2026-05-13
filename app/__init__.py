from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.routes import tasks_bp
    app.register_blueprint(tasks_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"Error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"Error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"Error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()

    return app