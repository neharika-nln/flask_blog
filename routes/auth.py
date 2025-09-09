from flask import Blueprint, request, jsonify
from models import User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from extensions import db, bcrypt, jwt_blocklist

bcrypt = Bcrypt()
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Check if email already exists
    existing_email = User.query.filter_by(email=data["email"]).first()
    if existing_email:
        return jsonify({"error": "Email already registered"}), 400

    # Check if username already exists
    existing_username = User.query.filter_by(username=data["username"]).first()
    if existing_username:
        return jsonify({"error": "Username already taken"}), 400


    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    # Create new user
    new_user = User(
        username=data["username"],
        name=data["name"],
        email=data["email"],
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user:
        return jsonify({"message":"User not found!"}),401
    if not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"message":"Wrong password!"}),401
    if user and bcrypt.check_password_hash(user.password, data["password"]):
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token,"name":user.name,"user_id":user.id,"message":"Login successful"}), 200
    # return jsonify({"error": "Wrong password!"}), 401

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # token’s unique ID
    jwt_blocklist.add(jti)  # add it to the blocklist
    return jsonify({"message": "Logged out successfully"}), 200