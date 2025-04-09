from app.models import Inventory
from app.extensions import ma
from marshmallow import fields

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_all = True

class InventoryDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        include_all = True

    service_tickets = fields.Nested('ServiceTicketSchema', many=True, exclude=['id', 'inventory_items'])

inventory_schema = InventorySchema()
inventory_items_schema = InventorySchema(many=True)
inventory_detail_schema = InventoryDetailSchema()