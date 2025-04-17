from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

class CreateServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics_ids = fields.List(fields.Int(), required=True)
    customer_id = fields.Int(required=True)

    class Meta:
        model = ServiceTicket
        fields = ("mechanic_ids", "customer_id", "date_created", "desc", "VIN")

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested('MechanicSchema', many=True, required=True)
    customer = fields.Nested('CustomerSchema', required=True)
    inventory_items = fields.Nested('InventorySchema', many=True)
    class Meta:
        model = ServiceTicket
        fields = ("id", "date_created", "desc", "VIN", "mechanics", "customer", "inventory_items", "total_cost")

class EditServiceTickerSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")

class AddInventorySchema(ma.Schema):
    inventory_ids = fields.List(fields.Int(), required=True)
    quantities = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ("inventory_ids", "quantities")

class ReceiptSchema(ma.Schema):
    total_cost = fields.Float(required=True)
    service_ticket = fields.Nested('ServiceTicketSchema')
    items = fields.List(fields.Dict())

    class Meta:
        fields = ("total_cost", "service_ticket", "items")

class MessageResponseSchema(ma.Schema):
    message = fields.String(required=True)

    inventory_id = fields.Int()
    service_ticket_id = fields.Int()
    quantity = fields.Int()

    class Meta:
        fields = ("message", "inventory_id", "service_ticket_id", "quantity")
    
service_ticket_schema = CreateServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
return_service_ticket_schema = ServiceTicketSchema()
edit_service_ticket_schema = EditServiceTickerSchema()
add_inventory_schema = AddInventorySchema()
message_response_schema = MessageResponseSchema()
receipt_schema = ReceiptSchema()