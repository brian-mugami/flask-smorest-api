from flask.views import MethodView
from flask import jsonify
from flask_smorest import abort, Blueprint
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, create_refresh_token, get_jwt_identity

from db import db
from blocklist import blocklist
from models import UserModel
from schemas import UserSchema

blp = Blueprint("Users", __name__, description="Operation on users")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username= user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return jsonify({"refresh token": refresh_token, "access_token":access_token})

        abort(401, message="User not available")

@blp.route("/refresh")#token refresh
class Refresh(MethodView):
    @jwt_required
    def post(self):
        current_user = get_jwt_identity()#gets identity once
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access token": new_token}


@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required
    def post(self):
        jti = get_jwt()["jti"]
        blocklist.add(jti)
        return {"message" : "logout successfull"}


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter_by(username = user_data["username"]).first()
        if user:
            abort(409, message= "User already exists")

        user = UserModel(username = user_data["username"], password = pbkdf2_sha256.hash(user_data["password"]))

        db.session.add(user)
        db.session.commit()

        return {"user": "created"}, 201

@blp.route("/user/<int:id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, id):
        user = UserModel.query.get_or_404(id)
        return user

    def delete(self, id):
        user = UserModel.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()

        return {"message": "deleted successfully"}




