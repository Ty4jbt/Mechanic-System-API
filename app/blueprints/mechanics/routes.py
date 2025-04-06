from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Mechanic, db
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, login_schema
from app.extensions import cache
from app.utils.util import mechanic_token_required, encode_mechanic_token

@mechanics_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic and mechanic.password == password:
        token = encode_mechanic_token(mechanic.id)

        response = {
            "status": "success",
            "message": "Successfully logged in",
            "token": token
        }

        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 400

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
        password=mechanic_data['password'],
        salary=mechanic_data['salary']
    )

    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result), 200

@mechanics_bp.route('/', methods=['PUT'])
@mechanic_token_required
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

@mechanics_bp.route('/', methods=['DELETE'])
@mechanic_token_required
def delete_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()

    if mechanic is None:
        return jsonify({'message': 'Mechanic not found'})

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'successfully deleted mechanic {mechanic_id}'}), 200

@mechanics_bp.route('/popular', methods=['GET'])
def get_popular_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)

    return mechanics_schema.jsonify(mechanics), 200

@mechanics_bp.route('/search', methods=['GET'])
def search_mechanic():
    name = request.args.get('name')

    query = select(Mechanic).where(Mechanic.name.like(f'%{name}%'))
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics), 200