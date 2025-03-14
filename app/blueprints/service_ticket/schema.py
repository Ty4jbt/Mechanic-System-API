from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested('MechanicSchema', many=True, required=True)
    customer = fields.Nested('CustomerSchema', required=True)
    class Meta:
        model = ServiceTicket
        fields = ("mechanic_ids", "customer_id", "date_created", "desc", "VIN", "mechanics", "customer")

class EditServiceTickerSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    
    class Meta:
        fields = ("add_mechanic_ids", "remove_mechanic_ids")

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
return_service_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])
edit_service_ticket_schema = EditServiceTickerSchema()