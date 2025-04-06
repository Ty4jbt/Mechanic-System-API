from app.models import Order, OrderParts
from app.extensions import ma
from marshmallow import fields

class ReceiptSchema(ma.Schema):
    '''
    {
        "total" : 2799.88,
        "order" : {
            order_id: 1,
            mechanic_id: 1,
            order_date: "2023-10-01",
            order_parts: [
                {
                    part: {part_name: "Tire", price: 199.99},
                    quantity: 4,
                },
                {
                    part: {part_name: "Rim", price: 499.99},
                    quantity: 2,
                }
            ]
        }
    }
    '''
    total = fields.Float(required=True)
    order = fields.Nested('OrderSchema')


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_relationships = True

    order_parts = fields.Nested('OrderPartSchema', many=True, exclude=['id'])

class OrderPartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderParts

    part = fields.Nested('PartSchema', exclude=['id'])

class CreateOrderSchema(ma.Schema):
    '''
    {
        "mechanic_id": 1,
        "part_quant": [
            {
                "part_id": 1,
                "part_quant": 2
            },
            {
                "part_id": 2,
                "part_quant": 3
            }
        ]
    }
    '''

    mechanic_id = fields.Int(required=True)
    part_quant = fields.Nested('PartQuantSchema', many=True, required=True)

class PartQuantSchema(ma.Schema):
    part_id = fields.Int(required=True)
    part_quant = fields.Int(required=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
create_order_schema = CreateOrderSchema()
receipt_schema = ReceiptSchema()