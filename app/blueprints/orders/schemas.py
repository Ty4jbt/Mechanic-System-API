from app.models import Order, OrderItems
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
            order_items: [
                {
                    inventory_item: {part_name: "Tire", price: 199.99},
                    quantity: 4,
                },
                {
                    inventory_item: {part_name: "Rim", price: 499.99},
                    quantity: 4,
                }
            ]
        }
    }
    '''
    total_cost = fields.Float(required=True)
    order = fields.Nested('OrderSchema')


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_relationships = True

    order_items = fields.Nested('OrderItemSchema', many=True, exclude=['id'])

class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItems

    inventory_item = fields.Nested('InventorySchema', exclude=['id'])

class CreateOrderSchema(ma.Schema):
    '''
    {
        "mechanic_id": 1,
        "inventory_items": [
            {
                "inventory_id": 1,
                "quantity": 2
            },
            {
                "inventory_id": 2,
                "quantity": 3
            }
        ]
    }
    '''

    mechanic_id = fields.Int(required=True)
    inventory_items = fields.Nested('InventoryQuantSchema', many=True, required=True)

class InventoryQuantSchema(ma.Schema):
    inventory_id = fields.Int(required=True)
    quantity = fields.Int(required=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
create_order_schema = CreateOrderSchema()
receipt_schema = ReceiptSchema()