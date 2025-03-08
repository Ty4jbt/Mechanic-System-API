from flask import Flask
from .models import db
from .extensions import ma
from .blueprints.customers import customers_bp
from .blueprints.mechanics import mechanics_bp

def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    # Add extensions
    db.init_app(app)
    ma.init_app(app)

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')

    return app