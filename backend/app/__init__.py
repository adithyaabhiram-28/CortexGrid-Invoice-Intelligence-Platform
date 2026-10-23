import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.extensions import db, make_celery
from app.routes.auth import auth_bp
from app.routes.vendors import vendors_bp
from app.routes.invoices import invoices_bp
from app.routes.purchase_orders import purchase_orders_bp
from app.utils.db_migrate import ensure_schema_updates

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(purchase_orders_bp)

    # Register error handlers
    @app.errorhandler(400)
    def bad_request_error(e):
        return jsonify({'error': 'Bad Request', 'message': str(e.description if hasattr(e, 'description') else str(e))}), 400

    @app.errorhandler(404)
    def not_found_error(e):
        return jsonify({'error': 'Resource Not Found'}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'error': 'Internal Server Error'}), 500

    # Auto-create tables and safely apply column updates in development mode
    with app.app_context():
        try:
            db.create_all()
            ensure_schema_updates(app)
        except Exception as err:
            app.logger.warning(f"Database initialization warning: {str(err)}")

    return app

celery = make_celery()
