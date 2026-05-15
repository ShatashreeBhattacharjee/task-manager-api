import re
from flask import Blueprint,jsonify,request
from flask_jwt_extended import create_access_token
from app import db
from app.models import User


auth_bp=Blueprint('auth',__name__)
@auth_bp.route('/register',methods=['POST'])
def register():
    data=request.get_json(silent=True)
    if not data or "username" not in data or "password" not in data:
        return jsonify({"Error": "Username and password required"}), 400
    if not isinstance(data["username"],str) or not data["username"].strip():
        return jsonify({"Error": "Username must be a non-empty string"}), 400
    if not isinstance(data["password"],str):
        return jsonify({"Error": "Password must be a string"}), 400
    password=data["password"]
    if len(password)<8:
        return jsonify({"Error": "Password must be 8 characters long"}), 400
    if not re.search(r'[A-Z]',password):
        return jsonify({"Error": "Password must have at least one uppercase letter"}), 400
    if not re.search(r'[a-z]',password):
        return jsonify({"Error": "Password must have at least one lowercase letter"}), 400
    if not re.search(r'[0-9]', password):
        return jsonify({"Error": "Password must have at least one number"}), 400
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return jsonify({"Error": "Password must have at least one special character"}), 400
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"Error": "Username already exists"}), 409
    user=User()
    user.username=data["username"]
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message": "User registered successfully", "user": user.to_dict()}), 201

@auth_bp.route('/login',methods=['POST'])
def login():
    data=request.get_json(silent=True)
    if not data or "username" not in data or "password" not in data:
        return jsonify({"Error": "Username and password required"}), 400
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"Error": "Invalid username or password"}), 401
    token=create_access_token(identity=str(user.id))
    return jsonify({"Message": "Login successful", "token": token}), 200
