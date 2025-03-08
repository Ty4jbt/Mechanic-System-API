from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Mechanic, db
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema

@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_mechanic = Mechanic(
        name=mechanic_data['name'],
        email=mechanic_data['email'],
        phone=mechanic_data['phone'],
        salary=mechanic_data['salary']
    )

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result), 200

@mechanics_bp.route('//<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic is None:
        return jsonify({'message': 'Mechanic not found'})
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route('//<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic is None:
        return jsonify({'message': 'Mechanic not found'})

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'successfully deleted mechanic {mechanic_id}'}), 200