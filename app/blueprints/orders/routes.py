from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Order, OrderParts, db
from app.blueprints.orders import orders_bp
from app.blueprints.orders.schemas import order_schema, orders_schema, create_order_schema, receipt_schema
from datetime import date

@orders_bp.route('/', methods=['POST'])
def create_order():
    try:
        order_data = create_order_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Order(
        mechanic_id=order_data['mechanic_id'],
        order_date = date.today(),
    )

    db.session.add(new_order)
    db.session.commit()

    for part in order_data['part_quant']:
        order_part = OrderParts(
            order_id = new_order.id,
            part_id = part['part_id'],
            quantity = part['part_quant']
        )

        db.session.add(order_part)

    db.session.commit()

    total = 0

    for order_part in new_order.order_parts:
        price = order_part.part.price * order_part.quantity

        total += price

    receipt = {
        'total': total,
        'order': new_order
    }

    return receipt_schema.jsonify(receipt), 201
    
