from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Inventory, db
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventory_items_schema, inventory_detail_schema

@inventory_bp.route('/', methods=['POST'])
def create_inventory_item():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_item = Inventory(
        name=inventory_data['name'],
        price=inventory_data['price'],
        quantity_in_stock=inventory_data.get('quantity_in_stock', 0),
    )

    db.session.add(new_item)
    db.session.commit()

    return inventory_schema.jsonify(new_item), 201

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    query = select(Inventory)
    result = db.session.execute(query).scalars().all()
    return inventory_items_schema.jsonify(result), 200

@inventory_bp.route('/<int:inventory_id>', methods=['GET'])
def get_inventory_item(inventory_id):
    query = select(Inventory).where(Inventory.id == inventory_id)
    item = db.session.execute(query).scalars().first()

    if item is None:
        return jsonify({'message': 'Inventory item not found'})
    
    return inventory_detail_schema.jsonify(item), 200

@inventory_bp.route('/<int:inventory_id>', methods=['PUT'])
def update_inventory_item(inventory_id):
    query = select(Inventory).where(Inventory.id == inventory_id)
    item = db.session.execute(query).scalars().first()

    if item is None:
        return jsonify({'message': 'Inventory item not found'})
    
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in inventory_data.items():
        setattr(item, field, value)

    db.session.commit()
    return inventory_schema.jsonify(item), 200

@inventory_bp.route('/<int:inventory_id>', methods=['DELETE'])
def delete_inventory_item(inventory_id):
    query = select(Inventory).where(Inventory.id == inventory_id)
    item = db.session.execute(query).scalars().first()

    if item is None:
        return jsonify({'message': 'Inventory item not found'})

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': f'successfully deleted inventory item {inventory_id}'}), 200

@inventory_bp.route('/popular', methods=['GET'])
def get_popular_inventory():
    query = select(Inventory)
    items = db.session.execute(query).scalars().all()

    items.sort(key=lambda item: len(item.service_tickets), reverse=True)

    return inventory_items_schema.jsonify(items), 200

@inventory_bp.route('/search', methods=['GET'])
def search_inventory():
    name = request.args.get('name')

    query = select(Inventory).where(Inventory.name.like(f'%{name}%'))
    items = db.session.execute(query).scalars().all()

    return inventory_items_schema.jsonify(items), 200

@inventory_bp.route('/low-stock', methods=['GET'])
def get_low_stock():
    threshold = request.args.get('threshold', 5, type=int)

    query = select(Inventory).where(Inventory.quantity_in_stock < threshold)
    items = db.session.execute(query).scalars().all()

    return inventory_items_schema.jsonify(items), 200