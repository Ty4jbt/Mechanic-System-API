from flask import Blueprint

service_ticket_bp = Blueprint('service_tickets', __name__)

from . import routes