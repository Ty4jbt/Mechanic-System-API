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
    class Meta:
        model = ServiceTicket
        fields = ("id", "date_created", "desc", "VIN", "mechanics", "customer")

class EditServiceTickerSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")

class AddPartSchema(ma.Schema):
    part_ids = fields.List(fields.Int(), required=True)
    quantity = fields.Int(required=True)
    class Meta:
        fields = ("part_ids", "quantity")

class MessageResponseSchema(ma.Schema):
    message = fields.String(required=True)

    part_id = fields.Int()
    service_ticket_id = fields.Int()
    quantity = fields.Int()

    class Meta:
        fields = ("message", "part_id", "service_ticket_id", "quantity")
    
service_ticket_schema = CreateServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
return_service_ticket_schema = ServiceTicketSchema()
edit_service_ticket_schema = EditServiceTickerSchema()
add_part_schema = AddPartSchema()
message_response_schema = MessageResponseSchema()