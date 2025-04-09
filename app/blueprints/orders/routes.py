from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Order, OrderItems, Inventory, db
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
        total_cost = 0.0
    )

    db.session.add(new_order)
    db.session.commit()

    total_cost = 0.0
    order_items = []

    for item_data in order_data['inventory_items']:
        inventory_id = item_data['inventory_id']
        quantity = item_data['quantity']

        inventory_query = select(Inventory).where(Inventory.id == inventory_id)
        inventory_item = db.session.execute(inventory_query).scalars().first()

        if not inventory_item:
            db.session.delete(new_order)
            db.session.commit()
            return jsonify({'message': 'Inventory item with ID not found'}), 404
        
        order_item = OrderItems(
            order_id=new_order.id,
            inventory_id=inventory_id,
            quantity=quantity
        )

        inventory_item.quantity_in_stock += quantity

        item_cost = inventory_item.price * quantity
        total_cost += item_cost

        db.session.add(order_item)

        order_items.append({
            'inventory_id': inventory_id,
            'name': inventory_item.name,
            'quantity': quantity,
            'unit_price': inventory_item.price,
            'total_price': item_cost
        })

    new_order.total_cost = total_cost
    db.session.commit()

    receipt = {
        'total_cost': total_cost,
        'order': new_order
    }

    return receipt_schema.jsonify(receipt), 201

@orders_bp.route('/', methods=['GET'])
def get_orders():
    query = select(Order)
    result = db.session.execute(query).scalars().all()
    return orders_schema.jsonify(result), 200
    
@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    query = select(Order).where(Order.id == order_id)
    order = db.session.execute(query).scalars().first()

    if order is None:
        return jsonify({'message': 'Order not found'}), 404

    return order_schema.jsonify(order), 200

@orders_bp.route('/<int:order_id>/receipt', methods=['GET'])
def get_order_receipt(order_id):
    query = select(Order).where(Order.id == order_id)
    order = db.session.execute(query).scalars().first()

    if order is None:
        return jsonify({'message': 'Order not found'}), 404

    item_query = select(OrderItems).where(OrderItems.order_id == order_id)
    order_items = db.session.execute(item_query).scalars().all()

    items = []
    total_cost = 0.0

    for order_item in order_items:
        inventory_query = select(Inventory).where(Inventory.id == order_item.inventory_id)
        inventory_item = db.session.execute(inventory_query).scalars().first()

        if inventory_item:
            item_cost = inventory_item.price * order_item.quantity
            total_cost += item_cost

            items.append({
                'id': inventory_item.id,
                'name': inventory_item.name,
                'quantity': order_item.quantity,
                'unit_price': inventory_item.price,
                'total_price': item_cost
            })
    
    if order.total_cost != total_cost:
        order.total_cost = total_cost
        db.session.commit()

    receipt_data = {
        'total_cost': total_cost,
        'order': order,
        'items': items
    }

    return receipt_schema.jsonify(receipt_data), 200