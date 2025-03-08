from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested('MechanicSchema', many=True)
    customer = fields.Nested('CustomerSchema')
    class Meta:
        model = ServiceTicket
        fields = ("mechanic_ids", "customer_id", "date_created", "desc", "VIN", "mechanics", "customer")

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
return_service_ticket_schema = ServiceTicketSchema(exclude=["customer_id"])