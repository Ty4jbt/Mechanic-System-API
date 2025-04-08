from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import ServiceTicket, db, Mechanic, Part, ServicePartQuantity
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.service_ticket.schema import service_ticket_schema, service_tickets_schema, return_service_ticket_schema, edit_service_ticket_schema, add_part_schema, message_response_schema
from app.blueprints.parts.schemas import parts_schema
from app.utils.util import customer_token_required

@service_ticket_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
        print(service_ticket_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_service_ticket = ServiceTicket(
        date_created=service_ticket_data['date_created'],
        desc=service_ticket_data['desc'],
        VIN=service_ticket_data['VIN'],
        customer_id=service_ticket_data['customer_id']
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

@service_ticket_bp.route('/<int:service_ticket_id>/parts', methods=['POST'])
def add_part_to_ticket(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return jsonify({'message': 'Service ticket not found'}), 404
    
    try:
        part_data = add_part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if len(part_data['part_ids']) != len(part_data['quantities']):
        return message_response_schema.jsonify({
            'message': 'Part IDs and quantities must match in length'
        }), 400
    
    added_parts = []

    for i, part_id in enumerate(part_data['part_ids']):
        quantity = part_data['quantities'][i]

        part_query = select(Part).where(Part.id == part_id)
        part = db.session.execute(part_query).scalars().first()

        if part is None:
            return jsonify({'message': 'Part not found'}), 404

        if part not in service_ticket.parts:
            service_ticket.parts.append(part)

        quantity_query = select(ServicePartQuantity).where(
            (ServicePartQuantity.service_ticket_id == service_ticket_id) & 
            (ServicePartQuantity.part_id == part_id)
        )

        existing_quantity = db.session.execute(quantity_query).scalars().first()

        if existing_quantity:
            existing_quantity.quantity = quantity
        else:
            new_quantity = ServicePartQuantity(
                service_ticket_id=service_ticket_id,
                part_id=part.id,
                quantity=quantity
            )
            db.session.add(new_quantity)

        added_parts.append({
            'part_id': part.id,
            'quantity': quantity
        })

    db.session.commit()

    response_data = {
        'message': f'Successfully added {len(added_parts)} parts to service ticket {service_ticket_id}',
        'service_ticket_id': service_ticket_id
    }

    return message_response_schema.jsonify(response_data), 201

@service_ticket_bp.route('/<int:service_ticket_id>/parts', methods=['GET'])
def get_ticket_parts(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return jsonify({'message': 'Service ticket not found'}), 404

    parts = service_ticket.parts

    quantity_query = select(ServicePartQuantity).where(
        ServicePartQuantity.service_ticket_id == service_ticket_id
    )

    quantity_relations = db.session.execute(quantity_query).scalars().all()

    parts_quant = []

    for relation in quantity_relations:
        part_query = select(Part).where(Part.id == relation.part_id)
        part = db.session.execute(part_query).scalars().first()

        if part:
            part_data = {
                'id': part.id,
                'part_name': part.part_name,
                'price': part.price,
                'quantity': relation.quantity
            }
            parts_quant.append(part_data)

    return jsonify({
        'parts': parts_schema.dump(parts),
        'parts_quant': parts_quant
    }), 200

@service_ticket_bp.route('/<int:service_ticket_id>/parts/<int:part_id>', methods=['DELETE'])
def remove_part_from_ticket(service_ticket_id, part_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return message_response_schema.jsonify({'message': 'Service ticket not found'}), 400

    part_query = select(Part).where(Part.id == part_id)
    part = db.session.execute(part_query).scalars().first()

    if part is None:
        return message_response_schema.jsonify({'message': 'Part not found'}), 400

    if part in service_ticket.parts:
        service_ticket.parts.remove(part)

    quantity_query = select(ServicePartQuantity).where(
        (ServicePartQuantity.service_ticket_id == service_ticket_id) &
        (ServicePartQuantity.part_id == part_id)
    )

    existing_quantity = db.session.execute(quantity_query).scalars().first()

    if existing_quantity:
        db.session.delete(existing_quantity)

    db.session.commit()

    response_data = {
        'message': f'Successfully removed part {part_id} from service ticket {service_ticket_id}',
        'part_id': part_id,
        'service_ticket_id': service_ticket_id
    }

    return message_response_schema.jsonify(response_data), 200

