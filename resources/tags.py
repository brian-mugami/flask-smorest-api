from flask.views import MethodView
from flask_smorest import abort,Blueprint
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import TagModel,StoreModel, ItemModel
from schemas import TagSchema, TagandItemSchema

blp = Blueprint("tags", __name__, description="Operation on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all() #works due to lazy = dynamics in relationship

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self,tag_data, store_id):
        #if TagModel.query.filter_by(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            #abort(400, message= "A tag with that name already exists in that store")

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message = str(e))

@blp.route("/tag/<string:id>")
class TagName(MethodView):

    @blp.response(200, TagSchema)
    def get(self, id):
        tag = TagModel.query.get(id)
        return tag

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagToItem(MethodView):
    blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="Error occured while adding the tag")

        return tag

    @blp.response(200, TagandItemSchema)
    def delete(self, tag_id, item_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="Error occured while removing the tag")

        return {tag: "removed"}

@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(202, description="Deletes a tag if no item is attached to it", example={"message":"Tag deleted"})
    @blp.alt_response(404, description="Tag not found")
    @blp.alt_response(400, description="Returned if tag is assigned to one or more items")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message: tag deleted"}

        abort(400, message="Error outside the code")


