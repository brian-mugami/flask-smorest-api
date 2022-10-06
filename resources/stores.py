from flask.views import MethodView
from flask_smorest import Blueprint,abort

from db import db
from sqlalchemy.exc import SQLAlchemyError
from schemas import StoreSchema
from models import StoreModel
blp = Blueprint("stores", __name__, description="Operation on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @blp.response(200, StoreSchema)# response sorted in json
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @blp.response(200, StoreSchema)
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {store: "deleted"}

@blp.route("/store")
class StoreList(MethodView):

    @blp.response(200, StoreSchema)
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
       # if "name" not in store_data:
        #    abort(400, message="Ensure name is in json payload")  no need for this validator as schema sorts us out
       store = StoreModel(**store_data)
       try:
           db.session.add(store)
           db.session.commit()
       except SQLAlchemyError:
           abort(500, message="An error occured when saving store to db")
       return store

