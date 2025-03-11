from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import ServiceTicket, db, Mechanic
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.service_ticket.schema import service_ticket_schema, service_tickets_schema, return_service_ticket_schema
from app.utils.util import token_required

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
@token_required
def get_my_tickets(customer_id):
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

# @service_ticket_bp.route('/<int:service_ticket_id>', methods=['PUT'])
# def update_service_ticket(service_ticket_id):
#     query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
#     service_ticket = db.session.execute(query).scalars().first()
    
#     if not service_ticket:
#         return jsonify({'message': 'Service ticket not found'}), 404
    
#     try:
#         service_ticket_data = service_ticket_schema.load(request.json)
#     except ValidationError as e:
#         return jsonify(e.messages), 400
    
#     service_ticket.date_created = service_ticket_data['date_created']
#     service_ticket.desc = service_ticket_data['desc']
#     service_ticket.VIN = service_ticket_data['VIN']
#     service_ticket.customer_id = service_ticket_data['customer_id']

#     for mechanic_id in service_ticket_data['mechanic_ids']:
#         query = select(Mechanic).where(Mechanic.id == mechanic_id)
#         mechanic = db.session.execute(query).scalar()
#         if mechanic:
#             service_ticket.mechanics.append(mechanic)
#         else:
#             return jsonify({'message': 'Mechanic not found'})
    
#     db.session.commit()

#     return return_service_ticket_schema.jsonify(service_ticket), 200