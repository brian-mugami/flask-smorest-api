from flask_jwt_extended import jwt_required, get_jwt# uses bearer instead of JWT in authorization headers
from flask.views import MethodView
from flask_smorest import Blueprint,abort
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("items", __name__, description="Operation on stores")

@blp.route("/item/<string:item_id>")
class Item(MethodView):

    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required(fresh=True)
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin only can delete") #from app.py jwt additional loader
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "deleted successfully"}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self,item_data, item_id):
        #item_data = request.get_json() when we use schemas an extra argument is added same to request.json and it goes infront of all other args exceptself
        item = ItemModel.query.get(item_id)
        #raise NotImplementedError("Put request not updated")
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()
        return item

@blp.route("/item")
class ItemList(MethodView):

    @jwt_required
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):  #no need for validators as schema sorts us out
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured when saving item to db")

        return {"item": "created"}

    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()