from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import ServiceTicket, db, Mechanic, Inventory, ServiceInventoryQuantity
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.service_ticket.schema import service_ticket_schema, service_tickets_schema, return_service_ticket_schema, edit_service_ticket_schema, add_inventory_schema, message_response_schema, receipt_schema
from app.blueprints.inventory.schemas import inventory_items_schema
from app.utils.util import customer_token_required

@service_ticket_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_service_ticket = ServiceTicket(
        date_created=service_ticket_data['date_created'],
        desc=service_ticket_data['desc'],
        VIN=service_ticket_data['VIN'],
        customer_id=service_ticket_data['customer_id'],
        total_cost=0.0
    )
    
    for mechanic_id in service_ticket_data['mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalar()
        if mechanic:
            new_service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({'message': 'Mechanic not found'})
        
    db.session.add(new_service_ticket)
    db.session.commit()

    return return_service_ticket_schema.jsonify(new_service_ticket), 201

@service_ticket_bp.route('/', methods=['GET'])
def get_service_tickets():
    query = select(ServiceTicket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

@service_ticket_bp.route('/<int:service_ticket_id>', methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return jsonify({'message': 'Service ticket not found'}), 400
    
    db.session.delete(service_ticket)
    db.session.commit()

    return jsonify({'message': f'Succesfully deleted service ticket {service_ticket_id}'}), 200

@service_ticket_bp.route('/my-tickets', methods=['GET'])
@customer_token_required
def get_my_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

@service_ticket_bp.route('/<int:service_ticket_id>', methods=['PUT'])
def edit_service_ticket(service_ticket_id):
    try:
        service_ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    for mechanic_id in service_ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    for mechanic_id in service_ticket_edits['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()
    return return_service_ticket_schema.jsonify(service_ticket), 200

@service_ticket_bp.route('/<int:service_ticket_id>/inventory', methods=['POST'])
def add_inventory_to_ticket(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return jsonify({'message': 'Service ticket not found'}), 404
    
    try:
        inventory_data = add_inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if len(inventory_data['inventory_ids']) != len(inventory_data['quantities']):
        return message_response_schema.jsonify({
            'message': 'Part IDs and quantities must match in length'
        }), 400
    
    added_items = []
    total_cost = 0.0

    for i, inventory_id in enumerate(inventory_data['inventory_ids']):
        quantity = inventory_data['quantities'][i]

        inventory_query = select(Inventory).where(Inventory.id == inventory_id)
        item = db.session.execute(inventory_query).scalars().first()

        if item is None:
            return jsonify({'message': f'Inventory item with ID {inventory_id} not found'}), 404
        
        if item.quantity_in_stock < quantity:
            return jsonify({'message': f'Not enough stock for item {item.name}. Available: {item.quantity_in_stock}, Requested: {quantity}'}), 400

        if item not in service_ticket.inventory_items:
            service_ticket.inventory_items.append(item)

        quantity_query = select(ServiceInventoryQuantity).where(
            (ServiceInventoryQuantity.service_ticket_id == service_ticket_id) & 
            (ServiceInventoryQuantity.inventory_id == inventory_id)
        )

        existing_quantity = db.session.execute(quantity_query).scalars().first()

        if existing_quantity:
            existing_quantity.quantity = quantity
        else:
            new_quantity = ServiceInventoryQuantity(
                service_ticket_id=service_ticket_id,
                inventory_id=item.id,
                quantity=quantity
            )
            db.session.add(new_quantity)

        item.quantity_in_stock -= quantity

        item_cost = item.price * quantity
        total_cost += item_cost

        added_items.append({
            'inventory_id': item.id,
            'name': item.name,
            'quantity': quantity,
            'unit_price': item.price,
            'total_price': item_cost
        })

    service_ticket.total_cost = (service_ticket.total_cost or 0) + total_cost

    db.session.commit()

    receipt_data = {
        'total_cost': total_cost,
        'service_ticket': service_ticket,
        'items': added_items
    }

    return receipt_schema.jsonify(receipt_data), 201

@service_ticket_bp.route('/<int:service_ticket_id>/inventory', methods=['GET'])
def get_ticket_inventory(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return jsonify({'message': 'Service ticket not found'}), 404

    items = service_ticket.inventory_items

    quantity_query = select(ServiceInventoryQuantity).where(
        ServiceInventoryQuantity.service_ticket_id == service_ticket_id
    )

    quantity_relations = db.session.execute(quantity_query).scalars().all()

    items_with_quantity = []

    for relation in quantity_relations:
        inventory_query = select(Inventory).where(Inventory.id == relation.inventory_id)
        item = db.session.execute(inventory_query).scalars().first()

        if item:
            item_data = {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': relation.quantity,
                'total_price': item.price * relation.quantity
            }
            items_with_quantity.append(item_data)

    return jsonify({
        'items': inventory_items_schema.dump(items),
        'items_with_quantity': items_with_quantity,
        'total_cost': service_ticket.total_cost
    }), 200

@service_ticket_bp.route('/<int:service_ticket_id>/inventory/<int:inventory_id>', methods=['DELETE'])
def remove_inventory_from_ticket(service_ticket_id, inventory_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return message_response_schema.jsonify({'message': 'Service ticket not found'}), 400

    inventory_query = select(Inventory).where(Inventory.id == inventory_id)
    item = db.session.execute(inventory_query).scalars().first()

    if item is None:
        return message_response_schema.jsonify({'message': 'Inventory item not found'}), 400

    quantity_query = select(ServiceInventoryQuantity).where(
        (ServiceInventoryQuantity.service_ticket_id == service_ticket_id) &
        (ServiceInventoryQuantity.inventory_id == inventory_id)
    )

    existing_quantity = db.session.execute(quantity_query).scalars().first()

    if existing_quantity:
        quantity = existing_quantity.quantity

        item.quantity_in_stock += quantity

        item_cost = item.price * quantity
        service_ticket.total_cost -= item_cost

        db.session.delete(existing_quantity)

        if item in service_ticket.inventory_items:
            service_ticket.inventory_items.remove(item)

        db.session.commit()

        response_data = {
            'message': f'Successfully removed {item.name} from service ticket {service_ticket_id}',
            'inventory_id': item.id,
            'service_ticket_id': service_ticket.id,
            'quantity': quantity
        }

        return message_response_schema.jsonify(response_data), 200
    else:
        return message_response_schema.jsonify({'message': 'Inventory item not found in service ticket'}), 400

@service_ticket_bp.route('/<int:service_ticket_id>/receipt', methods=['GET'])
def get_service_ticket_receipt(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return jsonify({'message': 'Service ticket not found'}), 404
    
    quantity_query = select(ServiceInventoryQuantity).where(
        ServiceInventoryQuantity.service_ticket_id == service_ticket_id
    )
    quantity_relations = db.session.execute(quantity_query).scalars().all()

    items = []
    total_cost = 0.0

    for relation in quantity_relations:
        inventory_query = select(Inventory).where(Inventory.id == relation.inventory_id)
        item = db.session.execute(inventory_query).scalars().first()

        if item:
            item_cost = item.price * relation.quantity
            total_cost += item_cost

            items.append({
                'id': item.id,
                'name': item.name,
                'unit_price': item.price,
                'quantity': relation.quantity,
                'total_price': item_cost
            })

    if service_ticket.total_cost != total_cost:
        service_ticket.total_cost = total_cost
        db.session.commit()

    receipt_data = {
        'total_cost': total_cost,
        'service_ticket': service_ticket,
        'items': items
    }

    return receipt_schema.jsonify(receipt_data), 200