from flask import Blueprint, request, jsonify
import random
from datetime import datetime, timedelta
from models import User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from extensions import db, bcrypt, jwt_blocklist
from utils.send_email import send_otp_email

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

    if data["password"] == "":
        return jsonify({"error": "Password cannot be empty"}), 400
        
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
        token = create_access_token(identity=str(user.id))     # this creates the token
        return jsonify({"token": token,"name":user.name,"user_id":user.id,"message":"Login successful"}), 200
    # return jsonify({"error": "Wrong password!"}), 401

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # token’s unique ID
    jwt_blocklist.add(jti)  # add it to the blocklist
    return jsonify({"message": "Logged out successfully"}), 200

# Temporary store for OTPs (better to use Redis or DB for production)
otp_store = {}

# Step 1: Request OTP
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not registered"}), 404

    otp = str(random.randint(100000, 999999))
    otp_store[email] = {
        "otp": otp,
        "expires_at": datetime.now() + timedelta(minutes=10)
    }

    # Send OTP via SendGrid
    send_otp_email(email, otp)

    return jsonify({"message": "OTP sent to your email"}), 200

# Step 2: Verify OTP
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    record = otp_store.get(email)
    if not record:
        return jsonify({"error": "No OTP request found"}), 400

    if record["otp"] != otp:
        return jsonify({"error": "Invalid OTP"}), 400

    if datetime.now() > record["expires_at"]:
        return jsonify({"error": "OTP expired"}), 400

    return jsonify({"message": "OTP verified successfully"}), 200

# Step 3: Reset Password
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Email not registered"}), 404

    # Hash password before saving (important!)
    user.password = bcrypt.generate_password_hash(new_password).decode("utf-8")

    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200