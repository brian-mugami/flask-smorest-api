import os  # order of imporattion is crucial
import secrets

from flask_smorest import Api
from flask_migrate import Migrate
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from db import db
from blocklist import blocklist

from resources.stores import blp as StoreBlueprint
from resources.item import blp as ItemBlueprint
from resources.tags import blp as TagBluePrint
from resources.user import blp as UserBlueprint

# docker build -t {appname} .(showing same dir)
# docker run -dp 5005:5000 rest-apis-flask--runs in the background
# docker run -dp 5005:6000 -w/app -v "$(pwd):/app"flask-smorest-api

jwt = JWTManager()


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config[
        "OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"  # for documentation purposes..http://localhost:7005{port no}/swagger-ui
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///api.db")  # either or
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(16)

    db.init_app(app)
    migrate = Migrate(app,db)
    import models
    #with app.app_context():
      #db.create_all()

    api = Api(app)
    jwt.init_app(app)
    @jwt.token_in_blocklist_loader#aids in loging out
    def check_if_jwt_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in blocklist

    @jwt.revoked_token_loader
    def revocked_token_callback(jwt_header, jwt_payload):
        return jsonify(
            {"error": "Token revoked"}
        ), 401


    #those that take an error lack the jwt
    @jwt.additional_claims_loader
    def additons_to_jwt(identity):#user.id
        if identity == 1:
            return jsonify({"is admin": "true"})
        else:
            return jsonify({"is admin": "False"})

    @jwt.invalid_token_loader
    def invalid_token_loader(error):
        return (
            jsonify(
                {"message": "signature verification failed", "error": "invalid token"}
            ), 401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {"Desc": "Request lack token", "error": "auth_required"}
            ), 401
        )
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "signature verification failed", "error": "token expired"}), 401
        )
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBlueprint)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(port=8000, debug=True)