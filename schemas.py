from marshmallow import Schema,fields

class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class ItemUpdateSchema(Schema):
    price = fields.Float()
    name = fields.Str()
    store_id = fields.Int()

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainItemSchema(),dump_only=True)#dump_only=read only = True nested is done for foreign keys
    tags = fields.Nested(PlainTagSchema(),dump_only=True)

class StoreSchema(PlainStoreSchema, PlainTagSchema):
    items = fields.List(fields.Nested(PlainStoreSchema(), dump_only=True))# deals with the relationships
    tags = fields.List(fields.Nested(PlainTagSchema(), dump_only=True))

class TagSchema(PlainTagSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainTagSchema(),dump_only=True )
    items = fields.Nested(PlainItemSchema(),dump_only=True )

class TagandItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema())
    tags = fields.Nested(TagSchema())

class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)# never sent to client you wont be able to see
    id = fields.Int(dump_only=True)# we do not expect it from the client

