from flask import Blueprint

parts_bp = Blueprint('parts', __name__)

from . import routes