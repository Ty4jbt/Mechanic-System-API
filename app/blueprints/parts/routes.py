from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Part, db
from app.blueprints.parts import parts_bp
from app.blueprints.parts.schemas import part_schema, parts_schema

@parts_bp.route('/', methods=['POST'])
def create_part():
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_part = Part(
        part_name=part_data['part_name'],
        price=part_data['price']
    )

    db.session.add(new_part)
    db.session.commit()

    return part_schema.jsonify(new_part), 201

@parts_bp.route('/', methods=['GET'])
def get_parts():
    query = select(Part)
    result = db.session.execute(query).scalars().all()
    return parts_schema.jsonify(result), 200

@parts_bp.route('/<int:part_id>', methods=['PUT'])
def update_part(part_id):
    query = select(Part).where(Part.id == part_id)
    part = db.session.execute(query).scalars().first()

    if part is None:
        return jsonify({'message': 'part not found'})
    
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in part_data.items():
        setattr(part, field, value)

    db.session.commit()
    return part_schema.jsonify(part), 200

@parts_bp.route('/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    query = select(Part).where(Part.id == part_id)
    part = db.session.execute(query).scalars().first()

    if part is None:
        return jsonify({'message': 'part not found'})

    db.session.delete(part)
    db.session.commit()
    return jsonify({'message': f'successfully deleted part {part_id}'}), 200

@parts_bp.route('/popular', methods=['GET'])
def get_popular_parts():
    query = select(Part)
    parts = db.session.execute(query).scalars().all()

    parts.sort(key=lambda part: len(part.service_tickets), reverse=True)

    return parts_schema.jsonify(parts), 200

@parts_bp.route('/search', methods=['GET'])
def search_part():
    name = request.args.get('name')

    query = select(Part).where(Part.name.like(f'%{name}%'))
    parts = db.session.execute(query).scalars().all()

    return parts_schema.jsonify(parts), 200