from app.models import Part
from app.extensions import ma

class PartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Part

part_schema = PartSchema()
parts_schema = PartSchema(many=True)